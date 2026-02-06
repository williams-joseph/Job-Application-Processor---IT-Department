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
        'nationality': [
            r'Nationality\s*:?\s*([A-Z][a-zA-Z\s]+?)(?:\n|Sex|Gender|Date)',
            r'Country\s+of\s+Citizenship\s*:?\s*([A-Z][a-zA-Z\s]+)',
        ],
        'gender': [
            r'(?:Sex|Gender)\s*:?\s*(Male|Female|M|F)\b',
        ],
        'exp_start': [
            r'(?:Experience\s+Start|Work\s+Start|Started\s+Work)\s*:?\s*(\d{4})',
            r'(?:Earliest|First)\s+Employment\s*:?\s*(\d{4})',
            r'(?:Experience|Employment)\s+History\s+since\s*:?\s*(\d{4})',
        ]
    }
    
    def __init__(self):
        self.confidence_threshold = 0.5
        from config import DEFAULT_POSITION_CODE, DEFAULT_INT_EXT
        self.default_position_code = DEFAULT_POSITION_CODE
        self.default_int_ext = DEFAULT_INT_EXT
    
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
        current_year = datetime.now().year
        
        fields = {
            'NAME': '',
            'POSITION CODE': self.default_position_code,
            'GENDER': '',
            'INT/EXT': self.default_int_ext,
            'DOB': '',
            'AGE': '',
            'NATIONALITY': '',
            'EXP START (YEAR)': '',
            'EXPERIENCE(Years)': '',
            'QUALIFICATIONS': '',
        }
        
        confidence = {k: 0.0 for k in fields.keys()}
        confidence['POSITION CODE'] = 1.0
        confidence['INT/EXT'] = 1.0
        
        # Extract Name
        name_match = self._find_best_match(text, self.PATTERNS['name'])
        if name_match:
            fields['NAME'] = name_match[0].strip()
            confidence['NAME'] = 0.9 if len(fields['NAME'].split()) >= 2 else 0.6
        
        # Extract Date of Birth
        dob_match = self._find_best_match(text, self.PATTERNS['dob'])
        if dob_match:
            dob_text = dob_match[0].strip()
            normalized_dob = self._normalize_date(dob_text)
            if normalized_dob:
                fields['DOB'] = normalized_dob
                confidence['DOB'] = 0.9
                
                # Calculate AGE
                try:
                    birth_date = datetime.strptime(normalized_dob, '%Y-%m-%d')
                    fields['AGE'] = current_year - birth_date.year
                    confidence['AGE'] = 0.9
                except Exception:
                    pass
            else:
                fields['DOB'] = dob_text
                confidence['DOB'] = 0.5
        
        # Extract Experience Start Year
        exp_match = self._find_best_match(text, self.PATTERNS['exp_start'])
        if exp_match:
            try:
                start_year = int(exp_match[0])
                fields['EXP START (YEAR)'] = start_year
                fields['EXPERIENCE(Years)'] = current_year - start_year
                confidence['EXP START (YEAR)'] = 0.8
                confidence['EXPERIENCE(Years)'] = 0.8
            except ValueError:
                pass
        else:
            # Try to find years in text that seem like work start years
            years = re.findall(r'\b(19|20)\d{2}\b', text)
            if years:
                # Often work history is listed after education. 
                # Education years are often earlier. Work start might be the oldest year after graduation.
                # Simplification: let's pick the one explicitly labeled or just leave blank if uncertain.
                pass

        # Extract Qualifications (Special Multiline Format)
        quals = self._extract_multiline_qualifications(text)
        if quals:
            fields['QUALIFICATIONS'] = quals
            confidence['QUALIFICATIONS'] = 0.8
        
        # Extract Nationality
        nat_match = self._find_best_match(text, self.PATTERNS['nationality'])
        if nat_match:
            fields['NATIONALITY'] = nat_match[0].strip()
            confidence['NATIONALITY'] = 0.9
        
        # Extract Gender
        gender_match = self._find_best_match(text, self.PATTERNS['gender'])
        if gender_match:
            gender_value = gender_match[0].strip().upper()
            if gender_value in ['M', 'MALE']:
                fields['GENDER'] = 'M'
            elif gender_value in ['F', 'FEMALE']:
                fields['GENDER'] = 'F'
            else:
                fields['GENDER'] = gender_value
            confidence['GENDER'] = 0.95
        
        return {
            'fields': fields,
            'confidence': confidence,
        }

    def _extract_multiline_qualifications(self, text: str) -> str:
        """
        Extract qualifications and format them as:
        Masters Degree MBA - 2023
        B.sc Business Administration - 2017
        ...
        """
        qual_list = []
        
        # Keywords for degrees and diplomas
        degree_keywords = [
            'PhD', 'Doctorate', 'Master', 'Masters', 'MBA', 'MSc', 'MA', 
            'Bachelor', 'B.sc', 'BSc', 'B.A', 'BA', 'Degree',
            'Diploma', 'HND', 'OND', 'SSCE', 'WAEC', 'WEAC', 
            'School Certificate', 'Certificate'
        ]
        
        # Pattern to find a degree and a year near it
        # Example: "B.sc Business Administration (2017)" or "MSc MBA - 2023"
        # We'll look for lines or segments containing keywords and a 4-digit year
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            found_year = re.search(r'\b(19|20)\d{2}\b', line)
            if found_year:
                year = found_year.group(0)
                # Check if this line contains a degree keyword
                for keyword in degree_keywords:
                    if re.search(rf'\b{re.escape(keyword)}\b', line, re.IGNORECASE):
                        # Clean up the line to just the qualification part
                        clean_line = line.replace(year, '').strip()
                        # Remove common separators and brackets
                        clean_line = re.sub(r'[\(\)\-\:\,]', ' ', clean_line).strip()
                        # Re-format properly
                        qual_list.append(f"{clean_line} - {year}")
                        break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_quals = []
        for q in qual_list:
            if q not in seen:
                unique_quals.append(q)
                seen.add(q)
        
        # Sort by year descending
        try:
            unique_quals.sort(key=lambda x: int(re.search(r'(\d{4})$', x).group(1)), reverse=True)
        except Exception:
            pass
            
        return '\n'.join(unique_quals)
    
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
        validation['NAME'] = bool(fields.get('NAME')) and len(str(fields['NAME']).split()) >= 2
        
        # DOB validation
        dob = fields.get('DOB', '')
        validation['DOB'] = bool(dob) and (
            re.match(r'\d{4}-\d{2}-\d{2}', str(dob)) or
            re.match(r'\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}', str(dob))
        )
        
        # Qualification validation
        validation['QUALIFICATIONS'] = bool(fields.get('QUALIFICATIONS'))
        
        # Nationality validation
        validation['NATIONALITY'] = bool(fields.get('NATIONALITY'))
        
        # Gender validation
        gender = fields.get('GENDER', '')
        validation['GENDER'] = str(gender) in ['Male', 'Female', 'M', 'F']
        
        return validation
