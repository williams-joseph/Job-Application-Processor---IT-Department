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
    
    HEADER_ROW = [
        'S/N', 'NAME', 'POSITION CODE', 'GENDER', 'INT/EXT', 'DOB', 
        'AGE', 'NATIONALITY', 'EXP START (YEAR)', 'EXPERIENCE(Years)', 'QUALIFICATIONS'
    ]
    
    def __init__(self):
        if not load_workbook:
            raise ImportError("openpyxl not installed")
        from config import EXCEL_SHEET_NAME
        self.sheet_name = EXCEL_SHEET_NAME
    
    def append_to_excel(self, excel_path: str, data_rows: List[Dict]) -> Dict:
        """
        Update existing rows or append new ones in the Excel file based on Applicant Name.
        """
        excel_path = Path(excel_path)
        
        # Load or create workbook
        if excel_path.exists():
            wb = load_workbook(excel_path)
            if self.sheet_name in wb.sheetnames:
                ws = wb[self.sheet_name]
            else:
                ws = wb.active
            logger.info(f"Loaded existing Excel file: {excel_path}")
        else:
            wb = Workbook()
            ws = wb.active
            ws.title = self.sheet_name
            self._write_header(ws)
            logger.info(f"Created new Excel file: {excel_path}")

        # Create a mapping of Existing Names to Row Numbers
        # And find the true last row with data to avoid gaps
        name_map = {}
        last_data_row = 1
        
        for row_idx in range(2, ws.max_row + 1):
            cell_val = ws.cell(row=row_idx, column=2).value
            if cell_val:
                # Normalize name for comparison
                name_key = str(cell_val).strip().upper()
                name_map[name_key] = row_idx
                if row_idx > last_data_row:
                    last_data_row = row_idx
        
        rows_updated = 0
        rows_appended = 0
        
        for data in data_rows:
            fields = data.get('fields', {})
            # Get the name we are processing
            applicant_name = fields.get('NAME', '').strip().upper()
            
            if not applicant_name:
                continue

            if applicant_name in name_map:
                # Update existing row
                row_num = name_map[applicant_name]
                rows_updated += 1
            else:
                # Append new row after the last real data row
                row_num = last_data_row + 1
                last_data_row += 1 # Increment for the next append
                rows_appended += 1
                # Write S/N and Name for new rows
                ws.cell(row=row_num, column=1).value = row_num - 1
                ws.cell(row=row_num, column=2).value = applicant_name

            # Write/Update Data Fields
            # Col 3: Position Code
            if fields.get('POSITION CODE'):
                 ws.cell(row=row_num, column=3).value = fields.get('POSITION CODE')
            
            # Col 4: Gender
            ws.cell(row=row_num, column=4).value = fields.get('GENDER', '')
            
            # Col 5: Int/Ext
            if fields.get('INT/EXT'):
                ws.cell(row=row_num, column=5).value = fields.get('INT/EXT')

            # Col 6: DOB
            ws.cell(row=row_num, column=6).value = fields.get('DOB', '')
            
            # Col 7: Age
            ws.cell(row=row_num, column=7).value = fields.get('AGE', '')
            
            # Col 8: Nationality
            ws.cell(row=row_num, column=8).value = fields.get('NATIONALITY', '')
            
            # Col 9: Exp Start
            ws.cell(row=row_num, column=9).value = fields.get('EXP START (YEAR)', '')
            
            # Col 10: Experience
            ws.cell(row=row_num, column=10).value = fields.get('EXPERIENCE(Years)', '')
            
            # Col 11: Qualifications
            qual_cell = ws.cell(row=row_num, column=11)
            qual_cell.value = fields.get('QUALIFICATIONS', '')
            qual_cell.alignment = Alignment(wrap_text=True, vertical="top")
        
        # Cleanup: Remove any extra columns beyond K (11)
        # This fixes the issue of "seeing L to CN" ghost columns
        if ws.max_column > 11:
            cols_to_delete = ws.max_column - 11
            ws.delete_cols(12, cols_to_delete)
            logger.info(f"Cleaned up {cols_to_delete} extra columns")

        # Save workbook
        try:
            wb.save(excel_path)
            logger.info(f"Sync complete. Updated {rows_updated} rows and appended {rows_appended} rows")
            return {
                'rows_added': rows_updated + rows_appended,
                'rows_updated': rows_updated,
                'rows_appended': rows_appended,
                'file_path': str(excel_path),
            }
        except PermissionError:
             raise PermissionError("Could not save Excel file. Is it open in another program?")
    
    def _write_header(self, worksheet):
        """Write header row with formatting."""
        for idx, header in enumerate(self.HEADER_ROW, start=1):
            cell = worksheet.cell(row=1, column=idx)
            cell.value = header
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Set column widths
        col_widths = {
            'A': 8,   # S/N
            'B': 25,  # NAME
            'C': 20,  # POSITION CODE
            'D': 10,  # GENDER
            'E': 10,  # INT/EXT
            'F': 15,  # DOB
            'G': 8,   # AGE
            'H': 15,  # NATIONALITY
            'I': 18,  # EXP START
            'J': 18,  # EXPERIENCE
            'K': 50,  # QUALIFICATIONS
        }
        for col, width in col_widths.items():
            worksheet.column_dimensions[col].width = width
    
    def create_template(self, output_path: str):
        """Create a template Excel file with headers."""
        wb = Workbook()
        ws = wb.active
        ws.title = self.sheet_name
        self._write_header(ws)
        wb.save(output_path)
        logger.info(f"Created template Excel file: {output_path}")

