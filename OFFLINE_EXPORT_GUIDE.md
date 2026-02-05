# Offline Data Export Guide

This application is designed to work **completely offline** - no internet connection required!

## Overview

The ECOWAS Application Processor exports all data to **Excel files (.xlsx)** that you can:
- Open and edit in Microsoft Excel
- Open in Google Sheets (by uploading manually)
- Open in LibreOffice Calc
- Share via USB, email, or network drive

## How It Works

### 1. Process Applications
1. Select the folder containing application documents
2. Click "Start Processing"
3. Review and edit extracted data in the application
4. Click "Export to Excel"

### 2. Excel File Output

The application creates or updates an Excel file with:
- **Professional formatting**: Color-coded headers
- **Confidence indicators**: Visual highlights for low-confidence data
- **All required fields**: Name, Date of Birth, Qualification, Nationality, Sex
- **Status tracking**: Shows which applications were processed successfully

### 3. Manual Upload to Google Sheets (Optional)

If you want to use Google Sheets, you can manually upload the Excel file:

1. **Go to Google Sheets**: [sheets.google.com](https://sheets.google.com)
2. **Upload the Excel file**:
   - Click "New" → "File Upload"
   - Drag and drop your Excel file
   - Or click "Browse" to select the file
3. **Done!** Your data is now in Google Sheets

### 4. Sharing the Excel File

You can share the Excel file however you prefer:
- **USB Drive**: Copy to flash drive
- **Email**: Attach to email
- **Network Drive**: Save to shared folder
- **Cloud Storage**: Upload to Google Drive, Dropbox, etc.

## Benefits of Offline Operation

✅ **No Internet Required**: Process applications anywhere, anytime  
✅ **Complete Privacy**: Your data never leaves your computer  
✅ **Faster Processing**: No network delays  
✅ **No API Costs**: No Google Cloud fees or quotas  
✅ **Simple Setup**: No complex API configuration needed  
✅ **Works Anywhere**: Perfect for locations with limited connectivity  

## Excel File Features

### Color Coding
- **Red highlighting**: Low confidence (< 60%) - requires review
- **Yellow highlighting**: Medium confidence (60-80%) - worth checking
- **No highlighting**: High confidence (> 80%) - likely accurate

### Professional Format
- Bold headers with blue background
- Properly sized columns for readability
- All data aligned for easy scanning

### Easy Editing
- Click any cell to edit manually
- Add notes or comments
- Sort and filter data
- Create charts and pivot tables

## Working with Multiple Batches

If you're processing applications in batches:

1. **Same Excel file**: The application appends new data to existing file
2. **Separate files**: Use different filenames for different batches
3. **Merge later**: Use Excel's consolidation features to combine

## Importing to Other Systems

The Excel file can be imported into:
- **Database systems**: MySQL, PostgreSQL, etc.
- **CRM systems**: Salesforce, HubSpot, etc.
- **Custom applications**: Via CSV export
- **Google Workspace**: Sheets, Forms, etc.

## Troubleshooting

### "Export failed"
- Check you have write permissions to the output folder
- Ensure the Excel file isn't open in another program
- Try a different filename or location

### "Can't open Excel file"
- Make sure you have Excel, LibreOffice, or similar installed
- File can be opened in Google Sheets via upload
- Check the file isn't corrupted (should be ~10KB minimum)

### "Data looks wrong"
- Use the review interface before exporting
- Edit any incorrect fields manually
- Re-process with better quality scans if needed

## Data Security

🔒 **Your data is completely private**:
- Never sent to external servers
- Never uploaded to the cloud (unless you choose to)
- Stored only on your computer
- You have complete control

## Need Cloud Features?

While this application is offline-only, you can still:
1. **Manually upload** Excel files to Google Sheets anytime
2. **Use cloud storage** like Google Drive to store Excel files
3. **Share files** via email or network drives
4. **Import data** into cloud-based systems after processing

This gives you the **best of both worlds**: offline privacy and speed, with cloud access when YOU choose.

---

## Quick Reference

| Task | Steps |
|------|-------|
| Export data | Click "Export to Excel" button |
| Upload to Google Sheets | Go to sheets.google.com → File Upload |
| Edit exported data | Open Excel file and make changes |
| Share with team | Email file or save to shared drive |
| Process new batch | Use same Excel file or create new one |

**Questions?** See the main `USER_GUIDE.md` for detailed instructions.
