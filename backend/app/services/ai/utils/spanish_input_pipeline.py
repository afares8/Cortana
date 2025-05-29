import re
import logging
from typing import Dict, List, Optional, Set, Tuple, Union
import unicodedata
from langdetect import detect, LangDetectException

logger = logging.getLogger(__name__)

def process_spanish_input(text: str, debug: bool = False) -> Union[str, Tuple[str, Dict]]:
    """
    Process Spanish text input before sending to AI models.
    
    Args:
        text: Input text to process
        debug: Whether to return debug information
        
    Returns:
        Processed text with standardized terminology and formatting,
        or a tuple of (processed_text, debug_info) if debug=True
    """
    pipeline = SpanishInputPipeline()
    is_spanish = pipeline.is_spanish(text)
    
    if is_spanish:
        processed_text = pipeline.preprocess(text)
    else:
        processed_text = text
        
    if debug:
        debug_info = {
            "original_text": text,
            "processed_text": processed_text,
            "is_spanish": is_spanish,
            "changes_made": text != processed_text
        }
        return processed_text, debug_info
        
    return processed_text

class SpanishInputPipeline:
    """
    Pipeline for preprocessing Spanish text input before sending to AI models.
    
    This pipeline handles:
    1. Language detection
    2. Accent normalization
    3. Punctuation balancing
    4. Legal terminology standardization
    """
    
    def __init__(self):
        self.legal_terms_mapping = {
            "clausula": "cláusula",
            "articulo": "artículo",
            "parrafo": "párrafo",
            "termino": "término",
            "juridico": "jurídico",
            "juridica": "jurídica",
            "codigo": "código",
            "cesion": "cesión",
            "resolucion": "resolución",
            "indemnizacion": "indemnización",
            "prorroga": "prórroga",
            "credito": "crédito",
            "deposito": "depósito",
            "pagare": "pagaré",
            "garantia": "garantía",
            
            "contrato": "contrato",
            "acuerdo": "acuerdo",
            "parte": "parte",
            "partes": "partes",
            "confidencialidad": "confidencialidad",
            "terminacion": "terminación",
            "rescision": "rescisión",
            "jurisdiccion": "jurisdicción",
            "arbitraje": "arbitraje",
            "obligacion": "obligación",
            "obligaciones": "obligaciones",
            "incumplimiento": "incumplimiento",
            "fuerza mayor": "fuerza mayor",
            "caso fortuito": "caso fortuito",
            "notificacion": "notificación",
            "notificaciones": "notificaciones",
            "vigencia": "vigencia",
            "renovacion": "renovación",
            "automatica": "automática",
            "penalizacion": "penalización",
            "multa": "multa",
            "sancion": "sanción",
        }
    
    def is_spanish(self, text: str) -> bool:
        """
        Detect if the input text is in Spanish.
        """
        try:
            if re.search(r'[áéíóúüñ¿¡]', text, re.IGNORECASE):
                return True
            
            spanish_words = {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'y', 'o', 
                            'pero', 'porque', 'cuando', 'como', 'donde', 'quien', 'que', 'cual'}
            
            words = set(re.findall(r'\b\w+\b', text.lower()))
            if len(words.intersection(spanish_words)) >= 2:
                return True
            
            lang = detect(text)
            return lang == 'es'
        except LangDetectException:
            text_lower = text.lower()
            for term in self.legal_terms_mapping.keys():
                if term in text_lower:
                    return True
            
            return False
    
    def preprocess(self, text: str) -> str:
        """
        Preprocess Spanish text for better AI model understanding.
        """
        text = re.sub(r'\s+', ' ', text).strip()
        
        text = self._restore_accents(text)
        
        text = self._balance_punctuation(text)
        
        text = self._standardize_legal_terms(text)
        
        return text
    
    def _restore_accents(self, text: str) -> str:
        """
        Restore missing accents in Spanish text.
        """
        words = re.findall(r'\b\w+\b', text)
        for word in words:
            word_lower = word.lower()
            if word_lower in self.legal_terms_mapping:
                if word.isupper():
                    replacement = self.legal_terms_mapping[word_lower].upper()
                elif word[0].isupper():
                    replacement = self.legal_terms_mapping[word_lower].capitalize()
                else:
                    replacement = self.legal_terms_mapping[word_lower]
                
                text = re.sub(r'\b' + re.escape(word) + r'\b', replacement, text)
        
        return text
    
    def _balance_punctuation(self, text: str) -> str:
        """
        Balance Spanish punctuation, especially question and exclamation marks.
        """
        if '?' in text and '¿' not in text:
            for match in re.finditer(r'(?<!\¿)[^.!¡¿?]*\?', text):
                question = match.group(0)
                if len(question.split()) > 1:
                    replacement = '¿' + question
                    text = text.replace(question, replacement)
        
        if '!' in text and '¡' not in text:
            for match in re.finditer(r'(?<!\¡)[^.?¡¿!]*\!', text):
                exclamation = match.group(0)
                if len(exclamation.split()) > 1:
                    replacement = '¡' + exclamation
                    text = text.replace(exclamation, replacement)
        
        return text
    
    def _standardize_legal_terms(self, text: str) -> str:
        """
        Standardize legal terminology in Spanish text.
        """
        
        variations = {
            r'\bclaus[uú]las?\b': 'cláusula',
            r'\bart[ií]culos?\b': 'artículo',
            r'\bp[aá]rrafos?\b': 'párrafo',
            r'\bt[eé]rminos?\b': 'término',
            r'\bjur[ií]dicos?\b': 'jurídico',
            r'\bc[oó]digos?\b': 'código',
            r'\bces[ií][oó]n\b': 'cesión',
            r'\bresoluci[oó]n\b': 'resolución',
            r'\bindemnizaci[oó]n\b': 'indemnización',
            r'\bpr[oó]rroga\b': 'prórroga',
            r'\bcr[eé]dito\b': 'crédito',
            r'\bdep[oó]sito\b': 'depósito',
            r'\bpagar[eé]\b': 'pagaré',
            r'\bgarant[ií]a\b': 'garantía',
        }
        
        for pattern, replacement in variations.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text

spanish_pipeline = SpanishInputPipeline()
