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

### Step 4: Enable PowerShell Scripts (Fix "scripts disabled" error)
Windows prevents PowerShell scripts from running by default. You need to enable them to allow your virtual environment to activate.
1.  Open **PowerShell** as Administrator or a standard PowerShell window.
2.  Run the following command:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```
3.  Type `Y` or `A` (Yes to All) if prompted.

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
4.  The application window will open directly.
5.  **New Features:** 
    *   **Position Code:** You can now type the specific position code (like `ACCTRE_25EXT`) directly in the app before processing.
    *   **Int/Ext Status:** You can also set the default status for the batch.

---

## 4. Build the Final Executable (.exe)

The project includes a `build.py` script that handles the complex PyInstaller command for you. It uses the flags you recommended:
*   `--onefile`: Creating a single executable file.
*   `--windowed`: Preventing a console window from opening.
*   `--icon`: Attaching your custom `icon.ico`.
*   `--add-data`: Bundling the logos and guides inside the `.exe`.

To build:
1.  In the same Command Prompt (with `(venv)` active), run:
    ```cmd
    python build.py
    ```
2.  Wait for the build process to finish.
3.  Navigate to the newly created **`dist/`** folder.
4.  You will see **`ECOWAS-Application-Processor.exe`**.

*Note: If you want to run the command manually, use:*
`pyinstaller --onefile --windowed --icon=icon.ico --add-data "logo_square.png;." --add-data "logo.png;." main.py`

## 5. Deployment / Distribution

To give this app to other users at ECOWAS:

1.  Copy **`ECOWAS-Application-Processor.exe`** from the `dist/` folder to a USB drive or shared network folder.
2.  On the user's computer, ensure **Tesseract OCR** is installed (see Step 1.2).
3.  Paste the `.exe` on their Desktop.
4.  Double-click to run. No other installation is required!

## 6. Troubleshooting VS Code Issues (Windows)

If you see a red squiggly line under `import PyInstaller` or other packages in VS Code while on Windows, follow these steps:

### Issue: "Import 'PyInstaller' could not be resolved"
This is often a VS Code configuration issue, even if the package is installed correctly in your virtual environment.

1.  **Select the Correct Interpreter:**
    *   Click on the Python version in the bottom right corner of VS Code (e.g., `3.12.x (venv)`).
    *   Select the interpreter that points specifically to the virtual environment: `./venv/Scripts/python.exe`.

2.  **Manually Install via Terminal:**
    *   Open the VS Code terminal (`Ctrl + ` `).
    *   Ensure you are in the project root and run:
        ```cmd
        .\venv\Scripts\pip install pyinstaller
        ```
    *   This ensures the package is installed to the local environment correctly.

3.  **Restart the Language Server:**
    *   Press `Ctrl + Shift + P`.
    *   Type **"Python: Restart Language Server"** and press Enter.
    *   This forces VS Code to re-scan the environment and should clear the error.

### General Tips for Windows
*   **Always use the Virtual Environment:** If you see errors about "module not found" when running `python main.py`, ensure your terminal shows `(venv)` at the start of the line. If not, run `venv\Scripts\activate`.
*   **Permissions:** If building the `.exe` fails due to "Access Denied", try running your terminal or VS Code as an Administrator.
