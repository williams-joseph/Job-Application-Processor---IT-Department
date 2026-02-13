# ECOWAS Job Application Processor

## Overview
This tool automates the extraction of applicant data from **PDF** and **Word (DOCX)** application forms. It is designed to drastically reduce the time spent on manual data entry by processing hundreds of applications in batches and exporting the results to Excel.

## Key Features
- **Batch Processing**: Capable of processing 500+ applicant folders at once.
- **Offline & Secure**: Runs entirely on your local machine. No internet access required, ensuring data privacy.
- **Intelligent Extraction**: pulls Name, Date of Birth, Nationality, Qualifications, and Experience from standard ECOWAS application forms.
- **Excel Sync**: Updates your existing "Research Officer" or other tracking sheets without creating duplicate rows.
- **Smart Filtering**: 
  - Standardizes dates (e.g., "20th Sept" -> "2023-09-20").
  - Rounds experience years (e.g., 4.7 years -> 5 years).
  - Deduplicates qualifications.

## How to Use
1.  **Launch the Application**: Run the `ECOWAS Processor.exe` or `main.py`.
2.  **Select Folders**:
    *   **Parent Folder**: Browse to the folder containing all your applicant sub-folders (e.g., `Downloads/Research Officer`).
    *   **Excel File**: Select your tracking Excel sheet (or create a new one).
3.  **Process**: Click **Process Applications**. The tool will scan each folder, read the forms, and show progress.
4.  **Review**:
    *   **Extracted Data**: View the results table. Double-click any cell to manually correct specific details if needed.
    *   **Errors**: Check the "Errors & Warnings" tab for any files that couldn't be read.
5.  **Export**: Click **Export to Excel** to save the clean data into your spreadsheet.

## Installation & Building (Windows)
To create the standalone `.exe` file for distribution:

1.  **Install Python**: Ensure Python 3.10+ is installed.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Install Tesseract OCR**:
    *   Download and install Tesseract OCR for Windows.
    *   Ensure the path in `config.py` matches your installation (Default: `C:\Program Files\Tesseract-OCR\tesseract.exe`).
4.  **Build the Executable**:
    Run the build script in your terminal:
    ```bash
    python build.py
    ```
    The final `ECOWAS Job Application Processor.exe` will be found in the `dist` folder.

## Requirements
*   **OS**: Windows 10/11
*   **Software**: Microsoft Excel (for viewing exports)
*   **Tesseract OCR**: Required for scanning PDF images.
