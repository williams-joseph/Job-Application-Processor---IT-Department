# ECOWAS Application Processor - Quick Start

## 🚀 Installation (5 minutes)

### Windows
1. Download Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
2. Run `setup.bat`
3. Done!

### Linux/Mac
```bash
# Install Tesseract
sudo apt-get install tesseract-ocr  # Ubuntu/Debian
brew install tesseract              # Mac

# Setup project
chmod +x setup.sh
./setup.sh
```

## ▶️ Running the App

```bash
# Activate environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Run application
python main.py
```

## 📁 Folder Structure

```
Parent Folder/
├── Applicant 1/
│   ├── Application Form.pdf
│   └── other files...
├── Applicant 2/
│   ├── Application Form.docx
│   └── other files...
└── ...
```

## 🎯 Basic Workflow

1. **Select Parent Folder** → Folder containing all applicant subfolders
2. **Select Excel File** → Where to save results
3. **Click "Process Applications"** → Wait for completion
4. **Review Results** → Check table, edit if needed
5. **Export to Excel** → Save to file

## 🎨 Color Codes

- ⬜ **White**: Good (80%+ confidence)
- 🟨 **Yellow**: Check (60-80% confidence)
- 🟥 **Red**: Review required (<60% confidence)

## 🔍 Filters

- **All**: Show everything
- **Flagged**: Low confidence entries
- **Errors**: Failed extractions only

## ⚡ Quick Tips

1. ✅ Use "Application Form" in filename
2. ✅ One applicant per folder
3. ✅ PDF/DOCX preferred over images
4. ✅ Test with 10 files first
5. ✅ Review flagged items before export

## 🧪 Test Run

```bash
# Create sample data
python test_setup.py

# Now run the app and select the 'test_data' folder
python main.py
```

## 📊 Expected Performance

- **500 PDF applications**: ~20-30 minutes
- **500 DOCX applications**: ~10-15 minutes
- **Success rate**: 85-95% (with standard forms)

## 🆘 Common Issues

### "Tesseract not found"
→ Install Tesseract OCR (see installation above)

### "Application form not found"
→ Check filename contains "application" or "form"

### "Permission denied" on Excel
→ Close Excel file before exporting

### Low confidence scores
→ Use typed forms instead of handwritten/scanned

## 📚 Full Documentation

- **Complete Guide**: `USER_GUIDE.md`
- **Offline Export**: `OFFLINE_EXPORT_GUIDE.md`
- **README**: `README.md`

## 🔧 Build Executable

```bash
pip install pyinstaller
python build.py
# Output: dist/ECOWAS-Application-Processor.exe
```

---

**Need help?** Check `USER_GUIDE.md` for detailed instructions!
