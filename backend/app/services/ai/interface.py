from typing import List, Optional, Dict, Any
from fastapi import UploadFile

from app.services.ai.models.ai_model import AIAnalysisResult, ExtractedClause, RiskScore, AIQuery
from app.services.ai.schemas.ai_schema import GenerateResponse

class AIServiceInterface:
    """
    Interface for AI operations.
    """
    
    async def analyze_contract(self, contract_id: int, analysis_type: str) -> Optional[AIAnalysisResult]:
        """
        Analyze a contract using AI.
        """
        pass
    
    async def extract_clauses(
        self,
        file: UploadFile,
        clause_types: Optional[List[str]] = None
    ) -> List[ExtractedClause]:
        """
        Extract clauses from a contract document.
        """
        pass
    
    async def score_risk(self, contract_id: int) -> Optional[RiskScore]:
        """
        Score the risk of a contract.
        """
        pass
    
    async def detect_anomalies(self, contract_id: int) -> Optional[Dict[str, Any]]:
        """
        Detect anomalies in a contract.
        """
        pass
    
    async def query(self, query: str, user_id: Optional[int] = None) -> AIQuery:
        """
        Query the AI system.
        """
        pass
    
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
        pass
