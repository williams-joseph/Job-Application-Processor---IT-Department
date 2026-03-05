# ECOWAS Application Processor - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Using the Application](#using-the-application)
5. [Understanding Results](#understanding-results)
6. [Troubleshooting](#troubleshooting)
7. [Tips for Best Results](#tips-for-best-results)

---

## Getting Started

### What Does This Application Do?

The ECOWAS Application Processor automates the extraction of data from job application forms. Instead of manually reading each PDF or Word document and typing the information into Excel, this tool:

1. **Scans** all applicant folders automatically
2. **Extracts** key information (Name, DOB, Qualification, etc.)
3. **Validates** the extracted data
4. **Exports** to Excel with confidence scoring
5. **Handles errors** gracefully without stopping

### Expected Time Savings

- **Manual processing**: ~5 minutes per application
- **With this tool**: ~3-4 seconds per application
- **For 500 applications**: Reduces ~42 hours to ~30 minutes

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 7 or later, Linux, macOS
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space
- **Python**: 3.8 or higher (if running from source)

### Required Software
1. **Python 3.8+** - [Download](https://www.python.org/downloads/)
2. **Tesseract OCR** - [Download for Windows](https://github.com/UB-Mannheim/tesseract/wiki)
   - Required for scanning image-based PDFs
   - Install to default location: `C:\Program Files\Tesseract-OCR`

---

## Installation

### Option 1: Windows Executable (Easiest)

1. Download `ECOWAS-Application-Processor.exe`
2. Install Tesseract OCR (see link above)
3. Double-click the `.exe` to run

### Option 2: Run from Source

#### Windows:
```batch
# 1. Download and extract the project
# 2. Open Command Prompt in project folder
# 3. Run setup script
setup.bat
```

#### Linux/Mac:
```bash
# 1. Download and extract the project
# 2. Open Terminal in project folder
# 3. Run setup script
chmod +x setup.sh
./setup.sh
```

---

## Using the Application

### Step-by-Step Workflow

#### 1. Prepare Your Folders

Organize applications like this:
```
Account Treasury/
├── John Doe/
│   ├── Application Form.pdf
│   ├── Resume.pdf
│   └── ID Card.jpg
├── Jane Smith/
│   ├── Application Form.docx
│   └── Certificates.pdf
└── ...
```

**Requirements**:
- Each applicant has their own folder
- Folder name = Applicant name (optional but helpful)
- Application form should have "application" or "form" in filename
- Supported formats: PDF, DOCX, DOC, JPG, PNG

#### 2. Launch the Application

- **Executable**: Double-click `ECOWAS-Application-Processor.exe`
- **Source**: Run `python main.py`

#### 3. Select Files

a) **Parent Folder**:
   - Click "Browse" next to "Parent Folder"
   - Select the folder containing all applicant subfolders
   - Example: Select `Account Treasury` folder

b) **Excel File**:
   - Click "Browse" next to "Excel File"
   - Select existing Excel file to update
   - Or create a new one if prompted

#### 4. Process Applications

1. Click **"Process Applications"**
2. Confirm the processing (can't be undone once started)
3. Watch the progress bar
4. Wait for completion message

**What Happens During Processing**:
- Scans all subfolders
- Finds application forms
- Extracts text (using OCR if needed)
- Parses fields using pattern matching
- Validates extracted data
- Calculates confidence scores

#### 5. Review Results

After processing, you'll see a table with:

| Column | Description |
|--------|-------------|
| **Applicant** | Folder name |
| **Name** | Extracted full name |
| **DOB** | Date of birth |
| **Qualification** | Educational qualification |
| **Nationality** | Nationality |
| **Sex** | Gender (Male/Female) |
| **Status** | `success`, `failed`, `no_form`, `error` |
| **Confidence** | Overall confidence % |

**Color Coding**:
- 🟢 **White/No color**: High confidence (80%+)
- 🟡 **Yellow**: Medium confidence (60-80%)
- 🔴 **Red**: Low confidence (<60%) or error

#### 6. Edit Data (if needed)

- **Double-click** any cell to edit
- Press **Enter** to save
- Edits are preserved in the table

#### 7. Filter Results

Use the filter options:
- **All**: Show all applicants
- **Flagged**: Show only low-confidence entries that need review
- **Errors**: Show only failed extractions

#### 8. Export to Excel

1. Review/edit data as needed
2. Click **"Export to Excel"**
3. Data appends to your Excel file
4. Color coding preserved (red/yellow/green)

#### 9. Export Error Log (Optional)

If some applications failed:
1. Click **"Export Error Log"**
2. Choose save location
3. Review errors to fix source files

---

## Understanding Results

### Extraction Status

| Status | Meaning | Action Required |
|--------|---------|----------------|
| `success` | Data extracted successfully | Review if confidence is low |
| `no_form` | Application form not found in folder | Check folder structure |
| `failed` | Text extracted but parsing failed | Review document format |
| `error` | Exception during processing | Check error log |
| `unsupported` | File format not supported | Convert to PDF/DOCX |

### Confidence Scores

Confidence indicates how certain the system is about the extracted data:

- **90-100%**: Very confident (usually correct)
- **80-89%**: Confident (likely correct, worth quick check)
- **60-79%**: Moderate (should review)
- **Below 60%**: Low (definitely review)

**What Affects Confidence**:
- Clear, standard formatting = Higher confidence
- Handwritten text = Lower confidence
- Scanned images = Lower confidence
- Unusual layouts = Lower confidence

### Common Issues & Fixes

#### Issue: "Application form not found"
**Causes**:
- No files in applicant folder
- File doesn't have "application" or "form" in name
- Unsupported file format

**Fix**:
- Rename file to include "Application Form"
- Ensure file is PDF/DOCX
- Check file is in applicant's folder

#### Issue: Wrong data extracted
**Causes**:
- Non-standard form layout
- Poor quality scan
- Handwritten forms

**Fix**:
- Manually edit in results table before export
- Improve scan quality (300 DPI recommended)
- Use typed forms when possible

#### Issue: Slow processing
**Causes**:
- Large PDFs with many pages
- Image-based PDFs requiring OCR
- Low system resources

**Fix**:
- Close other applications
- Process in smaller batches
- Use text-based PDFs instead of scans

---

## Tips for Best Results

### Form Preparation

1. **Use Standard Templates**
   - Consistent layouts improve accuracy
   - Label fields clearly: "Name:", "Date of Birth:", etc.

2. **Digital Forms > Scanned Forms**
   - Typed text extracts more reliably than handwriting
   - If scanning, use 300 DPI or higher

3. **File Naming**
   - Include "Application" or "Form" in filename
   - Examples: `Application Form.pdf`, `Job Application.docx`

### Folder Organization

1. **One Applicant Per Folder**
   - Keep all documents for one person together
   - Folder name should be applicant's name

2. **Avoid Nested Subfolders**
   - Structure: `Parent/Applicant/Files`
   - Not: `Parent/Department/Position/Applicant/Files`

### Processing Strategy

1. **Test First**
   - Process 10-20 applications first
   - Review accuracy before processing all 500
   - Adjust form templates if needed

2. **Batch Processing**
   - Instead of 500 at once, try 100 at a time
   - Allows quicker review cycles
   - Easier to spot systematic issues

3. **Review Flagged Items**
   - Use "Flagged" filter to see low-confidence entries
   - Edit before exporting to Excel
   - Learn what causes low confidence

---

## Troubleshooting

### Installation Issues

**"Python not found"**
```bash
# Windows: Download from python.org and check "Add to PATH"
# Linux: sudo apt-get install python3.8
# Mac: brew install python@3.8
```

**"Module not found" errors**
```bash
pip install -r requirements.txt
# Or individually:
pip install pdfplumber python-docx pytesseract openpyxl Pillow
```

**"Tesseract not found"**
- Windows: Install from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- Linux: `sudo apt-get install tesseract-ocr`
- Mac: `brew install tesseract`
- Update `TESSERACT_PATH` in `config.py` if non-default location

### Runtime Issues

**"Permission denied" on Excel file**
- Close the Excel file before processing
- Ensure file is not read-only
- Check you have write permissions

**Application freezes**
- Processing is CPU-intensive, be patient
- Check progress bar is moving
- Force close only if truly frozen (Ctrl+C or Task Manager)

**Out of memory errors**
- Process in smaller batches
- Close other applications
- Increase system RAM if possible

**No data extracted**
- Check file is not password-protected
- Verify file is not corrupted
- Try opening file manually first

### Data Quality Issues

**Names not extracted**
- Check "Name:" or "Full Name:" label exists
- Ensure name is on same line or next line after label
- Name should start with capital letter

**Dates not recognized**
- Use standard formats: DD/MM/YYYY or DD-MM-YYYY
- Month names also work: "15 March 1990"
- Avoid ambiguous formats

**Wrong gender extracted**
- Check "Sex:" or "Gender:" label exists
- Use "Male/Female" or "M/F"
- Avoid ambiguous terms

---

## Advanced Features

### Google Sheets Integration

See `GOOGLE_SHEETS_SETUP.md` for:
- Setting up Google Cloud credentials
- Syncing directly to Google Sheets
- Real-time cloud storage

### Customization

Edit `config.py` to customize:
- Field extraction patterns
- Confidence thresholds
- File type support
- Processing workers (parallel processing)
- UI colors and layout

### Error Logging

- All processing logged to `ecowas_processor.log`
- Includes timestamps and detailed errors
- Useful for debugging issues
- Share with support if needed

---

## Getting Help

### Before Asking for Help

1. Check this user guide
2. Review error log file
3. Try with a single test file first
4. Verify file formats are supported

### Information to Provide

When reporting issues, include:
- Operating system and version
- Python version (`python --version`)
- Error message (full text)
- Sample file (if possible)
- Screenshot of issue

---

## Appendix

### Supported File Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Text-based or scanned |
| Word | `.docx`, `.doc` | Modern and legacy formats |
| Image | `.jpg`, `.jpeg`, `.png`, `.tiff`, `.bmp` | Requires Tesseract OCR |

### Default Field Patterns

The system looks for these patterns:

- **Name**: "Name:", "Full Name:", "Applicant Name:"
- **DOB**: "Date of Birth:", "DOB:", "Birth Date:"
- **Qualification**: "Qualification:", "Educational Qualification:"
- **Nationality**: "Nationality:", "Country of Citizenship:"
- **Sex**: "Sex:", "Gender:"

### Performance Benchmarks

Based on testing with 500 applications:

| File Type | Avg Time per File | 500 Files Total |
|-----------|-------------------|-----------------|
| Text PDF | 2-3 seconds | 16-25 minutes |
| DOCX | 1-2 seconds | 8-16 minutes |
| Scanned PDF (OCR) | 5-8 seconds | 42-67 minutes |

*Times vary based on system specs and file sizes*

---

**Version**: 1.0.0  
**Last Updated**: February 2026  
**Support**: Check project README for contact information
