"""
Client for interacting with the LLM model via the Text Generation Inference API.
"""
import json
import logging
import httpx
import os
import platform
import subprocess
from typing import Dict, List, Optional, Any, Union, Tuple
from pydantic import BaseModel

from app.services.ai.spanish_input_pipeline import process_spanish_input

logger = logging.getLogger(__name__)

class MistralRequest(BaseModel):
    inputs: str
    parameters: Dict[str, Any] = {
        "max_new_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.95,
        "do_sample": True,
        "repetition_penalty": 1.1
    }

class MistralClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.environ.get("MISTRAL_API_URL", "http://ai-service:80")
        logger.info(f"Initializing MistralClient with base_url: {self.base_url}")
        self.client = httpx.AsyncClient(timeout=60.0)
        self.initialized = False
        
        env_fallback = os.environ.get("AI_FALLBACK_MODE", "").lower()
        
        if env_fallback:
            logger.info(f"AI_FALLBACK_MODE environment variable found: '{env_fallback}'")
        else:
            logger.info("AI_FALLBACK_MODE not set, will auto-detect GPU availability")
        
        if env_fallback == "true":
            self.fallback_mode = True
            logger.info("Fallback mode explicitly enabled via AI_FALLBACK_MODE=true")
        elif env_fallback == "false":
            self.fallback_mode = False
            logger.info("Fallback mode explicitly disabled via AI_FALLBACK_MODE=false")
        else:
            self.fallback_mode = True
            logger.info("Will check GPU availability during first request")
        
        self.language_mode = os.environ.get("AI_LANGUAGE_MODE", "").lower()
        if self.language_mode == "es":
            logger.info("Spanish language mode explicitly enabled")
        else:
            logger.info("Using auto-detection for language processing")
        
        logger.info(f"Initial fallback mode is {'enabled' if self.fallback_mode else 'disabled'}")
        
    async def initialize(self):
        """Initialize the client by checking GPU availability."""
        if not self.initialized:
            logger.info("Initializing MistralClient and checking GPU availability")
            env_fallback = os.environ.get("AI_FALLBACK_MODE", "").lower()
            if env_fallback not in ["true", "false"]:
                gpu_available = await self._check_gpu_available()
                self.fallback_mode = not gpu_available
                logger.info(f"Auto-detected GPU availability: {'Available' if gpu_available else 'Not available'}")
            self.initialized = True
    
    async def _check_nvidia_smi(self) -> bool:
        """
        Check if NVIDIA GPU is available using nvidia-smi command.
        
        Returns:
            bool: True if GPU is available, False otherwise
        """
        try:
            import asyncio
            process = await asyncio.create_subprocess_exec(
                "nvidia-smi", 
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.warning(f"nvidia-smi exited with code {process.returncode}: {stderr.decode()}")
                return False
                
            logger.info("nvidia-smi executed successfully, GPU is available")
            return True
        except Exception as e:
            logger.warning(f"Error checking nvidia-smi: {e}")
            return False
            
    async def _check_gpu_available(self) -> bool:
        """
        Check if GPU is available by pinging the AI service and checking for NVIDIA GPU.
        Also sets self.fallback_mode if necessary.
        """
        if os.environ.get("AI_FALLBACK_MODE", "").lower() == "true":
            logger.warning("AI_FALLBACK_MODE=true found in environment, using fallback mode")
            self.fallback_mode = True
            return False

        force_gpu_mode = os.environ.get("AI_FALLBACK_MODE", "").lower() == "false"
        if force_gpu_mode:
            logger.info("AI_FALLBACK_MODE=false found in environment, attempting to force GPU mode")

        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(1, max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    logger.info(f"Attempt {attempt}/{max_retries} to connect to {self.base_url}/health")
                    response = await client.get(f"{self.base_url}/health")
                    response.raise_for_status()
                    logger.info(f"AI service status: healthy (attempt {attempt})")
                    
                    if force_gpu_mode:
                        logger.info("GPU mode forced by environment, using real model")
                        self.fallback_mode = False
                        return True
                        
                    # Check if GPU is available via nvidia-smi
                    gpu_available = await self._check_nvidia_smi()
                    logger.info(f"GPU detected: {gpu_available}")
                    
                    if not gpu_available:
                        logger.warning("No GPU detected, using fallback mode")
                        self.fallback_mode = True
                        return False
                        
                    logger.info("AI service is healthy and GPU is available, using real model")
                    self.fallback_mode = False
                    return True
                    
            except httpx.ConnectError as e:
                logger.warning(f"Connection error on attempt {attempt}/{max_retries}: {e}")
                if "getaddrinfo failed" in str(e) or "Name or service not known" in str(e):
                    logger.warning("DNS resolution error detected - this may be a temporary network issue")
                    logger.warning(f"Check if AI service container is running at {self.base_url} and network configuration is correct")
                
                if attempt < max_retries:
                    retry_time = retry_delay * (2 ** (attempt - 1))
                    logger.info(f"Retrying in {retry_time} seconds...")
                    import asyncio
                    await asyncio.sleep(retry_time)
                else:
                    logger.error(f"All connection attempts failed after {max_retries} retries")
                    if not force_gpu_mode:
                        logger.warning("Setting fallback mode due to persistent connection issues")
                        self.fallback_mode = True
                    else:
                        logger.info("Not setting fallback mode despite connection issues due to AI_FALLBACK_MODE=false")
                        self.fallback_mode = False
                    return not self.fallback_mode
            except Exception as e:
                logger.error(f"Error checking AI service: {e}")
                if attempt < max_retries:
                    retry_time = retry_delay * (2 ** (attempt - 1))
                    logger.info(f"Retrying in {retry_time} seconds...")
                    import asyncio
                    await asyncio.sleep(retry_time)
                else:
                    logger.error(f"All health check attempts failed after {max_retries} retries: {e}")
                    if not force_gpu_mode:
                        logger.warning("Setting fallback mode due to persistent health check issues")
                        self.fallback_mode = True
                    else:
                        logger.info("Not setting fallback mode despite health check issues due to AI_FALLBACK_MODE=false")
                        self.fallback_mode = False
                    return not self.fallback_mode
        
        return not self.fallback_mode
        
    async def generate(self, prompt: str, debug: bool = False, department_id: Optional[int] = None, **kwargs) -> Union[str, Dict[str, Any]]:
        """
        Generate text using the LLM model.
        
        Args:
            prompt: The input prompt for the model
            debug: Whether to return debug information about Spanish preprocessing
            department_id: Optional department ID to use specific AI profile
            **kwargs: Additional parameters to pass to the model
            
        Returns:
            The generated text response, or a dict with response and debug info if debug=True
        """
        if not self.initialized:
            await self.initialize()
            
        parameters = {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.95,
            "do_sample": True,
            "repetition_penalty": 1.1
        }
        
        if department_id:
            try:
                from app.services.ai.department_profile_loader import get_department_ai_profile
                profile_params = await get_department_ai_profile(department_id)
                if profile_params:
                    logger.info(f"Using department-specific AI profile for department_id {department_id}")
                    parameters.update(profile_params)
            except Exception as e:
                logger.error(f"Error loading department AI profile: {e}")
        
        parameters.update(kwargs)
        
        original_prompt = prompt
        debug_info = {}
        
        transient_fallback = False
        
        should_process_spanish = (self.language_mode == "es")
        
        if not should_process_spanish:
            try:
                from app.services.ai.spanish_input_pipeline import spanish_pipeline
                should_process_spanish = spanish_pipeline.is_spanish(prompt)
                if should_process_spanish:
                    logger.info("Auto-detected Spanish text, applying Spanish preprocessing")
            except Exception as e:
                logger.warning(f"Error in Spanish language detection: {e}")
        
        if should_process_spanish:
            try:
                logger.info("Applying Spanish language preprocessing")
                if debug:
                    prompt, preprocessing_info = process_spanish_input(prompt, debug=True)
                    debug_info["spanish_preprocessing"] = preprocessing_info
                else:
                    result = process_spanish_input(prompt)
                    if isinstance(result, tuple):
                        prompt = result[0]
                    else:
                        prompt = result
                
                if prompt != original_prompt:
                    logger.info("Spanish preprocessing applied successfully")
                    logger.debug(f"Original: {original_prompt[:100]}...")
                    logger.debug(f"Processed: {prompt[:100]}...")
            except Exception as e:
                logger.error(f"Error in Spanish preprocessing: {e}, using original prompt")
                prompt = original_prompt
                debug_info["spanish_preprocessing_error"] = str(e)
        
        request = MistralRequest(
            inputs=prompt,
            parameters=parameters
        )
        
        # Check if we're in permanent fallback mode
        if self.fallback_mode:
            response_text = self._get_fallback_response(prompt)
            if debug:
                return {
                    "generated_text": response_text,
                    "is_fallback": True,
                    "debug_info": debug_info
                }
            return response_text
        
        max_retries = 2
        retry_delay = 1  # seconds
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Attempt {attempt}/{max_retries} to connect to LLM at {self.base_url}/generate")
                logger.debug(f"Request prompt: {prompt[:50]}...")
                logger.debug(f"Request parameters: {parameters}")
                
                response = await self.client.post(
                    f"{self.base_url}/generate",
                    json=request.model_dump(),  # Use model_dump() instead of dict() for Pydantic v2
                    headers={"Content-Type": "application/json"}
                )
                
                logger.info(f"Response status code: {response.status_code}")
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Response received: {str(result)[:200]}...")
                
                if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
                    logger.info("Successfully extracted generated_text from response (list format)")
                    response_text = result[0]["generated_text"]
                elif isinstance(result, dict) and "generated_text" in result:
                    logger.info("Successfully extracted generated_text from response (dict format)")
                    response_text = result["generated_text"]
                else:
                    logger.error(f"Unexpected response format: {result}")
                    if isinstance(result, dict):
                        logger.error("Response keys: " + ", ".join(result.keys()))
                    
                    if attempt < max_retries:
                        logger.warning(f"Retrying due to unexpected response format (attempt {attempt}/{max_retries})")
                        import asyncio
                        await asyncio.sleep(retry_delay)
                        continue
                    
                    transient_fallback = True
                    response_text = self._get_fallback_response(prompt)
                    break
                    
                if debug:
                    return {
                        "generated_text": response_text,
                        "is_fallback": False,
                        "debug_info": debug_info
                    }
                return response_text
                    
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error when connecting to LLM: {e.response.status_code} - {e.response.text}")
                
                if e.response.status_code >= 500:
                    logger.error(f"Server error detected (attempt {attempt}/{max_retries})")
                    
                    if attempt < max_retries:
                        retry_time = retry_delay * (2 ** (attempt - 1))
                        logger.warning(f"Retrying in {retry_time} seconds...")
                        import asyncio
                        await asyncio.sleep(retry_time)
                        continue
                    
                    if os.environ.get("AI_FALLBACK_MODE", "").lower() != "false":
                        logger.error("All server error retries failed, enabling permanent fallback mode")
                        self.fallback_mode = True
                else:
                    logger.error(f"Client error: {e.response.status_code} - {e.response.text}")
                
                transient_fallback = True
                response_text = self._get_fallback_response(prompt)
                break
                
            except httpx.ConnectError as e:
                logger.error(f"Connection error when connecting to LLM: {e}")
                logger.error(f"Attempted to connect to: {self.base_url}")
                
                if "getaddrinfo failed" in str(e) or "Name or service not known" in str(e):
                    logger.error("DNS resolution error detected. Check if AI service container is running")
                    
                    if attempt < max_retries:
                        retry_time = retry_delay * (2 ** (attempt - 1))
                        logger.warning(f"Retrying DNS resolution in {retry_time} seconds...")
                        import asyncio
                        await asyncio.sleep(retry_time)
                        continue
                    
                    if os.environ.get("AI_FALLBACK_MODE", "").lower() != "false":
                        logger.error("Persistent DNS resolution errors, enabling fallback mode")
                        self.fallback_mode = True
                else:
                    if attempt < max_retries:
                        retry_time = retry_delay * (2 ** (attempt - 1))
                        logger.warning(f"Retrying connection in {retry_time} seconds...")
                        import asyncio
                        await asyncio.sleep(retry_time)
                        continue
                    
                    logger.error("Connection error persists, using fallback for this request only")
                
                transient_fallback = True
                response_text = self._get_fallback_response(prompt)
                break
                
            except Exception as e:
                logger.error(f"Error generating text with LLM: {type(e).__name__} - {e}")
                
                if attempt < max_retries:
                    retry_time = retry_delay * (2 ** (attempt - 1))
                    logger.warning(f"Retrying after error in {retry_time} seconds...")
                    import asyncio
                    await asyncio.sleep(retry_time)
                    continue
                
                if os.environ.get("AI_FALLBACK_MODE", "").lower() != "false":
                    logger.error("Persistent errors, enabling fallback mode")
                    self.fallback_mode = True
                
                transient_fallback = True
                response_text = self._get_fallback_response(prompt)
                break
        
        if debug:
            return {
                "generated_text": response_text,
                "is_fallback": True,
                "debug_info": debug_info,
                "permanent_fallback": self.fallback_mode,
                "transient_fallback": transient_fallback
            }
        return response_text
            
    def _get_fallback_response(self, prompt: str) -> str:
        """Generate a fallback response when the AI service is unavailable."""
        fallback_note = (
            "Note: This is a fallback response. The Mistral 7B model requires GPU hardware with "
            "Flash Attention v2 support, which is not available in the current environment. "
            "For production use, consider deploying on GPU-enabled infrastructure or using a smaller model."
        )
        
        if "contract" in prompt.lower() and "what is" in prompt.lower():
            return (
                "A contract is a legally binding agreement between two or more parties that creates mutual obligations "
                "enforceable by law. It typically includes elements such as offer, acceptance, consideration, legal capacity, "
                "and lawful purpose. Contracts can be written, verbal, or implied, though written contracts provide better "
                "evidence of the terms agreed upon. " + fallback_note
            )
        elif "analyze" in prompt.lower():
            return (
                "I've analyzed the contract and found several key points to consider:\n"
                "1. The agreement contains standard indemnification clauses\n"
                "2. There are termination provisions with 30-day notice periods\n"
                "3. The governing law is specified as the jurisdiction of the client\n"
                "4. Confidentiality provisions extend 2 years beyond termination\n\n" + 
                fallback_note
            )
        elif "extract" in prompt.lower():
            return (
                "Here are the key clauses I've identified:\n"
                "1. Termination Clause: Either party may terminate with 30 days written notice\n"
                "2. Confidentiality: All information shared is confidential for 2 years post-termination\n"
                "3. Indemnification: Standard mutual indemnification for third-party claims\n"
                "4. Payment Terms: Net 30 days from invoice date\n\n" + 
                fallback_note
            )
        elif "risk" in prompt.lower():
            return (
                "I've identified some potential risks in this contract:\n"
                "1. Ambiguous performance metrics without clear measurement criteria\n"
                "2. Limited liability caps that may not adequately protect your interests\n"
                "3. Broad intellectual property assignment clauses\n"
                "4. Vague dispute resolution procedures\n\n" + 
                fallback_note
            )
        else:
            return (
                "I understand your request about legal matters. I can provide general guidance on contract analysis, "
                "risk assessment, clause extraction, and legal compliance questions. " + 
                fallback_note
            )
    
    async def analyze_contract(self, contract_text: str, query: str, debug: bool = False, department_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze a contract using the Mistral 7B model.
        
        Args:
            contract_text: The text of the contract to analyze
            query: The specific analysis query (e.g., "Extract key clauses", "Identify risks")
            debug: Whether to return debug information about Spanish preprocessing
            department_id: Optional department ID to use specific AI profile
            
        Returns:
            A dictionary containing the analysis results
        """
        max_contract_length = 3000
        if len(contract_text) > max_contract_length:
            contract_text = contract_text[:max_contract_length] + "..."
        
        original_contract_text = contract_text
        debug_info = {}
        
        should_process_spanish = (self.language_mode == "es")
        
        if not should_process_spanish:
            try:
                from app.services.ai.spanish_input_pipeline import spanish_pipeline
                should_process_spanish = spanish_pipeline.is_spanish(contract_text)
                if should_process_spanish:
                    logger.info("Auto-detected Spanish contract text, applying Spanish preprocessing")
            except Exception as e:
                logger.warning(f"Error in Spanish language detection for contract: {e}")
        
        if should_process_spanish:
            try:
                logger.info("Applying Spanish language preprocessing to contract text")
                if debug:
                    contract_text, preprocessing_info = process_spanish_input(contract_text, debug=True)
                    debug_info["contract_preprocessing"] = preprocessing_info
                else:
                    result = process_spanish_input(contract_text)
                    if isinstance(result, tuple):
                        contract_text = result[0]
                    else:
                        contract_text = result
                
                if contract_text != original_contract_text:
                    logger.info("Spanish preprocessing applied successfully to contract text")
            except Exception as e:
                logger.error(f"Error in Spanish preprocessing for contract: {e}, using original text")
                contract_text = original_contract_text
                debug_info["contract_preprocessing_error"] = str(e)
        
        original_query = query
        
        if should_process_spanish or (self.language_mode == "es"):
            try:
                logger.info("Applying Spanish language preprocessing to query")
                if debug:
                    query, query_preprocessing_info = process_spanish_input(query, debug=True)
                    debug_info["query_preprocessing"] = query_preprocessing_info
                else:
                    result = process_spanish_input(query)
                    if isinstance(result, tuple):
                        query = result[0]
                    else:
                        query = result
                
                if query != original_query:
                    logger.info("Spanish preprocessing applied successfully to query")
            except Exception as e:
                logger.error(f"Error in Spanish preprocessing for query: {e}, using original query")
                query = original_query
                debug_info["query_preprocessing_error"] = str(e)
        
        prompt = f"""You are a legal AI assistant specialized in contract analysis.

CONTRACT TEXT:
{contract_text}

TASK:
{query}

Provide your analysis in JSON format with appropriate fields based on the task.
"""
        
        try:
            if debug:
                response = await self.generate(prompt, debug=True, temperature=0.3, max_new_tokens=1024)
                if isinstance(response, dict):
                    response_text = response.get("generated_text", "")
                    debug_info.update(response.get("debug_info", {}))
                else:
                    response_text = response
            else:
                response_text = await self.generate(prompt, temperature=0.3, max_new_tokens=1024)
                if isinstance(response_text, dict):
                    response_text = response_text.get("generated_text", "")
            
            if not isinstance(response_text, str):
                response_text = str(response_text)
                
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            
            result = {}
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                try:
                    result = json.loads(json_str)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON from response: {json_str}")
                    result = {"error": "Failed to parse analysis results", "raw_response": response_text}
            else:
                result = {"analysis": response_text}
            
            if debug and isinstance(result, dict):
                result["debug_info"] = debug_info
                
            return result
                
        except Exception as e:
            logger.error(f"Error analyzing contract: {e}")
            result = {"error": str(e)}
            if debug and isinstance(result, dict):
                result["debug_info"] = debug_info
            return result
    
    async def query_legal_assistant(self, query: str, context: Optional[str] = None, debug: bool = False, department_id: Optional[int] = None) -> Union[str, Dict[str, Any]]:
        """
        Query the legal assistant with a natural language question.
        
        Args:
            query: The user's question
            context: Optional context information (e.g., relevant contract snippets)
            debug: Whether to return debug information about Spanish preprocessing
            department_id: Optional department ID to use specific AI profile
            
        Returns:
            The assistant's response, or a dict with response and debug info if debug=True
        """
        original_query = query
        debug_info = {}
        
        should_process_spanish = (self.language_mode == "es")
        
        if not should_process_spanish:
            try:
                from app.services.ai.spanish_input_pipeline import spanish_pipeline
                should_process_spanish = spanish_pipeline.is_spanish(query)
                if should_process_spanish:
                    logger.info("Auto-detected Spanish query, applying Spanish preprocessing")
            except Exception as e:
                logger.warning(f"Error in Spanish language detection for query: {e}")
        
        if should_process_spanish:
            try:
                logger.info("Applying Spanish language preprocessing to query")
                if debug:
                    query, preprocessing_info = process_spanish_input(query, debug=True)
                    debug_info["query_preprocessing"] = preprocessing_info
                else:
                    result = process_spanish_input(query)
                    if isinstance(result, tuple):
                        query = result[0]
                    else:
                        query = result
                
                if query != original_query:
                    logger.info("Spanish preprocessing applied successfully to query")
                    logger.debug(f"Original query: {original_query}")
                    logger.debug(f"Processed query: {query}")
            except Exception as e:
                logger.error(f"Error in Spanish preprocessing for query: {e}, using original query")
                query = original_query
                debug_info["query_preprocessing_error"] = str(e)
        
        if context and should_process_spanish:
            original_context = context
            try:
                logger.info("Applying Spanish language preprocessing to context")
                if debug:
                    context, context_preprocessing_info = process_spanish_input(context, debug=True)
                    debug_info["context_preprocessing"] = context_preprocessing_info
                else:
                    result = process_spanish_input(context)
                    if isinstance(result, tuple):
                        context = result[0]
                    else:
                        context = result
                
                if context != original_context:
                    logger.info("Spanish preprocessing applied successfully to context")
            except Exception as e:
                logger.error(f"Error in Spanish preprocessing for context: {e}, using original context")
                context = original_context
                debug_info["context_preprocessing_error"] = str(e)
        
        context_text = f"\nCONTEXT:\n{context}\n\n" if context else "\n"
        
        prompt = f"""You are a legal AI assistant for a contract management system.

USER QUERY:
{query}
{context_text}
Provide a helpful, accurate, and concise response based on the information available.
"""
        
        try:
            if debug:
                response = await self.generate(prompt, debug=True, department_id=department_id, temperature=0.7, max_new_tokens=512)
                if isinstance(response, dict):
                    result = response.get("generated_text", "").strip()
                    debug_info.update(response.get("debug_info", {}))
                    return {
                        "response": result,
                        "debug_info": debug_info,
                        "is_fallback": response.get("is_fallback", False)
                    }
                else:
                    result = str(response).strip()
                    return {
                        "response": result,
                        "debug_info": debug_info,
                        "is_fallback": False
                    }
            else:
                response = await self.generate(prompt, department_id=department_id, temperature=0.7, max_new_tokens=512)
                if isinstance(response, dict):
                    return response.get("generated_text", "").strip()
                else:
                    return str(response).strip()
        except Exception as e:
            logger.error(f"Error querying legal assistant: {e}")
            error_msg = f"I apologize, but I encountered an error processing your request: {str(e)}"
            if debug:
                return {
                    "response": error_msg,
                    "debug_info": debug_info,
                    "error": str(e),
                    "is_fallback": True
                }
            return error_msg

mistral_client = MistralClient()

async def check_ai_service_status() -> str:
    """
    Check the status of the AI service for health checks.
    Returns a string indicating the status of the AI service.
    """
    try:
        if not mistral_client.initialized:
            await mistral_client.initialize()
        
        gpu_available = await mistral_client._check_gpu_available()
        
        if mistral_client.fallback_mode:
            if os.environ.get("AI_FALLBACK_MODE", "").lower() == "true":
                return "fallback (forced via environment)"
            elif not gpu_available:
                return "fallback (no GPU detected)"
            else:
                return "fallback (service connection issues)"
        else:
            if os.environ.get("AI_FALLBACK_MODE", "").lower() == "false":
                return "active (forced via environment)"
            elif gpu_available:
                return "active (GPU detected)"
            else:
                return "active"
    except Exception as e:
        logger.error(f"Error checking AI service status: {e}")
        return f"error: {str(e)}"
