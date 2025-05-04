from typing import List, Dict, Any, Optional, Tuple, Union
import logging
import os
import json
from datetime import datetime
from enum import Enum

from app.services.compliance.utils.document_embeddings import document_embeddings
from app.services.ai.utils.mistral_client import MistralClient
from app.services.compliance.models.compliance import (
    ComplianceReport, PEPScreeningResult, 
    SanctionsScreeningResult, DocumentRetentionPolicy
)

logger = logging.getLogger(__name__)

mistral_client = MistralClient()

class DueDiligenceLevel(str, Enum):
    BASIC = "basic"
    ENHANCED = "enhanced"
    SIMPLIFIED = "simplified"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class RiskCategory(str, Enum):
    CLIENT = "client"
    GEOGRAPHIC = "geographic"
    PRODUCT = "product"
    CHANNEL = "channel"
    TRANSACTIONAL = "transactional"

class ComplianceManualIntegration:
    """
    Service for integrating the compliance manual with the LegalContractTracker.
    Uses document embeddings and Mistral 7B for contextual understanding.
    """
    
    def __init__(self):
        """
        Initialize the compliance manual integration service.
        """
        self.embeddings = document_embeddings
        self.mistral = mistral_client
    
    async def embed_compliance_manual(self, pdf_path: str) -> bool:
        """
        Embed the compliance manual PDF into the vector database.
        
        Args:
            pdf_path: Path to the compliance manual PDF
            
        Returns:
            True if successful, False otherwise
        """
        metadata = {
            "document_type": "compliance_manual",
            "title": "Manual de Prevención de Blanqueo de Capitales - Magnate Maximus S.A.",
            "embedded_at": datetime.utcnow().isoformat()
        }
        
        return self.embeddings.embed_document(pdf_path, document_metadata=metadata)
    
    async def get_due_diligence_requirements(
        self, 
        due_diligence_level: DueDiligenceLevel,
        client_type: str = "individual"
    ) -> Dict[str, Any]:
        """
        Get the requirements for a specific due diligence level from the compliance manual.
        
        Args:
            due_diligence_level: Level of due diligence (basic, enhanced, simplified)
            client_type: Type of client (individual, company, etc.)
            
        Returns:
            Dictionary with due diligence requirements
        """
        query = f"What are the requirements for {due_diligence_level.value} due diligence for a {client_type} client?"
        context = self.embeddings.get_relevant_context(query, k=3)
        
        prompt = f"""
        Based on the following excerpts from the compliance manual, list the specific requirements for {due_diligence_level.value} due diligence for a {client_type} client.
        
        COMPLIANCE MANUAL EXCERPTS:
        {context}
        
        Please provide a structured response with the following information:
        1. Required documents
        2. Verification steps
        3. Approval requirements
        4. Monitoring frequency
        5. Risk assessment criteria
        
        Format the response as a JSON object.
        """
        
        response = await self.mistral.generate(prompt)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                requirements = json.loads(json_str)
            else:
                requirements = {
                    "raw_response": response,
                    "due_diligence_level": due_diligence_level.value,
                    "client_type": client_type
                }
        except Exception as e:
            logger.error(f"Error parsing Mistral response: {str(e)}")
            requirements = {
                "error": str(e),
                "raw_response": response,
                "due_diligence_level": due_diligence_level.value,
                "client_type": client_type
            }
        
        return requirements
    
    async def calculate_risk_score(
        self,
        client_id: int,
        risk_factors: Dict[RiskCategory, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate a risk score based on the risk matrices defined in the compliance manual.
        
        Args:
            client_id: ID of the client
            risk_factors: Dictionary of risk factors by category
            
        Returns:
            Dictionary with risk assessment results
        """
        query = "How to calculate risk scores using the risk matrices and heat map in the compliance manual?"
        context = self.embeddings.get_relevant_context(query, k=3)
        
        risk_factors_str = json.dumps(risk_factors, indent=2)
        
        prompt = f"""
        Based on the following excerpts from the compliance manual about risk matrices and the heat map, calculate the risk score for a client with the following risk factors:
        
        COMPLIANCE MANUAL EXCERPTS:
        {context}
        
        RISK FACTORS:
        {risk_factors_str}
        
        Please provide a structured response with the following information:
        1. Individual risk scores for each category (Client, Geographic, Product/Service, Channel, Transactional)
        2. Overall inherent risk score
        3. Risk level classification (Low, Medium, High, Very High)
        4. Justification for the risk assessment
        5. Recommended due diligence level based on the risk assessment
        
        Format the response as a JSON object.
        """
        
        response = await self.mistral.generate(prompt)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                risk_assessment = json.loads(json_str)
            else:
                risk_assessment = {
                    "raw_response": response,
                    "client_id": client_id
                }
        except Exception as e:
            logger.error(f"Error parsing Mistral response: {str(e)}")
            risk_assessment = {
                "error": str(e),
                "raw_response": response,
                "client_id": client_id
            }
        
        return risk_assessment
    
    async def detect_suspicious_activity(
        self,
        transaction_data: Dict[str, Any],
        client_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect suspicious activity based on transaction data and client profile.
        
        Args:
            transaction_data: Data about the transaction
            client_profile: Profile information about the client
            
        Returns:
            Dictionary with suspicious activity detection results
        """
        query = "What are the red flags and indicators of suspicious activity according to the compliance manual?"
        context = self.embeddings.get_relevant_context(query, k=3)
        
        transaction_str = json.dumps(transaction_data, indent=2)
        profile_str = json.dumps(client_profile, indent=2)
        
        prompt = f"""
        Based on the following excerpts from the compliance manual about suspicious activity indicators, analyze the transaction and client profile to detect any suspicious activity:
        
        COMPLIANCE MANUAL EXCERPTS:
        {context}
        
        TRANSACTION DATA:
        {transaction_str}
        
        CLIENT PROFILE:
        {profile_str}
        
        Please provide a structured response with the following information:
        1. Is this activity suspicious? (Yes/No)
        2. Identified red flags (list all that apply)
        3. Risk level of the suspicious activity (Low, Medium, High)
        4. Recommended actions (e.g., request explanation, file ROS report, etc.)
        5. Justification for the assessment
        
        Format the response as a JSON object.
        """
        
        response = await self.mistral.generate(prompt)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                assessment = json.loads(json_str)
            else:
                assessment = {
                    "raw_response": response,
                    "transaction_id": transaction_data.get("transaction_id", "unknown")
                }
        except Exception as e:
            logger.error(f"Error parsing Mistral response: {str(e)}")
            assessment = {
                "error": str(e),
                "raw_response": response,
                "transaction_id": transaction_data.get("transaction_id", "unknown")
            }
        
        return assessment
    
    async def generate_ros_report(
        self,
        suspicious_activity: Dict[str, Any],
        client_data: Dict[str, Any],
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a Suspicious Activity Report (ROS) based on detected suspicious activity.
        
        Args:
            suspicious_activity: Results of suspicious activity detection
            client_data: Data about the client
            transaction_data: Data about the transaction
            
        Returns:
            Dictionary with the ROS report
        """
        query = "What are the requirements for filing a Suspicious Activity Report (ROS) according to the compliance manual?"
        context = self.embeddings.get_relevant_context(query, k=3)
        
        suspicious_str = json.dumps(suspicious_activity, indent=2)
        client_str = json.dumps(client_data, indent=2)
        transaction_str = json.dumps(transaction_data, indent=2)
        
        prompt = f"""
        Based on the following excerpts from the compliance manual about ROS report requirements, generate a Suspicious Activity Report (ROS) for the following suspicious activity:
        
        COMPLIANCE MANUAL EXCERPTS:
        {context}
        
        SUSPICIOUS ACTIVITY ASSESSMENT:
        {suspicious_str}
        
        CLIENT DATA:
        {client_str}
        
        TRANSACTION DATA:
        {transaction_str}
        
        Please provide a structured ROS report with the following sections:
        1. Reporting Entity Information
        2. Subject Information (Client)
        3. Suspicious Activity Details
        4. Transaction Details
        5. Suspicious Activity Indicators
        6. Narrative Description
        7. Supporting Documentation
        8. Certification
        
        Format the response as a JSON object.
        """
        
        response = await self.mistral.generate(prompt)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                ros_report = json.loads(json_str)
            else:
                ros_report = {
                    "raw_response": response,
                    "client_id": client_data.get("client_id", "unknown"),
                    "transaction_id": transaction_data.get("transaction_id", "unknown")
                }
        except Exception as e:
            logger.error(f"Error parsing Mistral response: {str(e)}")
            ros_report = {
                "error": str(e),
                "raw_response": response,
                "client_id": client_data.get("client_id", "unknown"),
                "transaction_id": transaction_data.get("transaction_id", "unknown")
            }
        
        return ros_report
    
    async def get_document_retention_requirements(self, document_type: str) -> Dict[str, Any]:
        """
        Get document retention requirements from the compliance manual.
        
        Args:
            document_type: Type of document
            
        Returns:
            Dictionary with document retention requirements
        """
        query = f"What are the document retention requirements for {document_type} according to the compliance manual?"
        context = self.embeddings.get_relevant_context(query, k=3)
        
        prompt = f"""
        Based on the following excerpts from the compliance manual, what are the document retention requirements for {document_type}?
        
        COMPLIANCE MANUAL EXCERPTS:
        {context}
        
        Please provide a structured response with the following information:
        1. Minimum retention period (in years)
        2. Legal basis for the retention period
        3. Storage requirements
        4. Access restrictions
        5. Destruction procedures
        
        Format the response as a JSON object.
        """
        
        response = await self.mistral.generate(prompt)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                requirements = json.loads(json_str)
            else:
                requirements = {
                    "raw_response": response,
                    "document_type": document_type
                }
        except Exception as e:
            logger.error(f"Error parsing Mistral response: {str(e)}")
            requirements = {
                "error": str(e),
                "raw_response": response,
                "document_type": document_type
            }
        
        return requirements
    
    async def query_compliance_manual(self, query: str) -> Dict[str, Any]:
        """
        Query the compliance manual using RAG (Retrieval-Augmented Generation).
        
        Args:
            query: Query text
            
        Returns:
            Dictionary with the query response
        """
        context = self.embeddings.get_relevant_context(query, k=5)
        
        prompt = f"""
        Based on the following excerpts from the compliance manual, please answer this question:
        
        QUESTION:
        {query}
        
        COMPLIANCE MANUAL EXCERPTS:
        {context}
        
        Please provide a detailed and accurate answer based only on the information in the compliance manual excerpts. If the information is not available in the excerpts, please state that clearly.
        """
        
        response = await self.mistral.generate(prompt)
        
        return {
            "query": query,
            "context": context,
            "response": response,
            "is_fallback": self.mistral.fallback_mode
        }

compliance_manual_integration = ComplianceManualIntegration()
