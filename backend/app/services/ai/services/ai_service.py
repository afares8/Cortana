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
from app.services.ai.utils.spanish_input_pipeline import process_spanish_input

logger = logging.getLogger(__name__)

class AIService:
    """
    Service for AI operations.
    """
    
    def __init__(self):
        self.mistral_client = MistralClient()
    
    async def analyze_contract(self, contract_id: int, analysis_type: str, contract_text: Optional[str] = None) -> Optional[AIAnalysisResult]:
        """
        Analyze a contract using AI.
        
        This method applies Spanish preprocessing to the contract text if it's detected as Spanish
        before analyzing it.
        """
        start_time = time.time()
        
        language = "en"
        if contract_text:
            processed_contract_text = process_spanish_input(contract_text)
            
            from app.services.ai.utils.spanish_input_pipeline import spanish_pipeline
            language = "es" if spanish_pipeline.is_spanish(contract_text) else "en"
            
            logger.info(f"Contract text processed through Spanish pipeline: {'changes made' if processed_contract_text != contract_text else 'no changes needed'}")
            
        
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
            language=language,
            confidence_score=0.9,
            created_at=datetime.utcnow(),
            updated_at=None
        )
    
    async def extract_clauses(
        self,
        file: UploadFile,
        clause_types: Optional[List[str]] = None,
        contract_text: Optional[str] = None
    ) -> List[ExtractedClause]:
        """
        Extract clauses from a contract document.
        
        This method applies Spanish preprocessing to the contract text if it's detected as Spanish
        before extracting clauses.
        """
        if not clause_types:
            clause_types = ["confidentiality", "termination", "penalties", "jurisdiction", "obligations"]
        
        language = "en"
        if contract_text:
            processed_contract_text = process_spanish_input(contract_text)
            
            from app.services.ai.utils.spanish_input_pipeline import spanish_pipeline
            language = "es" if spanish_pipeline.is_spanish(contract_text) else "en"
            
            logger.info(f"Contract text processed through Spanish pipeline: {'changes made' if processed_contract_text != contract_text else 'no changes needed'}")
            
        
        clauses = []
        for clause_type in clause_types:
            sample_text = f"Sample {clause_type} clause text"
            if language == "es":
                if clause_type == "confidentiality":
                    sample_text = "Texto de muestra de cláusula de confidencialidad"
                elif clause_type == "termination":
                    sample_text = "Texto de muestra de cláusula de terminación"
                elif clause_type == "penalties":
                    sample_text = "Texto de muestra de cláusula de penalidades"
                elif clause_type == "jurisdiction":
                    sample_text = "Texto de muestra de cláusula de jurisdicción"
                elif clause_type == "obligations":
                    sample_text = "Texto de muestra de cláusula de obligaciones"
            
            clauses.append(
                ExtractedClause(
                    clause_type=clause_type,
                    text=sample_text,
                    start_index=100,
                    end_index=200,
                    confidence=0.9,
                    language=language
                )
            )
        
        return clauses
    
    async def score_risk(self, contract_id: int, contract_text: Optional[str] = None) -> Optional[RiskScore]:
        """
        Score the risk of a contract.
        
        This method applies Spanish preprocessing to the contract text if it's detected as Spanish
        before scoring the risk.
        """
        language = "en"
        if contract_text:
            processed_contract_text = process_spanish_input(contract_text)
            
            from app.services.ai.utils.spanish_input_pipeline import spanish_pipeline
            language = "es" if spanish_pipeline.is_spanish(contract_text) else "en"
            
            logger.info(f"Contract text processed through Spanish pipeline: {'changes made' if processed_contract_text != contract_text else 'no changes needed'}")
            
        
        recommendations = ["Add a liability clause", "Review contract duration"]
        if language == "es":
            recommendations = ["Añadir una cláusula de responsabilidad", "Revisar la duración del contrato"]
        
        return RiskScore(
            score=65.5,
            factors=[
                {"name": "missing_clauses", "impact": "high", "description": "Missing liability clause" if language == "en" else "Falta cláusula de responsabilidad"},
                {"name": "unusual_duration", "impact": "medium", "description": "Contract duration is unusually long" if language == "en" else "La duración del contrato es inusualmente larga"}
            ],
            recommendations=recommendations,
            language=language
        )
    
    async def detect_anomalies(self, contract_id: int, contract_text: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Detect anomalies in a contract.
        
        This method applies Spanish preprocessing to the contract text if it's detected as Spanish
        before detecting anomalies.
        """
        language = "en"
        if contract_text:
            processed_contract_text = process_spanish_input(contract_text)
            
            from app.services.ai.utils.spanish_input_pipeline import spanish_pipeline
            language = "es" if spanish_pipeline.is_spanish(contract_text) else "en"
            
            logger.info(f"Contract text processed through Spanish pipeline: {'changes made' if processed_contract_text != contract_text else 'no changes needed'}")
            
            # In a real implementation, we would use the processed text for anomaly detection
        
        if language == "es":
            return {
                "anomalies": [
                    {"type": "unusual_duration", "description": "La duración del contrato es inusualmente larga", "confidence": 0.85, "language": "es"},
                    {"type": "missing_clause", "description": "Falta cláusula de responsabilidad", "confidence": 0.95, "language": "es"}
                ]
            }
        else:
            return {
                "anomalies": [
                    {"type": "unusual_duration", "description": "Contract duration is unusually long", "confidence": 0.85, "language": "en"},
                    {"type": "missing_clause", "description": "Missing liability clause", "confidence": 0.95, "language": "en"}
                ]
            }
    
    async def query(self, query: str, user_id: Optional[int] = None) -> AIQuery:
        """
        Query the AI system.
        
        This method applies Spanish preprocessing to the input text if it's detected as Spanish
        before sending it to the Mistral model.
        """
        start_time = time.time()
        
        processed_query = process_spanish_input(query)
        
        from app.services.ai.utils.spanish_input_pipeline import spanish_pipeline
        language = "es" if spanish_pipeline.is_spanish(query) else "en"
        
        logger.info(f"Query processed through Spanish pipeline: {'changes made' if processed_query != query else 'no changes needed'}")
        
        response_text = await self.mistral_client.generate(processed_query)
        
        processing_time = time.time() - start_time
        
        return AIQuery(
            id=1,
            user_id=user_id,
            query_text=query,
            response_text=response_text,
            model_used=self.mistral_client.model_name,
            processing_time=processing_time,
            language=language,
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
        
        This method applies Spanish preprocessing to the input text if it's detected as Spanish
        before sending it to the Mistral model.
        """
        if debug:
            processed_inputs, debug_info = process_spanish_input(inputs, debug=True)
            original_input = inputs
        else:
            processed_inputs = process_spanish_input(inputs)
            original_input = inputs
        
        logger.info(f"Input processed through Spanish pipeline: {'changes made' if processed_inputs != inputs else 'no changes needed'}")
        
        result = await self.mistral_client.generate(
            processed_inputs,
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
            response.original_input = original_input
            response.processed_input = processed_inputs
            if 'debug_info' in locals():
                response.spanish_processing = debug_info
        
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
