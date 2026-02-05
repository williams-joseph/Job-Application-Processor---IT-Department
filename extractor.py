"""
Document extraction module for ECOWAS Application Processor.
Handles PDF, DOCX, and OCR-based text extraction.
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from docx import Document
except ImportError:
    Document = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None


from config import TESSERACT_PATH

if pytesseract and os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


class FieldExtractor:
    """Extracts structured data from application forms."""
    
    # Regex patterns for field extraction
    PATTERNS = {
        'name': [
            r'(?:Full\s+)?Name\s*:?\s*([A-Z][a-zA-Z\s\'-]+(?:[A-Z][a-zA-Z\s\'-]+)*)',
            r'Applicant\s+Name\s*:?\s*([A-Z][a-zA-Z\s\'-]+)',
            r'Surname\s*:?\s*([A-Z][a-zA-Z\s\'-]+)\s+(?:First|Other)\s+Name\s*:?\s*([A-Z][a-zA-Z\s\'-]+)',
        ],
        'dob': [
            r'(?:Date\s+of\s+Birth|DOB|Birth\s+Date)\s*:?\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})',
            r'(?:Date\s+of\s+Birth|DOB|Birth\s+Date)\s*:?\s*(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
        ],
        'qualification': [
            r'(?:Highest\s+)?Qualification\s*:?\s*([A-Z][a-zA-Z\s\.,\(\)]+?)(?:\n|Date|Year)',
            r'Educational\s+Qualification\s*:?\s*([A-Z][a-zA-Z\s\.,\(\)]+?)(?:\n|Date|Year)',
            r'(?:BSc|MSc|PhD|BA|MA|HND|OND|SSCE)\s*(?:in\s+)?([A-Za-z\s]+)',
        ],
        'nationality': [
            r'Nationality\s*:?\s*([A-Z][a-zA-Z\s]+?)(?:\n|Sex|Gender|Date)',
            r'Country\s+of\s+Citizenship\s*:?\s*([A-Z][a-zA-Z\s]+)',
        ],
        'sex': [
            r'(?:Sex|Gender)\s*:?\s*(Male|Female|M|F)\b',
        ],
    }
    
    def __init__(self):
        self.confidence_threshold = 0.5
    
    def extract_from_file(self, file_path: str) -> Dict:
        """
        Extract text and parse fields from a document file.
        
        Args:
            file_path: Path to the application form
            
        Returns:
            Dictionary with extracted fields and metadata
        """
        file_path = Path(file_path)
        
        result = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'extraction_status': 'success',
            'error_message': None,
            'fields': {},
            'confidence_scores': {},
            'raw_text': None,
        }
        
        try:
            # Extract text based on file type
            if file_path.suffix.lower() == '.pdf':
                text = self._extract_pdf(file_path)
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                text = self._extract_docx(file_path)
            elif file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                text = self._extract_image(file_path)
            else:
                result['extraction_status'] = 'unsupported'
                result['error_message'] = f"Unsupported file type: {file_path.suffix}"
                return result
            
            if not text or len(text.strip()) < 10:
                result['extraction_status'] = 'failed'
                result['error_message'] = "No text extracted from document"
                return result
            
            result['raw_text'] = text
            
            # Parse fields from extracted text
            parsed_fields = self._parse_fields(text)
            result['fields'] = parsed_fields['fields']
            result['confidence_scores'] = parsed_fields['confidence']
            
        except Exception as e:
            result['extraction_status'] = 'error'
            result['error_message'] = str(e)
        
        return result
    
    def _extract_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        if not pdfplumber:
            raise ImportError("pdfplumber not installed")
        
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        # If no text extracted, try OCR
        if not text.strip() and pytesseract:
            text = self._extract_pdf_with_ocr(file_path)
        
        return text
    
    def _extract_pdf_with_ocr(self, file_path: Path) -> str:
        """Extract text from PDF using OCR."""
        if not pytesseract or not Image:
            return ""
        
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # Convert page to image
                img = page.to_image(resolution=300)
                pil_img = img.original
                # OCR the image
                page_text = pytesseract.image_to_string(pil_img)
                text += page_text + "\n"
        
        return text
    
    def _extract_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file."""
        if not Document:
            raise ImportError("python-docx not installed")
        
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        
        # Also extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text += " " + cell.text
            text += "\n"
        
        return text
    
    def _extract_image(self, file_path: Path) -> str:
        """Extract text from image using OCR."""
        if not pytesseract or not Image:
            raise ImportError("pytesseract and Pillow not installed")
        
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        return text
    
    def _parse_fields(self, text: str) -> Dict:
        """
        Parse structured fields from extracted text.
        
        Args:
            text: Raw text from document
            
        Returns:
            Dictionary with fields and confidence scores
        """
        fields = {
            'Name': '',
            'Date of Birth': '',
            'Qualification': '',
            'Nationality': '',
            'Sex': '',
        }
        
        confidence = {
            'Name': 0.0,
            'Date of Birth': 0.0,
            'Qualification': 0.0,
            'Nationality': 0.0,
            'Sex': 0.0,
        }
        
        # Extract Name
        name_match = self._find_best_match(text, self.PATTERNS['name'])
        if name_match:
            fields['Name'] = name_match[0].strip()
            confidence['Name'] = 0.9 if len(fields['Name'].split()) >= 2 else 0.6
        
        # Extract Date of Birth
        dob_match = self._find_best_match(text, self.PATTERNS['dob'])
        if dob_match:
            dob_text = dob_match[0].strip()
            normalized_dob = self._normalize_date(dob_text)
            if normalized_dob:
                fields['Date of Birth'] = normalized_dob
                confidence['Date of Birth'] = 0.9
            else:
                fields['Date of Birth'] = dob_text
                confidence['Date of Birth'] = 0.5
        
        # Extract Qualification
        qual_match = self._find_best_match(text, self.PATTERNS['qualification'])
        if qual_match:
            fields['Qualification'] = qual_match[0].strip()
            confidence['Qualification'] = 0.8
        
        # Extract Nationality
        nat_match = self._find_best_match(text, self.PATTERNS['nationality'])
        if nat_match:
            fields['Nationality'] = nat_match[0].strip()
            confidence['Nationality'] = 0.9
        
        # Extract Sex
        sex_match = self._find_best_match(text, self.PATTERNS['sex'])
        if sex_match:
            sex_value = sex_match[0].strip().upper()
            # Normalize to Male/Female
            if sex_value in ['M', 'MALE']:
                fields['Sex'] = 'Male'
            elif sex_value in ['F', 'FEMALE']:
                fields['Sex'] = 'Female'
            else:
                fields['Sex'] = sex_value
            confidence['Sex'] = 0.95
        
        return {
            'fields': fields,
            'confidence': confidence,
        }
    
    def _find_best_match(self, text: str, patterns: list) -> Optional[Tuple]:
        """Try multiple patterns and return the best match."""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.groups()
        return None
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date to standard format (YYYY-MM-DD)."""
        date_formats = [
            '%d-%m-%Y', '%d/%m/%Y', '%d.%m.%Y',
            '%d-%m-%y', '%d/%m/%y', '%d.%m.%y',
            '%d %B %Y', '%d %b %Y',
            '%Y-%m-%d', '%Y/%m/%d',
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def validate_fields(self, fields: Dict) -> Dict[str, bool]:
        """
        Validate extracted fields.
        
        Returns:
            Dictionary mapping field names to validation status
        """
        validation = {}
        
        # Name validation
        validation['Name'] = bool(fields.get('Name')) and len(fields['Name'].split()) >= 2
        
        # DOB validation
        dob = fields.get('Date of Birth', '')
        validation['Date of Birth'] = bool(dob) and (
            re.match(r'\d{4}-\d{2}-\d{2}', dob) or
            re.match(r'\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}', dob)
        )
        
        # Qualification validation
        validation['Qualification'] = bool(fields.get('Qualification'))
        
        # Nationality validation
        validation['Nationality'] = bool(fields.get('Nationality'))
        
        # Sex validation
        sex = fields.get('Sex', '')
        validation['Sex'] = sex in ['Male', 'Female', 'M', 'F']
        
        return validation
