"""
Unit tests for the Spanish language preprocessing pipeline.
"""
import unittest
from app.services.ai.spanish_input_pipeline import process_spanish_input, spanish_pipeline

class TestSpanishPipeline(unittest.TestCase):
    """Test cases for the Spanish language preprocessing pipeline."""
    
    def test_language_detection(self):
        """Test that the pipeline correctly detects Spanish language."""
        spanish_text = "Este es un texto en español con algunas palabras."
        self.assertTrue(spanish_pipeline.is_spanish(spanish_text))
        
        english_text = "This is an English text with some words."
        self.assertFalse(spanish_pipeline.is_spanish(english_text))
        
        mixed_text = "This is mostly English pero tiene algunas palabras en español."
        self.assertFalse(spanish_pipeline.is_spanish(mixed_text))
        
        mixed_text_spanish = "Este texto está principalmente en español but has some English words."
        self.assertTrue(spanish_pipeline.is_spanish(mixed_text_spanish))
    
    def test_accent_normalization(self):
        """Test that the pipeline correctly normalizes accents in Spanish text."""
        text_without_accents = "clausula de terminacion y resolucion"
        processed = spanish_pipeline.normalize_accents(text_without_accents)
        self.assertEqual(processed, "cláusula de terminación y resolución")
        
        text_with_accents = "cláusula de terminación y resolución"
        processed = spanish_pipeline.normalize_accents(text_with_accents)
        self.assertEqual(processed, text_with_accents)
        
        mixed_case = "CLAUSULA de Terminacion"
        processed = spanish_pipeline.normalize_accents(mixed_case)
        self.assertEqual(processed, "CLÁUSULA de Terminación")
    
    def test_punctuation_balancing(self):
        """Test that the pipeline correctly balances punctuation in Spanish text."""
        text_with_missing_question = "Como estas?"
        processed = spanish_pipeline.balance_punctuation(text_with_missing_question)
        self.assertEqual(processed, "¿Como estas?")
        
        text_with_missing_exclamation = "Que sorpresa!"
        processed = spanish_pipeline.balance_punctuation(text_with_missing_exclamation)
        self.assertEqual(processed, "¡Que sorpresa!")
        
        balanced_text = "¿Cómo estás? ¡Qué sorpresa!"
        processed = spanish_pipeline.balance_punctuation(balanced_text)
        self.assertEqual(processed, balanced_text)
        
        text_with_spaces = "Hola , ¿cómo estás ?"
        processed = spanish_pipeline.balance_punctuation(text_with_spaces)
        self.assertEqual(processed, "Hola, ¿cómo estás?")
    
    def test_legal_terminology(self):
        """Test that the pipeline correctly handles legal terminology."""
        legal_text = "La rescision del contrato requiere notificacion previa según el articulo 15."
        processed = spanish_pipeline.normalize_accents(legal_text)
        self.assertEqual(
            processed, 
            "La rescisión del contrato requiere notificación previa según el artículo 15."
        )
        
        legal_text_caps = "RESCISION DEL CONTRATO"
        processed = spanish_pipeline.normalize_accents(legal_text_caps)
        self.assertEqual(processed, "RESCISIÓN DEL CONTRATO")
    
    def test_full_pipeline_processing(self):
        """Test the complete pipeline processing with various inputs."""
        input_text = "clausula de terminacion: La rescision del contrato requiere notificacion previa de 30 dias."
        processed, debug_info = process_spanish_input(input_text, debug=True)
        
        self.assertIn("cláusula de terminación", processed)
        self.assertIn("rescisión", processed)
        self.assertIn("notificación", processed)
        self.assertTrue(debug_info["is_spanish"])
        self.assertTrue(debug_info["changes_made"])
        
        correct_text = "La cláusula de terminación establece que la rescisión del contrato requiere notificación previa."
        processed, debug_info = process_spanish_input(correct_text, debug=True)
        
        self.assertEqual(processed, correct_text)
        self.assertTrue(debug_info["is_spanish"])
        self.assertFalse(debug_info["changes_made"])
        
        english_text = "The termination clause states that contract rescission requires prior notification."
        processed, debug_info = process_spanish_input(english_text, debug=True)
        
        self.assertEqual(processed, english_text)
        self.assertFalse(debug_info["is_spanish"])
        self.assertFalse(debug_info["changes_made"])
    
    def test_error_handling(self):
        """Test that the pipeline gracefully handles errors."""
        try:
            result = process_spanish_input(None)
            self.assertEqual(result, None)
        except Exception as e:
            self.fail(f"process_spanish_input raised {type(e).__name__} unexpectedly!")
        
        result = process_spanish_input("")
        self.assertEqual(result, "")

if __name__ == "__main__":
    unittest.main()
