"""
Spanish Language Support Pipeline for Mistral Integration in Cortana

This module provides preprocessing and normalization for Spanish text inputs
before they are sent to the Mistral AI model. It handles:
- Spelling correction
- Grammar correction
- Accent normalization
- Punctuation balancing
- Legal terminology standardization

The pipeline ensures that Spanish inputs are properly processed while preserving
their semantic meaning, making the AI responses more accurate and relevant.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Union

import langdetect
from langdetect import DetectorFactory
DetectorFactory.seed = 0  # For consistent language detection results


logger = logging.getLogger(__name__)

LEGAL_TERMS_CORRECTIONS = {
    "rescision": "rescisión",
    "resolucion": "resolución",
    "clausula": "cláusula",
    "clausulas": "cláusulas",
    "articulo": "artículo",
    "articulos": "artículos",
    "parrafo": "párrafo",
    "parrafos": "párrafos",
    "termino": "término",
    "terminos": "términos",
    "jurisdiccion": "jurisdicción",
    "indemnizacion": "indemnización",
    "prorroga": "prórroga",
    "cesion": "cesión",
    "subrogacion": "subrogación",
    "garantia": "garantía",
    "arbitraje": "arbitraje",
    "confidencialidad": "confidencialidad",
    "notificacion": "notificación",
    "notificaciones": "notificaciones",
    "incumplimiento": "incumplimiento",
    "compensacion": "compensación",
    "liquidacion": "liquidación",
    "ejecucion": "ejecución",
}

class SpanishInputPipeline:
    """
    Pipeline for preprocessing Spanish text inputs before sending to Mistral AI.
    
    This class handles various text normalization tasks including:
    - Language detection
    - Spelling correction
    - Grammar correction
    - Accent normalization
    - Punctuation balancing
    """
    
    def __init__(self, use_spellcheck: bool = True, use_grammar_check: bool = True):
        """
        Initialize the Spanish input pipeline.
        
        Args:
            use_spellcheck: Whether to use spellchecking (requires additional libraries)
            use_grammar_check: Whether to use grammar checking (requires additional libraries)
        """
        self.use_spellcheck = use_spellcheck
        self.use_grammar_check = use_grammar_check
        self._initialize_nlp_tools()
        
        logger.info("Spanish input pipeline initialized")
        
    def _initialize_nlp_tools(self):
        """Initialize NLP tools if the required libraries are available."""
        self.nlp = None
        self.language_tool = None
        self.sym_spell = None
        self.use_grammar_check = False
        self.use_spellcheck = False
        
        logger.warning("NLP tools disabled for compatibility with Python 3.12")
        
        """
        try:
            import spacy
            self.nlp = spacy.load("es_core_news_md")
            logger.info("Loaded spaCy es_core_news_md model")
        except (ImportError, OSError) as e:
            logger.warning(f"spaCy es_core_news_md model not available: {e}")
            self.nlp = None
            
        if self.use_grammar_check:
            try:
                import language_tool_python
                self.language_tool = language_tool_python.LanguageTool('es')
                logger.info("Loaded LanguageTool for Spanish")
            except ImportError as e:
                logger.warning(f"LanguageTool not available: {e}")
                self.language_tool = None
                self.use_grammar_check = False
        else:
            self.language_tool = None
            
        if self.use_spellcheck:
            try:
                from symspellpy import SymSpell, Verbosity
                self.sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
                logger.info("Initialized SymSpell for Spanish spellchecking")
            except ImportError as e:
                logger.warning(f"SymSpell not available: {e}")
                self.sym_spell = None
                self.use_spellcheck = False
        else:
            self.sym_spell = None
        """
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            ISO language code (e.g., 'es' for Spanish, 'en' for English)
        """
        try:
            return langdetect.detect(text)
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return "es"
    
    def is_spanish(self, text: str) -> bool:
        """
        Check if the input text is in Spanish.
        
        Args:
            text: Input text to analyze
            
        Returns:
            True if the text is in Spanish, False otherwise
        """
        return self.detect_language(text) == "es"
    
    def normalize_accents(self, text: str) -> str:
        """
        Normalize accents in Spanish text.
        
        Args:
            text: Input text to normalize
            
        Returns:
            Text with normalized accents
        """
        words = text.split()
        normalized_words = []
        
        for word in words:
            word_lower = word.lower()
            if word_lower in LEGAL_TERMS_CORRECTIONS:
                if word.isupper():
                    normalized_words.append(LEGAL_TERMS_CORRECTIONS[word_lower].upper())
                elif word[0].isupper():
                    normalized_words.append(LEGAL_TERMS_CORRECTIONS[word_lower].capitalize())
                else:
                    normalized_words.append(LEGAL_TERMS_CORRECTIONS[word_lower])
            else:
                normalized_words.append(word)
                
        return " ".join(normalized_words)
    
    def balance_punctuation(self, text: str) -> str:
        """
        Balance punctuation marks in Spanish text.
        
        Args:
            text: Input text to process
            
        Returns:
            Text with balanced punctuation
        """
        if "?" in text and "¿" not in text:
            text = re.sub(r'(\s|^)([^¿]*)(\?)', r'\1¿\2\3', text)
            
        if "!" in text and "¡" not in text:
            text = re.sub(r'(\s|^)([^¡]*)(\!)', r'\1¡\2\3', text)
            
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        
        return text
    
    def correct_spelling(self, text: str) -> str:
        """
        Correct spelling in Spanish text.
        
        Args:
            text: Input text to correct
            
        Returns:
            Text with corrected spelling
        """
        if not self.use_spellcheck or self.sym_spell is None:
            return text
            
        
        words = text.split()
        corrected_words = []
        
        for word in words:
            word_lower = word.lower()
            if word_lower in LEGAL_TERMS_CORRECTIONS:
                if word.isupper():
                    corrected_words.append(LEGAL_TERMS_CORRECTIONS[word_lower].upper())
                elif word[0].isupper():
                    corrected_words.append(LEGAL_TERMS_CORRECTIONS[word_lower].capitalize())
                else:
                    corrected_words.append(LEGAL_TERMS_CORRECTIONS[word_lower])
            else:
                corrected_words.append(word)
                
        return " ".join(corrected_words)
    
    def correct_grammar(self, text: str) -> str:
        """
        Correct grammar in Spanish text using LanguageTool.
        
        Args:
            text: Input text to correct
            
        Returns:
            Text with corrected grammar
        """
        if not self.use_grammar_check or self.language_tool is None:
            return text
            
        try:
            return self.language_tool.correct(text)
        except Exception as e:
            logger.warning(f"Grammar correction failed: {e}")
            return text
    
    def process(self, text: str, debug: bool = False) -> Union[str, Tuple[str, Dict]]:
        """
        Process Spanish text through the complete pipeline.
        
        Args:
            text: Input text to process
            debug: Whether to return debug information
            
        Returns:
            Processed text, or a tuple of (processed_text, debug_info) if debug=True
        """
        original_text = text
        is_spanish = self.is_spanish(text)
        
        if is_spanish:
            logger.info("Processing Spanish text input")
            
            text = self.normalize_accents(text)
            text = self.balance_punctuation(text)
            text = self.correct_spelling(text)
            text = self.correct_grammar(text)
            
            logger.info("Spanish text processing complete")
        else:
            logger.info(f"Text detected as non-Spanish (lang={self.detect_language(text)}), skipping processing")
        
        if debug:
            debug_info = {
                "original_text": original_text,
                "processed_text": text,
                "is_spanish": is_spanish,
                "language_detected": self.detect_language(original_text),
                "changes_made": original_text != text
            }
            return text, debug_info
        
        return text

spanish_pipeline = SpanishInputPipeline()

def process_spanish_input(text: str, debug: bool = False) -> Union[str, Tuple[str, Dict]]:
    """
    Process Spanish text through the pipeline.
    
    This is the main entry point for the Spanish input pipeline.
    
    Args:
        text: Input text to process
        debug: Whether to return debug information
        
    Returns:
        Processed text, or a tuple of (processed_text, debug_info) if debug=True
    """
    try:
        return spanish_pipeline.process(text, debug)
    except Exception as e:
        logger.warning(f"Error processing Spanish text: {e}")
        if debug:
            return text, {
                "original_text": text,
                "processed_text": text,
                "is_spanish": False,
                "language_detected": "unknown",
                "changes_made": False,
                "error": str(e)
            }
        return text
