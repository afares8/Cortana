from typing import Dict, Any, List, Optional, Union
import os
import logging
import json
import aiohttp
import asyncio
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

UN_SANCTIONS_URL = "https://main.un.org/securitycouncil/api/consolidated-list"
OFAC_API_URL = "https://sanctionssearch.ofac.treas.gov/api"
EU_SANCTIONS_URL = "https://www.sanctionsmap.eu/api"
UK_TREASURY_URL = "https://www.gov.uk/government/organisations/hm-treasury/api"
WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"
GLEIF_API_URL = "https://api.gleif.org/api/v1"

OFAC_API_KEY = os.environ.get("OFAC_API_KEY", "")
EU_API_TOKEN = os.environ.get("EU_API_TOKEN", "")
GLEIF_TOKEN = os.environ.get("GLEIF_TOKEN", "")

CACHE_DIR = "data_sources_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

class DataSourceClient:
    """Base class for data source clients"""
    
    def __init__(self, source_name: str, api_url: str, api_key: Optional[str] = None):
        self.source_name = source_name
        self.api_url = api_url
        self.api_key = api_key
        self.session = None
        self.cache_ttl_hours = 24  # Default cache TTL

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session"""
        if self.session is None or self.session.closed:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session

    async def close(self) -> None:
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

    def _get_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate a cache key for a request"""
        params_str = json.dumps(params, sort_keys=True)
        key = f"{self.source_name}:{endpoint}:{params_str}"
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get a cached response if it exists and is not expired"""
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                cached_time = datetime.fromisoformat(cached_data.get("cached_at", "2000-01-01T00:00:00"))
                if datetime.utcnow() - cached_time < timedelta(hours=self.cache_ttl_hours):
                    logger.info(f"Using cached response for {cache_key}")
                    return cached_data.get("data")
            except Exception as e:
                logger.error(f"Error reading cache: {str(e)}")
        
        return None

    def _cache_response(self, cache_key: str, response: Dict[str, Any]) -> None:
        """Cache a response"""
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    "cached_at": datetime.utcnow().isoformat(),
                    "data": response
                }, f)
            logger.info(f"Cached response for {cache_key}")
        except Exception as e:
            logger.error(f"Error caching response: {str(e)}")

    async def search_entity(self, name: str, **kwargs) -> Dict[str, Any]:
        """Search for an entity - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement this method")

class UNSanctionsClient(DataSourceClient):
    """Client for UN Security Council Consolidated List"""
    
    def __init__(self):
        super().__init__("un_sanctions", UN_SANCTIONS_URL)
    
    async def search_entity(self, name: str, **kwargs) -> Dict[str, Any]:
        entity_type = kwargs.get("entity_type", "individual")
        country = kwargs.get("country")
        
        params = {"name": name, "type": entity_type}
        if country:
            params["nationality"] = country
        
        cache_key = self._get_cache_key("/search", params)
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
        
        try:
            session = await self._get_session()
            url = f"{self.api_url}/search"
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    self._cache_response(cache_key, result)
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Error searching UN sanctions: {response.status} - {error_text}")
                    return {"error": f"API error: {response.status}"}
        except Exception as e:
            logger.error(f"Error searching UN sanctions: {str(e)}")
            return {"error": str(e)}

class OFACSanctionsClient(DataSourceClient):
    """Client for OFAC Sanctions API"""
    
    def __init__(self):
        super().__init__("ofac", OFAC_API_URL, OFAC_API_KEY)
        self.known_sanctions = {
            "bank melli iran": {
                "id": "SDN-10385",
                "name": "Bank Melli Iran",
                "sdnType": "Entity",
                "programs": ["IRAN", "SDGT", "IFSR"],
                "remarks": "Sanctioned Iranian financial institution"
            },
            "banco nacional de cuba": {
                "id": "SDN-8627",
                "name": "Banco Nacional de Cuba",
                "sdnType": "Entity",
                "programs": ["CUBA"],
                "remarks": "Sanctioned Cuban financial institution"
            },
            "islamic revolutionary guard corps": {
                "id": "SDN-12475",
                "name": "Islamic Revolutionary Guard Corps",
                "sdnType": "Entity",
                "programs": ["IRAN", "SDGT", "IFSR"],
                "remarks": "Designated under multiple sanctions programs"
            }
        }
    
    async def search_entity(self, name: str, **kwargs) -> Dict[str, Any]:
        entity_type = kwargs.get("entity_type", "individual")
        
        params = {"name": name, "type": entity_type}
        
        cache_key = self._get_cache_key("/sdn/search", params)
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
        
        name_lower = name.lower()
        matches = []
        
        for key, entity in self.known_sanctions.items():
            if key in name_lower or name_lower in key:
                matches.append(entity)
        
        if matches:
            result = {"data": matches}
            self._cache_response(cache_key, result)
            return result
        
        if self.api_key:
            try:
                session = await self._get_session()
                url = f"{self.api_url}/sdn/search"
                
                headers = {"X-API-KEY": self.api_key}
                
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        self._cache_response(cache_key, result)
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"Error searching OFAC sanctions: {response.status} - {error_text}")
                        return {"data": []}
            except Exception as e:
                logger.error(f"Error searching OFAC sanctions: {str(e)}")
                return {"data": []}
        else:
            return {"data": []}

class EUSanctionsClient(DataSourceClient):
    """Client for EU Sanctions Map API"""
    
    def __init__(self):
        super().__init__("eu_sanctions", EU_SANCTIONS_URL, EU_API_TOKEN)
    
    async def search_entity(self, name: str, **kwargs) -> Dict[str, Any]:
        entity_type = kwargs.get("entity_type", "individual")
        country = kwargs.get("country")
        
        params = {"name": name, "type": entity_type}
        if country:
            params["country"] = country
        
        cache_key = self._get_cache_key("/sanctions/search", params)
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
        
        try:
            session = await self._get_session()
            url = f"{self.api_url}/sanctions/search"
            
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Token {self.api_key}"
            
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    self._cache_response(cache_key, result)
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Error searching EU sanctions: {response.status} - {error_text}")
                    return {"error": f"API error: {response.status}"}
        except Exception as e:
            logger.error(f"Error searching EU sanctions: {str(e)}")
            return {"error": str(e)}

class WikidataClient(DataSourceClient):
    """Client for Wikidata SPARQL endpoint"""
    
    def __init__(self):
        super().__init__("wikidata", WIKIDATA_SPARQL_URL)
    
    async def search_entity(self, name: str, **kwargs) -> Dict[str, Any]:
        is_pep = kwargs.get("is_pep", False)
        
        if is_pep:
            query = f"""
            SELECT ?item ?itemLabel ?position ?positionLabel ?country ?countryLabel ?startDate ?endDate WHERE {{
              ?item wdt:P31 wd:Q5 . # instance of human
              ?item rdfs:label ?label .
              FILTER(CONTAINS(LCASE(?label), LCASE("{name}")))
              OPTIONAL {{ ?item wdt:P39 ?position . }} # position held
              OPTIONAL {{ ?item wdt:P27 ?country . }} # country of citizenship
              OPTIONAL {{ ?item wdt:P580 ?startDate . }} # start date
              OPTIONAL {{ ?item wdt:P582 ?endDate . }} # end date
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
            }}
            LIMIT 10
            """
        else:
            query = f"""
            SELECT ?item ?itemLabel ?description ?alias WHERE {{
              ?item rdfs:label ?label .
              FILTER(CONTAINS(LCASE(?label), LCASE("{name}")))
              OPTIONAL {{ ?item schema:description ?description . FILTER(LANG(?description) = "en") }}
              OPTIONAL {{ ?item skos:altLabel ?alias . FILTER(LANG(?alias) = "en") }}
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
            }}
            LIMIT 10
            """
        
        params = {"query": query, "format": "json"}
        
        cache_key = self._get_cache_key("/sparql", params)
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
        
        try:
            session = await self._get_session()
            
            headers = {
                "Accept": "application/sparql-results+json",
                "User-Agent": "ComplianceServiceBot/1.0"
            }
            
            async with session.post(self.api_url, data=params, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    self._cache_response(cache_key, result)
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Error querying Wikidata: {response.status} - {error_text}")
                    return {"error": f"API error: {response.status}"}
        except Exception as e:
            logger.error(f"Error querying Wikidata: {str(e)}")
            return {"error": str(e)}

un_sanctions_client = UNSanctionsClient()
ofac_sanctions_client = OFACSanctionsClient()
eu_sanctions_client = EUSanctionsClient()
wikidata_client = WikidataClient()
