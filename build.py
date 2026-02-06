"""
Build script for creating standalone executable.
Requires PyInstaller: pip install pyinstaller
"""

import os
import sys
import subprocess
from pathlib import Path

def build_executable():
    """Build standalone executable using PyInstaller."""
    
    print("=" * 60)
    print("ECOWAS Application Processor - Build Script")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("\nError: PyInstaller not installed")
        print("Install with: pip install pyinstaller")
        return False
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",              # Single executable
        "--windowed",             # No console window
        "--name", "ECOWAS-Application-Processor",
        "--icon", "icon.ico" if Path("icon.ico").exists() else "",
        # Separator : for Linux/Mac, ; for Windows in --add-data
        "--add-data", f"README.md{os.pathsep}.",  
        "--add-data", f"OFFLINE_EXPORT_GUIDE.md{os.pathsep}.",
        "--add-data", f"QUICK_START.md{os.pathsep}.", 
        "--add-data", f"logo.png{os.pathsep}.",
        "--add-data", f"logo_square.png{os.pathsep}.",
        "--add-data", f"icon.ico{os.pathsep}.",
        "--hidden-import", "openpyxl",
        "--hidden-import", "pdfplumber",
        "--hidden-import", "docx",
        "--hidden-import", "pytesseract",
        "--hidden-import", "PIL",
        "--hidden-import", "ttkthemes",
        "main.py"
    ]
    
    # Remove empty icon parameter if no icon file
    cmd = [c for c in cmd if c]
    
    print("\nBuilding executable...")
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        
        print("\n" + "=" * 60)
        print("Build Complete!")
        print("=" * 60)
        print(f"\nExecutable location: dist/ECOWAS-Application-Processor.exe")
        print("\nNext steps:")
        print("1. Test the executable")
        print("2. Install Tesseract OCR on target machine")
        print("3. Distribute to users")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("\nBuild failed!")
        print(e.stderr)
        return False

def clean_build_files():
    """Clean build artifacts."""
    import shutil
    
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['*.spec']
    
    print("\nCleaning build files...")
    
    for dir_name in dirs_to_remove:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"Removed {dir_name}/")
    
    for pattern in files_to_remove:
        for file in Path('.').glob(pattern):
            file.unlink()
            print(f"Removed {file}")
    
    print("Clean complete!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'clean':
        clean_build_files()
    else:
        build_executable()
