from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import logging
import asyncio
import uuid

from app.services.compliance.schemas.verify import (
    CustomerVerifyRequest, CustomerVerificationResponse,
    VerificationResult, VerificationMatch, EntityBase
)
from app.services.compliance.models.verify import CustomerVerification
from app.services.compliance.utils.data_sources import (
    un_sanctions_client, ofac_sanctions_client, 
    eu_sanctions_client, wikidata_client
)
from app.services.compliance.utils.entity_enrichment import enrich_entity

logger = logging.getLogger(__name__)

class VerificationService:
    """Service for customer verification operations."""
    
    async def verify_customer(self, request: CustomerVerifyRequest) -> CustomerVerificationResponse:
        """
        Verify a customer against PEP and sanctions lists.
        
        Args:
            request: Customer verification request
            
        Returns:
            Verification response with results from multiple sources
        """
        verification_id = str(uuid.uuid4())
        customer = request.customer
        directors = request.directors or []
        ubos = request.ubos or []
        
        enriched_customer = await enrich_entity(customer.dict())
        enriched_directors = [await enrich_entity(director.dict()) for director in directors]
        enriched_ubos = [await enrich_entity(ubo.dict()) for ubo in ubos]
        
        tasks = [
            self._check_pep(customer, enriched_customer),
            self._check_ofac(customer, enriched_customer),
            self._check_un_sanctions(customer, enriched_customer),
            self._check_eu_sanctions(customer, enriched_customer)
        ]
        
        pep_result, ofac_result, un_result, eu_result = await asyncio.gather(*tasks)
        
        if customer.type.lower() == "legal":
            for idx, director in enumerate(directors):
                director_tasks = [
                    self._check_pep(director, enriched_directors[idx]),
                    self._check_ofac(director, enriched_directors[idx]),
                    self._check_un_sanctions(director, enriched_directors[idx]),
                    self._check_eu_sanctions(director, enriched_directors[idx])
                ]
                director_results = await asyncio.gather(*director_tasks)
                
                self._merge_results(pep_result, director_results[0], f"director:{idx}")
                self._merge_results(ofac_result, director_results[1], f"director:{idx}")
                self._merge_results(un_result, director_results[2], f"director:{idx}")
                self._merge_results(eu_result, director_results[3], f"director:{idx}")
            
            for idx, ubo in enumerate(ubos):
                ubo_tasks = [
                    self._check_pep(ubo, enriched_ubos[idx]),
                    self._check_ofac(ubo, enriched_ubos[idx]),
                    self._check_un_sanctions(ubo, enriched_ubos[idx]),
                    self._check_eu_sanctions(ubo, enriched_ubos[idx])
                ]
                ubo_results = await asyncio.gather(*ubo_tasks)
                
                self._merge_results(pep_result, ubo_results[0], f"ubo:{idx}")
                self._merge_results(ofac_result, ubo_results[1], f"ubo:{idx}")
                self._merge_results(un_result, ubo_results[2], f"ubo:{idx}")
                self._merge_results(eu_result, ubo_results[3], f"ubo:{idx}")
        
        enriched_data = {
            "customer": enriched_customer,
            "directors": enriched_directors if directors else [],
            "ubos": enriched_ubos if ubos else []
        }
        
        response = CustomerVerificationResponse(
            pep=pep_result,
            ofac=ofac_result,
            un=un_result,
            eu=eu_result,
            enriched_data=enriched_data,
            verification_id=verification_id,
            created_at=datetime.utcnow()
        )
        
        
        return response
    
    def _merge_results(self, main_result: VerificationResult, additional_result: VerificationResult, prefix: str) -> None:
        """Merge additional results into the main result with appropriate prefixes"""
        if additional_result.status in ["watchlist", "matched"] and main_result.status == "clear":
            main_result.status = additional_result.status
        
        for match in additional_result.matches:
            match.details["relationship"] = prefix
            main_result.matches.append(match)
    
    async def _check_pep(self, entity: EntityBase, enriched_data: Dict[str, Any]) -> VerificationResult:
        """Check an entity against PEP lists"""
        logger.info(f"Checking {entity.name} against PEP lists")
        
        result = VerificationResult(
            status="clear",
            matches=[],
            source="pep",
            timestamp=datetime.utcnow()
        )
        
        try:
            wikidata_response = await wikidata_client.search_entity(entity.name, is_pep=True)
            
            if "error" not in wikidata_response and "results" in wikidata_response:
                bindings = wikidata_response.get("results", {}).get("bindings", [])
                
                for binding in bindings:
                    if "item" in binding and "itemLabel" in binding:
                        item_uri = binding["item"].get("value", "")
                        item_label = binding["itemLabel"].get("value", "")
                        
                        is_pep_match = False
                        position_label = binding.get("positionLabel", {}).get("value", "")
                        
                        political_terms = ["minister", "president", "governor", "senator", 
                                          "parliament", "congress", "deputy", "secretary", 
                                          "chief", "director", "head", "ambassador"]
                        
                        if any(term in position_label.lower() for term in political_terms):
                            is_pep_match = True
                        
                        if is_pep_match:
                            from difflib import SequenceMatcher
                            score = SequenceMatcher(None, entity.name.lower(), item_label.lower()).ratio()
                            
                            if score > 0.7:  # Threshold for considering it a match
                                result.status = "matched" if score > 0.9 else "watchlist"
                                
                                match = VerificationMatch(
                                    source="wikidata_pep",
                                    source_id=item_uri.split("/")[-1],
                                    name=item_label,
                                    match_type="exact" if score > 0.9 else "partial",
                                    score=score,
                                    details={
                                        "position": position_label,
                                        "country": binding.get("countryLabel", {}).get("value", "Unknown"),
                                        "start_date": binding.get("startDate", {}).get("value", ""),
                                        "end_date": binding.get("endDate", {}).get("value", "")
                                    }
                                )
                                
                                result.matches.append(match)
            
            for alias in enriched_data.get("aliases", []):
                if alias != entity.name:
                    alias_response = await wikidata_client.search_entity(alias, is_pep=True)
                    
                    if "error" not in alias_response and "results" in alias_response:
                        alias_bindings = alias_response.get("results", {}).get("bindings", [])
                        
                        for binding in alias_bindings:
                            if "item" in binding and "itemLabel" in binding:
                                item_uri = binding["item"].get("value", "")
                                item_label = binding["itemLabel"].get("value", "")
                                
                                is_pep_match = False
                                position_label = binding.get("positionLabel", {}).get("value", "")
                                
                                if any(term in position_label.lower() for term in political_terms):
                                    is_pep_match = True
                                
                                if is_pep_match:
                                    score = SequenceMatcher(None, alias.lower(), item_label.lower()).ratio()
                                    
                                    if score > 0.7:
                                        result.status = "matched" if score > 0.9 else "watchlist"
                                        
                                        match = VerificationMatch(
                                            source="wikidata_pep",
                                            source_id=item_uri.split("/")[-1],
                                            name=item_label,
                                            match_type="alias",
                                            score=score,
                                            details={
                                                "position": position_label,
                                                "country": binding.get("countryLabel", {}).get("value", "Unknown"),
                                                "start_date": binding.get("startDate", {}).get("value", ""),
                                                "end_date": binding.get("endDate", {}).get("value", ""),
                                                "matched_alias": alias
                                            }
                                        )
                                        
                                        result.matches.append(match)
            
            
        except Exception as e:
            logger.error(f"Error checking PEP status: {str(e)}")
        
        return result
    
    async def _check_ofac(self, entity: EntityBase, enriched_data: Dict[str, Any]) -> VerificationResult:
        """Check an entity against OFAC sanctions list"""
        logger.info(f"Checking {entity.name} against OFAC sanctions list")
        
        result = VerificationResult(
            status="clear",
            matches=[],
            source="ofac",
            timestamp=datetime.utcnow()
        )
        
        try:
            ofac_entity_type = "individual" if entity.type.lower() == "natural" else "entity"
            
            ofac_response = await ofac_sanctions_client.search_entity(
                entity.name, 
                entity_type=ofac_entity_type,
                country=entity.country
            )
            
            if "error" not in ofac_response and "data" in ofac_response:
                matches = ofac_response.get("data", [])
                
                for match_data in matches:
                    sdn_name = match_data.get("name", "")
                    sdn_id = match_data.get("id", "")
                    programs = match_data.get("programs", [])
                    
                    from difflib import SequenceMatcher
                    score = SequenceMatcher(None, entity.name.lower(), sdn_name.lower()).ratio()
                    
                    if score > 0.7:  # Threshold for considering it a match
                        result.status = "matched" if score > 0.9 else "watchlist"
                        
                        match = VerificationMatch(
                            source="ofac",
                            source_id=sdn_id,
                            name=sdn_name,
                            match_type="exact" if score > 0.9 else "partial",
                            score=score,
                            details={
                                "programs": programs,
                                "entity_type": match_data.get("sdnType", ""),
                                "remarks": match_data.get("remarks", "")
                            }
                        )
                        
                        result.matches.append(match)
            
            for alias in enriched_data.get("aliases", []):
                if alias != entity.name:
                    alias_response = await ofac_sanctions_client.search_entity(
                        alias, 
                        entity_type=ofac_entity_type,
                        country=entity.country
                    )
                    
                    if "error" not in alias_response and "data" in alias_response:
                        alias_matches = alias_response.get("data", [])
                        
                        for match_data in alias_matches:
                            sdn_name = match_data.get("name", "")
                            sdn_id = match_data.get("id", "")
                            programs = match_data.get("programs", [])
                            
                            score = SequenceMatcher(None, alias.lower(), sdn_name.lower()).ratio()
                            
                            if score > 0.7:
                                result.status = "matched" if score > 0.9 else "watchlist"
                                
                                match = VerificationMatch(
                                    source="ofac",
                                    source_id=sdn_id,
                                    name=sdn_name,
                                    match_type="alias",
                                    score=score,
                                    details={
                                        "programs": programs,
                                        "entity_type": match_data.get("sdnType", ""),
                                        "remarks": match_data.get("remarks", ""),
                                        "matched_alias": alias
                                    }
                                )
                                
                                result.matches.append(match)
            
        except Exception as e:
            logger.error(f"Error checking OFAC sanctions: {str(e)}")
        
        return result
    
    async def _check_un_sanctions(self, entity: EntityBase, enriched_data: Dict[str, Any]) -> VerificationResult:
        """Check an entity against UN sanctions list"""
        logger.info(f"Checking {entity.name} against UN sanctions list")
        
        result = VerificationResult(
            status="clear",
            matches=[],
            source="un",
            timestamp=datetime.utcnow()
        )
        
        try:
            un_entity_type = "individual" if entity.type.lower() == "natural" else "entity"
            
            un_response = await un_sanctions_client.search_entity(
                entity.name, 
                entity_type=un_entity_type,
                country=entity.country
            )
            
            if "error" not in un_response and "data" in un_response:
                matches = un_response.get("data", [])
                
                for match_data in matches:
                    un_name = match_data.get("name", "")
                    un_id = match_data.get("id", "")
                    un_reference = match_data.get("reference", "")
                    
                    from difflib import SequenceMatcher
                    score = SequenceMatcher(None, entity.name.lower(), un_name.lower()).ratio()
                    
                    if score > 0.7:  # Threshold for considering it a match
                        result.status = "matched" if score > 0.9 else "watchlist"
                        
                        match = VerificationMatch(
                            source="un",
                            source_id=un_id,
                            name=un_name,
                            match_type="exact" if score > 0.9 else "partial",
                            score=score,
                            details={
                                "reference": un_reference,
                                "entity_type": match_data.get("type", ""),
                                "nationality": match_data.get("nationality", ""),
                                "listed_on": match_data.get("listed_on", "")
                            }
                        )
                        
                        result.matches.append(match)
            
            for alias in enriched_data.get("aliases", []):
                if alias != entity.name:
                    alias_response = await un_sanctions_client.search_entity(
                        alias, 
                        entity_type=un_entity_type,
                        country=entity.country
                    )
                    
                    if "error" not in alias_response and "data" in alias_response:
                        alias_matches = alias_response.get("data", [])
                        
                        for match_data in alias_matches:
                            un_name = match_data.get("name", "")
                            un_id = match_data.get("id", "")
                            un_reference = match_data.get("reference", "")
                            
                            score = SequenceMatcher(None, alias.lower(), un_name.lower()).ratio()
                            
                            if score > 0.7:
                                result.status = "matched" if score > 0.9 else "watchlist"
                                
                                match = VerificationMatch(
                                    source="un",
                                    source_id=un_id,
                                    name=un_name,
                                    match_type="alias",
                                    score=score,
                                    details={
                                        "reference": un_reference,
                                        "entity_type": match_data.get("type", ""),
                                        "nationality": match_data.get("nationality", ""),
                                        "listed_on": match_data.get("listed_on", ""),
                                        "matched_alias": alias
                                    }
                                )
                                
                                result.matches.append(match)
            
        except Exception as e:
            logger.error(f"Error checking UN sanctions: {str(e)}")
        
        return result
    
    async def _check_eu_sanctions(self, entity: EntityBase, enriched_data: Dict[str, Any]) -> VerificationResult:
        """Check an entity against EU sanctions list"""
        logger.info(f"Checking {entity.name} against EU sanctions list")
        
        result = VerificationResult(
            status="clear",
            matches=[],
            source="eu",
            timestamp=datetime.utcnow()
        )
        
        try:
            eu_entity_type = "individual" if entity.type.lower() == "natural" else "entity"
            
            eu_response = await eu_sanctions_client.search_entity(
                entity.name, 
                entity_type=eu_entity_type,
                country=entity.country
            )
            
            if "error" not in eu_response and "data" in eu_response:
                matches = eu_response.get("data", [])
                
                for match_data in matches:
                    eu_name = match_data.get("name", "")
                    eu_id = match_data.get("id", "")
                    eu_regulation = match_data.get("regulation", "")
                    
                    from difflib import SequenceMatcher
                    score = SequenceMatcher(None, entity.name.lower(), eu_name.lower()).ratio()
                    
                    if score > 0.7:  # Threshold for considering it a match
                        result.status = "matched" if score > 0.9 else "watchlist"
                        
                        match = VerificationMatch(
                            source="eu",
                            source_id=eu_id,
                            name=eu_name,
                            match_type="exact" if score > 0.9 else "partial",
                            score=score,
                            details={
                                "regulation": eu_regulation,
                                "entity_type": match_data.get("type", ""),
                                "subject_type": match_data.get("subject_type", ""),
                                "publication_date": match_data.get("publication_date", "")
                            }
                        )
                        
                        result.matches.append(match)
            
            for alias in enriched_data.get("aliases", []):
                if alias != entity.name:
                    alias_response = await eu_sanctions_client.search_entity(
                        alias, 
                        entity_type=eu_entity_type,
                        country=entity.country
                    )
                    
                    if "error" not in alias_response and "data" in alias_response:
                        alias_matches = alias_response.get("data", [])
                        
                        for match_data in alias_matches:
                            eu_name = match_data.get("name", "")
                            eu_id = match_data.get("id", "")
                            eu_regulation = match_data.get("regulation", "")
                            
                            score = SequenceMatcher(None, alias.lower(), eu_name.lower()).ratio()
                            
                            if score > 0.7:
                                result.status = "matched" if score > 0.9 else "watchlist"
                                
                                match = VerificationMatch(
                                    source="eu",
                                    source_id=eu_id,
                                    name=eu_name,
                                    match_type="alias",
                                    score=score,
                                    details={
                                        "regulation": eu_regulation,
                                        "entity_type": match_data.get("type", ""),
                                        "subject_type": match_data.get("subject_type", ""),
                                        "publication_date": match_data.get("publication_date", ""),
                                        "matched_alias": alias
                                    }
                                )
                                
                                result.matches.append(match)
            
        except Exception as e:
            logger.error(f"Error checking EU sanctions: {str(e)}")
        
        return result

verification_service = VerificationService()
