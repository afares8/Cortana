import re
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import easyocr
from fastapi import UploadFile
import tempfile
import os

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        self.reader = easyocr.Reader(['en', 'es'])
    
    async def extract_id_data(self, file: UploadFile) -> Dict[str, Any]:
        """
        Extract identification data from uploaded document using OCR.
        Returns extracted fields or fallback data if OCR fails.
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                results = self.reader.readtext(temp_file_path)
                text_blocks = [result[1] for result in results]
                full_text = ' '.join(text_blocks)
                
                logger.info(f"OCR extracted text: {full_text}")
                
                extracted_data = self._parse_extracted_text(full_text)
                
                return {
                    "success": True,
                    "data": extracted_data,
                    "raw_text": full_text
                }
                
            finally:
                os.unlink(temp_file_path)
                
        except Exception as e:
            logger.error(f"OCR processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": self._get_fallback_data()
            }
    
    def _parse_extracted_text(self, text: str) -> Dict[str, Optional[str]]:
        """Parse extracted text to find name, DOB, and ID number using regex patterns."""
        
        result = {
            "name": None,
            "dob": None,
            "id_number": None
        }
        
        id_patterns = [
            r'[A-Z]{1,2}-\d{1,2}-\d{4,8}',  # E-8-123456, PE-12-345678
            r'\d{1,2}-\d{3,4}-\d{4,6}',     # 8-123-456789
            r'[A-Z]{2}\d{6,10}'             # PE12345678
        ]
        
        for pattern in id_patterns:
            match = re.search(pattern, text)
            if match:
                result["id_number"] = match.group()
                break
        
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{4}',  # DD/MM/YYYY or DD-MM-YYYY
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',  # YYYY/MM/DD or YYYY-MM-DD
            r'\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}'  # DD Month YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                date_str = match.group()
                result["dob"] = self._normalize_date(date_str)
                break
        
        exclude_words = {
            'REPUBLICA', 'PANAMA', 'CEDULA', 'IDENTIDAD', 'PASSPORT', 'PASAPORTE',
            'DOCUMENTO', 'NACIONAL', 'PERSONAL', 'IDENTIFICATION', 'CARD',
            'FECHA', 'NACIMIENTO', 'BIRTH', 'DATE', 'SEXO', 'SEX', 'NACIONALIDAD'
        }
        
        name_pattern = r'\b[A-Z][A-Z\s]{2,30}\b'
        name_matches = re.findall(name_pattern, text)
        
        for match in name_matches:
            words = match.strip().split()
            if len(words) >= 2 and not any(word in exclude_words for word in words):
                result["name"] = match.strip()
                break
        
        return result
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM-DD format."""
        try:
            formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d', '%Y-%m-%d']
            
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            return date_str
            
        except Exception:
            return date_str
    
    def _get_fallback_data(self) -> Dict[str, Optional[str]]:
        """Return empty fallback data when OCR fails."""
        return {
            "name": None,
            "dob": None,
            "id_number": None
        }

ocr_service = OCRService()
