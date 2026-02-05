# Windows Deployment & Testing Guide

This guide explains how to move your development from Linux to Windows, test the application, and build the final executable for the ECOWAS CCJ IT Department.

## 1. Prepare the Windows Machine

Before you can run or build the app, you need to set up the Windows environment. This is a **one-time setup**.

### Step 1: Install Python
1.  Download **Python 3.12** (or newer) from [python.org](https://www.python.org/downloads/).
2.  Run the installer.
3.  **IMPORTANT:** Check the box that says **"Add Python to PATH"** before clicking Install.

### Step 2: Install Tesseract OCR
The application needs Tesseract to read scanned documents.
1.  Download the **Tesseract installer** (e.g., `tesseract-ocr-w64-setup.exe`) from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
2.  Run the installer.
3.  Install it to the default location: `C:\Program Files\Tesseract-OCR`.
    *   *If you install it elsewhere, you must update `config.py` with the new path.*

### Step 3: Get the Code
1.  Go to the GitHub repository.
2.  Click **Code** -> **Download ZIP**.
3.  Extract the ZIP folder to your Documents or Desktop.

---

## 2. Setup the Environment

 Now that you have the code and Python:

1.  Open the extracted folder.
2.  Double-click **`setup.bat`**.
3.  A black window (Command Prompt) will open. It will:
    *   Create a virtual environment (`venv`).
    *   Install all necessary libraries (`pdfplumber`, `pandas`, `openpyxl`, etc.).
4.  When it says **"Setup Complete!"**, you are ready.

---

## 3. Test the Application

To run the app as a developer (before building the .exe):

1.  Inside the project folder, right-click and select "Open in Terminal" or type `cmd` in the address bar to open Command Prompt.
2.  Activate the environment:
    ```cmd
    venv\Scripts\activate
    ```
    *(You should see `(venv)` appear at the start of the line)*
3.  Run the main application:
    ```cmd
    python main.py
    ```
4.  The **Splash Screen** should appear, followed by the main window. Test it with some sample files.

---

## 4. Build the Final Executable (.exe)

When testing is successful and you want to create the file for distribution:

1.  In the same Command Prompt (with `(venv)` active), run:
    ```cmd
    python build.py
    ```
2.  Wait for the build process to finish. It takes about 1-2 minutes.
3.  Navigate to the newly created **`dist/`** folder.
4.  You will see **`ECOWAS-Application-Processor.exe`**.

## 5. Deployment / Distribution

To give this app to other users at ECOWAS:

1.  Copy **`ECOWAS-Application-Processor.exe`** from the `dist/` folder to a USB drive or shared network folder.
2.  On the user's computer, ensure **Tesseract OCR** is installed (see Step 1.2).
3.  Paste the `.exe` on their Desktop.
4.  Double-click to run. No other installation is required!
