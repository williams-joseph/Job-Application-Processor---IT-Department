"""
Configuration file for ECOWAS Application Processor.
"""

import os
from pathlib import Path

# Application Settings
APP_NAME = "ECOWAS Job Application Processor"
APP_VERSION = "1.0.0"

# Processing Settings
MAX_WORKERS = 4  # Number of parallel workers for processing
BATCH_SIZE = 500  # Maximum applications per batch

# File Settings
SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.doc', '.jpg', '.jpeg', '.png', '.tiff', '.bmp']
APPLICATION_FORM_KEYWORDS = ['application', 'form', 'application form']

# Tesseract OCR Path (Update for your system)
# Windows default
# Tesseract OCR Path
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Confidence Thresholds
CONFIDENCE_LOW = 0.6
CONFIDENCE_MEDIUM = 0.8
CONFIDENCE_HIGH = 0.9

# Excel Settings
EXCEL_SHEET_NAME = "Sheet1"
EXCEL_HEADERS = [
    'S/N', 'NAME', 'POSITION CODE', 'GENDER', 'INT/EXT', 'DOB', 
    'AGE', 'NATIONALITY', 'EXP START (YEAR)', 'EXPERIENCE(Years)', 'QUALIFICATIONS'
]

# Default values for constant fields
DEFAULT_POSITION_CODE = "ACCTRE_25EXT"
DEFAULT_INT_EXT = "EXT"



# Logging Settings
LOG_FILE = "ecowas_processor.log"
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Field Extraction Settings
FIELD_DEFINITIONS = {
    'NAME': {
        'required': True,
        'validation': lambda x: len(str(x).split()) >= 2,
        'error_message': 'Name should contain at least first and last name',
    },
    'GENDER': {
        'required': True,
        'validation': lambda x: str(x).upper() in ['MALE', 'FEMALE', 'M', 'F'],
        'error_message': 'Gender must be Male, Female, M, or F',
    },
    'DOB': {
        'required': True,
        'validation': lambda x: bool(x),
        'error_message': 'Date of Birth is required',
    },
    'NATIONALITY': {
        'required': True,
        'validation': lambda x: bool(x),
        'error_message': 'Nationality is required',
    },
    'EXP START (YEAR)': {
        'required': False,
        'validation': lambda x: True,
        'error_message': '',
    },
    'QUALIFICATIONS': {
        'required': True,
        'validation': lambda x: bool(x),
        'error_message': 'Qualification is required',
    },
}

# UI Settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
MIN_WINDOW_WIDTH = 1000
MIN_WINDOW_HEIGHT = 600

# Color Scheme
COLOR_SUCCESS = "#c6efce"
COLOR_WARNING = "#ffeb9c"
COLOR_ERROR = "#ffc7ce"
COLOR_PRIMARY = "#4472c4"

# Performance Settings
OCR_DPI = 300  # DPI for OCR image conversion
PDF_MAX_PAGES = 10  # Maximum pages to process per PDF (application forms are typically 1-2 pages)
