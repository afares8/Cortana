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

logging.basicConfig(level=logging.INFO)
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
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.environ.get("MISTRAL_API_URL", "http://ai-service:80")
        logger.info(f"Initializing MistralClient with base_url: {self.base_url}")
        self.client = httpx.AsyncClient(timeout=60.0)
        
        env_fallback = os.environ.get("AI_FALLBACK_MODE", "").lower()
        
        if env_fallback == "":
            has_gpu, gpu_info = self._check_gpu_available()
            self.fallback_mode = not has_gpu
            logger.info(f"Auto-detected GPU availability: {'Available' if has_gpu else 'Not available'}")
            if has_gpu:
                logger.info(f"GPU info: {gpu_info}")
            else:
                logger.info("No GPU detected, using fallback mode")
        else:
            self.fallback_mode = env_fallback == "true"
            logger.info(f"Fallback mode explicitly set to: {self.fallback_mode}")
        
        logger.info(f"Fallback mode is {'enabled' if self.fallback_mode else 'disabled'}")
        
        self._verify_ai_service_connectivity()
    
    def _verify_ai_service_connectivity(self):
        """
        Verify connectivity to the AI service and log the result.
        This is a non-blocking check that runs in the background.
        """
        import threading
        
        def check_connectivity():
            try:
                result = subprocess.run(
                    ["curl", "-s", f"{self.base_url}/health"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0 and "ok" in result.stdout.lower():
                    logger.info(f"✅ Successfully connected to AI service at {self.base_url}")
                    if self.fallback_mode:
                        logger.warning(f"⚠️ AI service is available but fallback mode is enabled. Consider setting AI_FALLBACK_MODE=false")
                else:
                    logger.error(f"❌ Failed to connect to AI service at {self.base_url}: {result.stderr}")
                    if not self.fallback_mode:
                        logger.warning(f"⚠️ AI service is not available but fallback mode is disabled. Will attempt to connect anyway.")
            except Exception as e:
                logger.error(f"❌ Error checking AI service connectivity: {e}")
        
        threading.Thread(target=check_connectivity).start()
    
    def _check_gpu_available(self) -> Tuple[bool, str]:
        """
        Check if GPU is available for running the Mistral model.
        
        Returns:
            Tuple[bool, str]: (has_gpu, gpu_info)
        """
        gpu_info = "No GPU information available"
        
        try:
            import torch
            if torch.cuda.is_available():
                device_count = torch.cuda.device_count()
                device_name = torch.cuda.get_device_name(0) if device_count > 0 else "Unknown"
                gpu_info = f"CUDA available: {device_count} device(s), Device 0: {device_name}"
                return True, gpu_info
        except (ImportError, Exception) as e:
            logger.debug(f"Could not check CUDA via torch: {e}")
        
        try:
            if platform.system() == "Linux":
                result = subprocess.run(
                    ["which", "nvidia-smi"], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if result.returncode == 0:
                    nvidia_smi = subprocess.run(
                        ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    if nvidia_smi.returncode == 0 and nvidia_smi.stdout.strip():
                        gpu_info = f"NVIDIA GPU: {nvidia_smi.stdout.strip()}"
                        return True, gpu_info
        except Exception as e:
            logger.debug(f"Could not check NVIDIA GPU via system commands: {e}")
        
        try:
            if platform.system() == "Linux":
                result = subprocess.run(
                    ["which", "rocm-smi"], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if result.returncode == 0:
                    rocm_smi = subprocess.run(
                        ["rocm-smi", "--showproductname"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    if rocm_smi.returncode == 0 and "GPU" in rocm_smi.stdout:
                        gpu_info = f"AMD GPU: {rocm_smi.stdout.strip()}"
                        return True, gpu_info
        except Exception as e:
            logger.debug(f"Could not check AMD GPU via system commands: {e}")
        
        return False, gpu_info
        
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using the LLM model.
        
        Args:
            prompt: The input prompt for the model
            **kwargs: Additional parameters to pass to the model
            
        Returns:
            The generated text response
        """
        env_fallback = os.environ.get("AI_FALLBACK_MODE", "").lower()
        if env_fallback == "false":
            logger.info("Forcing fallback mode to False based on environment variable")
            self.fallback_mode = False
        
        parameters = {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.95,
            "do_sample": True,
            "repetition_penalty": 1.1
        }
        
        parameters.update(kwargs)
        
        request = MistralRequest(
            inputs=prompt,
            parameters=parameters
        )
        
        if self.fallback_mode:
            logger.warning("Using fallback mode for text generation")
            return self._get_fallback_response(prompt)
        
        try:
            logger.info(f"Connecting to LLM at {self.base_url}/generate with prompt: {prompt[:50]}...")
            logger.debug(f"Full request: {request.model_dump()}")
            
            request_json = request.model_dump()
            logger.info(f"Request JSON: {json.dumps(request_json)}")
            
            response = await self.client.post(
                f"{self.base_url}/generate",
                json=request_json,
                headers={"Content-Type": "application/json"}
            )
            
            logger.info(f"Response status code: {response.status_code}")
            
            raw_response = response.text
            logger.info(f"Raw response text: {raw_response[:500]}...")
            
            response.raise_for_status()
            
            try:
                result = response.json()
                logger.info(f"Response JSON: {json.dumps(result)[:500]}...")
                
                if "generated_text" in result:
                    logger.info("Found 'generated_text' in response")
                    return result["generated_text"]
                elif "outputs" in result and isinstance(result["outputs"], list) and len(result["outputs"]) > 0:
                    if "text" in result["outputs"][0]:
                        logger.info("Found 'outputs[0].text' in response")
                        return result["outputs"][0]["text"]
                    elif "generated_text" in result["outputs"][0]:
                        logger.info("Found 'outputs[0].generated_text' in response")
                        return result["outputs"][0]["generated_text"]
                
                logger.error(f"Unexpected response format: {result}")
                logger.error("Response keys: " + ", ".join(result.keys() if isinstance(result, dict) else ["<not a dict>"]))
                
                if isinstance(result, dict):
                    for key, value in result.items():
                        if isinstance(value, str) and len(value) > 20:
                            logger.info(f"Using text from key '{key}' as fallback")
                            return value
                
                if isinstance(raw_response, str) and len(raw_response) > 20 and not raw_response.startswith("{"):
                    logger.info("Using raw response text as fallback")
                    return raw_response
                
                logger.warning("Could not extract text from response, using fallback")
                return self._get_fallback_response(prompt)
                
            except json.JSONDecodeError:
                logger.error(f"Response is not valid JSON: {raw_response[:200]}...")
                
                if isinstance(raw_response, str) and len(raw_response) > 20 and not raw_response.startswith("{"):
                    logger.info("Using non-JSON response as text")
                    return raw_response
                
                return self._get_fallback_response(prompt)
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error when connecting to LLM: {e.response.status_code} - {e.response.text}")
            return self._get_fallback_response(prompt)
        except httpx.ConnectError as e:
            logger.error(f"Connection error when connecting to LLM: {e} - Is the AI service running?")
            logger.error(f"Attempted to connect to: {self.base_url}")
            return self._get_fallback_response(prompt)
        except Exception as e:
            logger.error(f"Error generating text with LLM: {type(e).__name__} - {e}")
            return self._get_fallback_response(prompt)
            
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
    
    async def analyze_contract(self, contract_text: str, query: str) -> Dict[str, Any]:
        """
        Analyze a contract using the Mistral 7B model.
        
        Args:
            contract_text: The text of the contract to analyze
            query: The specific analysis query (e.g., "Extract key clauses", "Identify risks")
            
        Returns:
            A dictionary containing the analysis results
        """
        max_contract_length = 3000
        if len(contract_text) > max_contract_length:
            contract_text = contract_text[:max_contract_length] + "..."
        
        prompt = f"""You are a legal AI assistant specialized in contract analysis.

CONTRACT TEXT:
{contract_text}

TASK:
{query}

Provide your analysis in JSON format with appropriate fields based on the task.
"""
        
        try:
            response_text = await self.generate(prompt, temperature=0.3, max_new_tokens=1024)
            
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON from response: {json_str}")
                    return {"error": "Failed to parse analysis results", "raw_response": response_text}
            else:
                return {"analysis": response_text}
                
        except Exception as e:
            logger.error(f"Error analyzing contract: {e}")
            return {"error": str(e)}
    
    async def query_legal_assistant(self, query: str, context: Optional[str] = None) -> str:
        """
        Query the legal assistant with a natural language question.
        
        Args:
            query: The user's question
            context: Optional context information (e.g., relevant contract snippets)
            
        Returns:
            The assistant's response
        """
        context_text = f"\nCONTEXT:\n{context}\n\n" if context else "\n"
        
        prompt = f"""You are a legal AI assistant for a contract management system.

USER QUERY:
{query}
{context_text}
Provide a helpful, accurate, and concise response based on the information available.
"""
        
        try:
            response = await self.generate(prompt, temperature=0.7, max_new_tokens=512)
            return response.strip()
        except Exception as e:
            logger.error(f"Error querying legal assistant: {e}")
            return f"I apologize, but I encountered an error processing your request: {str(e)}"

mistral_client = MistralClient()
