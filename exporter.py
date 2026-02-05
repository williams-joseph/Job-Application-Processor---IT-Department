"""
Excel export functionality for offline use.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
import logging

try:
    from openpyxl import load_workbook, Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
except ImportError:
    load_workbook = None
    Workbook = None

logger = logging.getLogger(__name__)


class ExcelExporter:
    """Handles Excel file operations."""
    
    HEADER_ROW = ['S/N', 'Name', 'Date of Birth', 'Qualification', 'Nationality', 'Sex']
    
    def __init__(self):
        if not load_workbook:
            raise ImportError("openpyxl not installed")
    
    def append_to_excel(self, excel_path: str, data_rows: List[Dict]) -> Dict:
        """
        Append extracted data to existing Excel file.
        
        Args:
            excel_path: Path to Excel file
            data_rows: List of dictionaries with extracted data
            
        Returns:
            Dictionary with export statistics
        """
        excel_path = Path(excel_path)
        
        # Load or create workbook
        if excel_path.exists():
            wb = load_workbook(excel_path)
            ws = wb.active
            logger.info(f"Loaded existing Excel file: {excel_path}")
        else:
            wb = Workbook()
            ws = wb.active
            ws.title = "Applications"
            # Add header row
            self._write_header(ws)
            logger.info(f"Created new Excel file: {excel_path}")
        
        # Find last row
        start_row = ws.max_row + 1
        
        # Ensure header exists
        if ws.max_row == 1 and not ws['A1'].value:
            self._write_header(ws)
            start_row = 2
        
        # Append data rows
        rows_added = 0
        for idx, data in enumerate(data_rows):
            row_num = start_row + idx
            
            fields = data.get('fields', {})
            
            # S/N is the row number (excluding header)
            ws[f'A{row_num}'] = row_num - 1
            ws[f'B{row_num}'] = fields.get('Name', '')
            ws[f'C{row_num}'] = fields.get('Date of Birth', '')
            ws[f'D{row_num}'] = fields.get('Qualification', '')
            ws[f'E{row_num}'] = fields.get('Nationality', '')
            ws[f'F{row_num}'] = fields.get('Sex', '')
            
            rows_added += 1
        
        # Save workbook
        wb.save(excel_path)
        logger.info(f"Added {rows_added} rows to Excel file")
        
        return {
            'rows_added': rows_added,
            'total_rows': ws.max_row - 1,  # Exclude header
            'file_path': str(excel_path),
        }
    
    def _write_header(self, worksheet):
        """Write header row with formatting."""
        for idx, header in enumerate(self.HEADER_ROW, start=1):
            cell = worksheet.cell(row=1, column=idx)
            cell.value = header
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Set column widths
        worksheet.column_dimensions['A'].width = 8   # S/N
        worksheet.column_dimensions['B'].width = 25  # Name
        worksheet.column_dimensions['C'].width = 15  # DOB
        worksheet.column_dimensions['D'].width = 30  # Qualification
        worksheet.column_dimensions['E'].width = 15  # Nationality
        worksheet.column_dimensions['F'].width = 10  # Sex
    
    def create_template(self, output_path: str):
        """Create a template Excel file with headers."""
        wb = Workbook()
        ws = wb.active
        ws.title = "Applications"
        self._write_header(ws)
        wb.save(output_path)
        logger.info(f"Created template Excel file: {output_path}")

