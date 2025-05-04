from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import time
import logging
from fastapi import UploadFile

from app.services.ai.models.ai_model import AIAnalysisResult, ExtractedClause, RiskScore, AIQuery
from app.services.ai.schemas.ai_schema import GenerateResponse
from app.services.ai.schemas.contextual_schema import ContextualGenerateResponse
from app.services.ai.utils.mistral_client import MistralClient
from app.services.ai.utils.intent_classifier import intent_classifier, IntentType
from app.services.ai.utils.context_retriever import context_retriever
from app.services.ai.utils.prompt_builder import prompt_builder

logger = logging.getLogger(__name__)

class AIService:
    """
    Service for AI operations.
    """
    
    def __init__(self):
        self.mistral_client = MistralClient()
    
    async def analyze_contract(self, contract_id: int, analysis_type: str) -> Optional[AIAnalysisResult]:
        """
        Analyze a contract using AI.
        """
        start_time = time.time()
        
        result = None
        if analysis_type == "clause_extraction":
            result = {
                "clauses": [
                    {
                        "clause_type": "confidentiality",
                        "text": "Sample confidentiality clause text",
                        "start_index": 100,
                        "end_index": 200,
                        "confidence": 0.95
                    }
                ]
            }
        elif analysis_type == "risk_scoring":
            result = {
                "score": 65.5,
                "factors": [
                    {"name": "missing_clauses", "impact": "high", "description": "Missing liability clause"}
                ],
                "recommendations": ["Add a liability clause"]
            }
        elif analysis_type == "anomaly_detection":
            result = {
                "anomalies": [
                    {"type": "unusual_duration", "description": "Contract duration is unusually long", "confidence": 0.85}
                ]
            }
        
        if not result:
            return None
        
        processing_time = time.time() - start_time
        
        return AIAnalysisResult(
            id=1,
            contract_id=contract_id,
            analysis_type=analysis_type,
            result=result,
            model_used="teknium/OpenHermes-2.5-Mistral-7B",
            processing_time=processing_time,
            language="en",
            confidence_score=0.9,
            created_at=datetime.utcnow(),
            updated_at=None
        )
    
    async def extract_clauses(
        self,
        file: UploadFile,
        clause_types: Optional[List[str]] = None
    ) -> List[ExtractedClause]:
        """
        Extract clauses from a contract document.
        """
        
        if not clause_types:
            clause_types = ["confidentiality", "termination", "penalties", "jurisdiction", "obligations"]
        
        clauses = []
        for clause_type in clause_types:
            clauses.append(
                ExtractedClause(
                    clause_type=clause_type,
                    text=f"Sample {clause_type} clause text",
                    start_index=100,
                    end_index=200,
                    confidence=0.9
                )
            )
        
        return clauses
    
    async def score_risk(self, contract_id: int) -> Optional[RiskScore]:
        """
        Score the risk of a contract.
        """
        
        return RiskScore(
            score=65.5,
            factors=[
                {"name": "missing_clauses", "impact": "high", "description": "Missing liability clause"},
                {"name": "unusual_duration", "impact": "medium", "description": "Contract duration is unusually long"}
            ],
            recommendations=["Add a liability clause", "Review contract duration"]
        )
    
    async def detect_anomalies(self, contract_id: int) -> Optional[Dict[str, Any]]:
        """
        Detect anomalies in a contract.
        """
        
        return {
            "anomalies": [
                {"type": "unusual_duration", "description": "Contract duration is unusually long", "confidence": 0.85},
                {"type": "missing_clause", "description": "Missing liability clause", "confidence": 0.95}
            ]
        }
    
    async def query(self, query: str, user_id: Optional[int] = None) -> AIQuery:
        """
        Query the AI system.
        """
        
        start_time = time.time()
        
        response_text = await self.mistral_client.generate(query)
        
        processing_time = time.time() - start_time
        
        return AIQuery(
            id=1,
            user_id=user_id,
            query_text=query,
            response_text=response_text,
            model_used=self.mistral_client.model_name,
            processing_time=processing_time,
            language="en",
            is_fallback=self.mistral_client.fallback_mode,
            created_at=datetime.utcnow(),
            updated_at=None
        )
    
    async def generate(
        self,
        inputs: str,
        max_new_tokens: Optional[int] = 500,
        temperature: Optional[float] = 0.7,
        top_p: Optional[float] = 0.9,
        debug: Optional[bool] = False
    ) -> GenerateResponse:
        """
        Generate text using the Mistral model.
        """
        result = await self.mistral_client.generate(
            inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            debug=debug
        )
        
        response = GenerateResponse(
            generated_text=result,
            is_fallback=self.mistral_client.fallback_mode,
            model=self.mistral_client.model_name
        )
        
        if debug:
            response.original_input = inputs
            response.processed_input = inputs  # In a real implementation, this would be the processed input
        
        return response
    
    async def contextual_generate(
        self,
        query: str,
        user_id: Optional[int] = None,
        max_new_tokens: Optional[int] = 500,
        temperature: Optional[float] = 0.7,
        top_p: Optional[float] = 0.9,
        debug: Optional[bool] = False
    ) -> ContextualGenerateResponse:
        """
        Generate text using the Mistral model with context from internal application data.
        
        This method:
        1. Classifies the intent of the query
        2. Retrieves relevant context data based on the intent
        3. Builds an enhanced prompt with the context data
        4. Generates a response using the enhanced prompt
        5. Returns the response with additional context information
        """
        start_time = time.time()
        
        intent, confidence = intent_classifier.classify_intent(query)
        logger.info(f"Classified query intent: {intent} (confidence: {confidence:.2f})")
        
        params = intent_classifier.extract_parameters(query, intent)
        logger.info(f"Extracted parameters: {params}")
        
        context_data = await context_retriever.retrieve_context(intent, params, user_id)
        logger.info(f"Retrieved context data for intent {intent}")
        
        language = "es"  # Could be enhanced with language detection
        
        enhanced_prompt = prompt_builder.build_prompt(query, intent, context_data, language)
        logger.info(f"Built enhanced prompt with context data")
        
        result = await self.mistral_client.generate(
            enhanced_prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            debug=debug
        )
        
        processing_time = time.time() - start_time
        
        response = ContextualGenerateResponse(
            generated_text=result,
            is_fallback=self.mistral_client.fallback_mode,
            model=self.mistral_client.model_name,
            intent=intent,
            original_query=query
        )
        
        if debug:
            response.context_data = context_data
            response.enhanced_prompt = enhanced_prompt
            response.debug_info = {
                "confidence": confidence,
                "parameters": params,
                "processing_time": processing_time,
                "language": language
            }
        
        return response

ai_service = AIService()
