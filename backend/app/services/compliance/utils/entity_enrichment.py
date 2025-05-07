from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import asyncio

from app.services.compliance.utils.data_sources import wikidata_client, gleif_api_url

logger = logging.getLogger(__name__)

async def enrich_entity(entity_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich an entity with aliases, IDs, and metadata.
    
    Args:
        entity_data: Basic entity data including name and country
        
    Returns:
        Enriched entity data
    """
    name = entity_data.get("name", "")
    entity_type = entity_data.get("type", "natural")
    country = entity_data.get("country")
    dob = entity_data.get("dob")
    
    enriched_data = {
        "original": entity_data,
        "aliases": [],
        "identifiers": [],
        "metadata": {},
        "sources": [],
        "enriched_at": datetime.utcnow().isoformat()
    }
    
    if name and name not in enriched_data["aliases"]:
        enriched_data["aliases"].append(name)
    
    if country:
        enriched_data["metadata"]["country"] = country
    if dob:
        enriched_data["metadata"]["dob"] = dob.isoformat() if hasattr(dob, "isoformat") else str(dob)
    
    await _enrich_with_wikidata(name, entity_type, enriched_data)
    
    if entity_type.lower() == "legal":
        await _enrich_with_lei(name, country, enriched_data)
    
    _apply_graph_tagging(name, entity_type, enriched_data)
    
    return enriched_data

async def _enrich_with_wikidata(name: str, entity_type: str, enriched_data: Dict[str, Any]) -> None:
    """Enrich entity data with Wikidata information"""
    try:
        is_pep = entity_type.lower() == "natural"
        wikidata_result = await wikidata_client.search_entity(name, is_pep=is_pep)
        
        if "error" not in wikidata_result and "results" in wikidata_result:
            bindings = wikidata_result.get("results", {}).get("bindings", [])
            
            for binding in bindings:
                if "alias" in binding and binding["alias"].get("value"):
                    alias = binding["alias"].get("value")
                    if alias and alias not in enriched_data["aliases"]:
                        enriched_data["aliases"].append(alias)
                
                if "description" in binding and binding["description"].get("value"):
                    enriched_data["metadata"]["description"] = binding["description"].get("value")
                
                if "item" in binding and binding["item"].get("value"):
                    item_uri = binding["item"].get("value")
                    wikidata_id = item_uri.split("/")[-1]
                    
                    if not any(ident.get("type") == "wikidata" and ident.get("id") == wikidata_id 
                              for ident in enriched_data["identifiers"]):
                        enriched_data["identifiers"].append({
                            "type": "wikidata",
                            "id": wikidata_id
                        })
                
                if is_pep:
                    if "position" in binding and binding["position"].get("value"):
                        position_uri = binding["position"].get("value")
                        position_label = binding.get("positionLabel", {}).get("value", "Unknown position")
                        
                        if "positions" not in enriched_data["metadata"]:
                            enriched_data["metadata"]["positions"] = []
                        
                        position_data = {
                            "position": position_label,
                            "position_id": position_uri.split("/")[-1]
                        }
                        
                        if "startDate" in binding and binding["startDate"].get("value"):
                            position_data["start_date"] = binding["startDate"].get("value")
                        if "endDate" in binding and binding["endDate"].get("value"):
                            position_data["end_date"] = binding["endDate"].get("value")
                        
                        enriched_data["metadata"]["positions"].append(position_data)
                    
                    if "country" in binding and binding["country"].get("value"):
                        country_uri = binding["country"].get("value")
                        country_label = binding.get("countryLabel", {}).get("value", "Unknown country")
                        
                        if "countries" not in enriched_data["metadata"]:
                            enriched_data["metadata"]["countries"] = []
                        
                        country_data = {
                            "country": country_label,
                            "country_id": country_uri.split("/")[-1]
                        }
                        
                        enriched_data["metadata"]["countries"].append(country_data)
            
            if bindings:
                enriched_data["sources"].append("wikidata")
    except Exception as e:
        logger.error(f"Error enriching entity with Wikidata: {str(e)}")

async def _enrich_with_lei(name: str, country: Optional[str], enriched_data: Dict[str, Any]) -> None:
    """Enrich legal entity with Legal Entity Identifier (LEI) information"""
    try:
        logger.info(f"LEI enrichment would be performed for {name} from {country}")
        
        
        enriched_data["metadata"]["lei_status"] = "not_implemented"
        
    except Exception as e:
        logger.error(f"Error enriching entity with LEI: {str(e)}")

def _apply_graph_tagging(name: str, entity_type: str, enriched_data: Dict[str, Any]) -> None:
    """Apply graph-based entity tagging to extract additional metadata"""
    try:
        
        if entity_type.lower() == "legal":
            lower_name = name.lower()
            
            industries = []
            if any(term in lower_name for term in ["bank", "credit", "finance", "capital", "invest"]):
                industries.append("financial_services")
            if any(term in lower_name for term in ["tech", "software", "digital", "cyber", "computer"]):
                industries.append("technology")
            if any(term in lower_name for term in ["oil", "gas", "petrol", "energy", "power"]):
                industries.append("energy")
            
            if industries:
                enriched_data["metadata"]["industries"] = industries
                enriched_data["sources"].append("graph_tagger")
        
    except Exception as e:
        logger.error(f"Error applying graph tagging: {str(e)}")

def normalize_name(name: str) -> str:
    """Normalize a name for better matching"""
    prefixes = ["mr", "mrs", "ms", "dr", "prof", "sir", "dame"]
    name_parts = name.lower().split()
    if name_parts and name_parts[0] in prefixes:
        name_parts = name_parts[1:]
    
    suffixes = ["jr", "sr", "i", "ii", "iii", "iv", "v"]
    if name_parts and name_parts[-1].rstrip(".") in suffixes:
        name_parts = name_parts[:-1]
    
    return " ".join(name_parts)
