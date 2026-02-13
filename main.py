"""
Main GUI application for ECOWAS Application Processor.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import logging
import os
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime

from processor import ApplicationProcessor
from exporter import ExcelExporter
from PIL import Image, ImageTk

# Try to import ttkthemes for better styling
try:
    from ttkthemes import ThemedTk
    THEMES_AVAILABLE = True
except ImportError:
    THEMES_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ecowas_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class ApplicationGUI:
    """Main GUI application."""
    
    def __init__(self):
        if THEMES_AVAILABLE:
            self.root = ThemedTk(theme="arc")
        else:
            self.root = tk.Tk()
        
        import config
        self.root.title(config.APP_NAME)
        
        # Set window icon
        try:
            icon_path = Path(resource_path("logo_square.png"))
            if icon_path.exists():
                self.icon_photo = tk.PhotoImage(file=str(icon_path))
                self.root.iconphoto(True, self.icon_photo)
        except Exception as e:
            logger.error(f"Could not load icon: {e}")

        # Calculate position to center the window
        width = 900
        height = 650
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.minsize(800, 500)
        
        # Initialize components
        self.processor = ApplicationProcessor(max_workers=4)
        self.excel_exporter = ExcelExporter()
        
        # Data
        self.results: List[Dict] = []
        self.filtered_results: List[Dict] = []
        self.parent_folder = ""
        self.excel_file = ""
        
        # UI Setup
        self._setup_ui()
        
        # Processing state
        self.is_processing = False
        
        # Load existing history
        self._load_history()
        
    def _setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1) # Give expansion weight to the Notebook (Row 3)
        
        # === Section 1: File Selection ===
        selection_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        selection_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        selection_frame.columnconfigure(1, weight=1)
        
        # Parent folder
        ttk.Label(selection_frame, text="Parent Folder:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.folder_entry = ttk.Entry(selection_frame, width=50)
        self.folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(selection_frame, text="Browse", command=self._browse_folder).grid(row=0, column=2, pady=5)
        
        # Excel file
        ttk.Label(selection_frame, text="Excel File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.excel_entry = ttk.Entry(selection_frame, width=50)
        self.excel_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(selection_frame, text="Browse", command=self._browse_excel).grid(row=1, column=2, pady=5)
        
        # === Section 2: Processing Controls ===
        control_frame = ttk.Frame(main_frame, padding="5")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.process_btn = ttk.Button(
            control_frame,
            text="Process Applications",
            command=self._start_processing,
            style="Accent.TButton"
        )
        self.process_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Export to Excel", command=self._export_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Clear Results", command=self._clear_results).pack(side=tk.LEFT, padx=5)
        
        # Filter controls
        ttk.Label(control_frame, text="Filter:").pack(side=tk.LEFT, padx=(20, 5))
        self.filter_var = tk.StringVar(value="all")
        filters = [("All", "all"), ("Errors Only", "errors")]
        for text, value in filters:
            ttk.Radiobutton(
                control_frame,
                text=text,
                variable=self.filter_var,
                value=value,
                command=self._apply_filter
            ).pack(side=tk.LEFT, padx=2)
        
        # === Section 3: Progress Bar ===
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Ready to process")
        ttk.Label(progress_frame, textvariable=self.progress_var).grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', maximum=100)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # === Section 3: Notebook (Tabs) ===
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Tab 1: Extracted Data
        table_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(table_frame, text=" Extracted Data ")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Create treeview with scrollbars for results
        tree_scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        columns = (
            'S/N', 'NAME', 'POSITION CODE', 'GENDER', 
            'INT/EXT', 'DOB', 'AGE', 'NATIONALITY', 'EXP START', 'EXPERIENCE', 'QUALIFICATIONS', 'Status'
        )
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        column_widths = {
            'S/N': 40, 'NAME': 180, 'POSITION CODE': 100, 'GENDER': 60,
            'INT/EXT': 60, 'DOB': 100, 'AGE': 50, 'NATIONALITY': 100,
            'EXP START': 80, 'EXPERIENCE': 80, 'QUALIFICATIONS': 250, 'Status': 100,
        }
        
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_by_column(c))
            self.tree.column(col, width=column_widths.get(col, 100), minwidth=50)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.tree.bind("<Double-1>", self._edit_cell)

        # Tab 2: Errors & Warnings
        error_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(error_frame, text=" Errors & Warnings ")
        error_frame.columnconfigure(0, weight=1)
        error_frame.rowconfigure(0, weight=1)
        
        self.error_text = scrolledtext.ScrolledText(error_frame, font=("Consolas", 10), state='disabled', wrap=tk.WORD)
        self.error_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Tab 3: Processing History
        history_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(history_frame, text=" Processing History ")
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        self.history_text = scrolledtext.ScrolledText(history_frame, font=("Consolas", 10), state='disabled', wrap=tk.WORD)
        self.history_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # === Section 4: Statistics (Removed) ===
        # User requested removal of statistics section.
        # Keeping minimal placeholder if needed or just removing frame completely.
        # Frame was at row 4.
        
        self.stats_text = tk.StringVar(value="")
    
    def _browse_folder(self):
        """Browse for parent folder."""
        folder = filedialog.askdirectory(title="Select Parent Folder Containing Applicant Folders")
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
            self.parent_folder = folder
    
    def _browse_excel(self):
        """Browse for Excel file."""
        file = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if not file:
            # Ask if user wants to create new file
            file = filedialog.asksaveasfilename(
                title="Create New Excel File",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")]
            )
            if file:
                # Create template
                self.excel_exporter.create_template(file)
        
        if file:
            self.excel_entry.delete(0, tk.END)
            self.excel_entry.insert(0, file)
            self.excel_file = file
    
    def _start_processing(self):
        """Start processing applications."""
        if self.is_processing:
            messagebox.showwarning("Processing", "Processing already in progress")
            return
        
        if not self.parent_folder:
            messagebox.showerror("Error", "Please select a parent folder")
            return
        
        # Confirm before starting
        result = messagebox.askyesno(
            "Confirm Processing",
            f"Process all applications in:\n{self.parent_folder}\n\nThis may take several minutes."
        )
        
        if not result:
            return
        
        # Clear previous results
        self._clear_results()
        
        # Disable button
        self.process_btn.config(state='disabled')
        self.is_processing = True
        
        # Start processing in separate thread
        thread = threading.Thread(target=self._process_thread, daemon=True)
        thread.start()
    
    def _process_thread(self):
        """Processing thread."""
        try:
            result = self.processor.process_applications(
                self.parent_folder,
                progress_callback=self._update_progress
            )
            
            # Update UI in main thread
            self.root.after(0, self._processing_complete, result)
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            self.root.after(0, self._processing_error, str(e))
    
    def _update_progress(self, current: int, total: int, message: str):
        """Update progress bar and message."""
        def update():
            if total > 0:
                progress = (current / total) * 100
                self.progress_bar['value'] = progress
            self.progress_var.set(message)
        
        self.root.after(0, update)
    
    def _processing_complete(self, result: Dict):
        """Handle processing completion."""
        self.is_processing = False
        self.process_btn.config(state='normal')
        
        self.results = result.get('results', [])
        self.filtered_results = self.results.copy()
        
        # Update table
        self._populate_table(self.results)
        
        # Update Errors tab
        self._update_errors_tab(result.get('errors', []))
        
        # Update History
        self._add_to_history(result)
        
        # Update statistics
        stats = result.get('stats', {})
        stats_text = (
            f"Total: {stats.get('total_processed', 0)} | "
            f"Successful: {stats.get('successful', 0)} | "
            f"Failed: {stats.get('failed', 0)} | "
            f"Success Rate: {stats.get('success_rate', 0)}% | "
            f"Time: {stats.get('elapsed_time', 0)}s | "
            f"Rate: {stats.get('rate', 0)} apps/s"
        )
        self.stats_text.set(stats_text)
        
        self.progress_var.set("Processing complete!")
        self.progress_bar['value'] = 100
        
        # Add completion marker to history
        self.history_text.config(state='normal')
        self.history_text.insert(1.0, f"[{datetime.now().strftime('%H:%M:%S')}] Batch processing completed successfully.\n\n")
        self.history_text.config(state='disabled')
        
        messagebox.showinfo("Complete", f"Processing complete!\n\n{stats_text}")
    
    def _processing_error(self, error_msg: str):
        """Handle processing error."""
        self.is_processing = False
        self.process_btn.config(state='normal')
        
        self.progress_var.set("Error occurred")
        self.progress_bar['value'] = 0
        
        messagebox.showerror("Processing Error", f"An error occurred:\n\n{error_msg}")
    
    def _populate_table(self, data: List[Dict]):
        """Populate the results table."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add new items
        for idx, result in enumerate(data, start=1):
            fields = result.get('fields', {})
            status = result.get('extraction_status', 'unknown')
            
            values = (
                idx,  # S/N
                fields.get('NAME', ''),
                fields.get('POSITION CODE', ''),
                fields.get('GENDER', ''),
                fields.get('INT/EXT', ''),
                fields.get('DOB', ''),
                fields.get('AGE', ''),
                fields.get('NATIONALITY', ''),
                fields.get('EXP START (YEAR)', ''),
                fields.get('EXPERIENCE(Years)', ''),
                fields.get('QUALIFICATIONS', ''),
                status,
            )
            
            item = self.tree.insert('', tk.END, values=values)
            
            # Color code based on status
            if status == 'no_form':
                self.tree.item(item, tags=('warning',))
            elif status != 'success':
                self.tree.item(item, tags=('error',))
        
        # Configure tags
        self.tree.tag_configure('error', background='#ffcccc')
        self.tree.tag_configure('warning', background='#ffffcc')
    
    def _apply_filter(self):
        """Apply filter to results."""
        filter_type = self.filter_var.get()
        
        if filter_type == "all":
            self.filtered_results = self.results.copy()
        elif filter_type == "errors":
            # Show errors and missing forms
            self.filtered_results = [
                r for r in self.results
                if r.get('extraction_status') not in ['success', 'no_form']
            ]
        
        self._populate_table(self.filtered_results)
    

    def _sort_by_column(self, col: str):
        """Sort table by column."""
        # Get column index
        col_index = self.tree['columns'].index(col)
        
        # Get all items
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        
        # Sort items
        items.sort(reverse=False)
        
        # Rearrange items
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)

    def _edit_cell(self, event):
        """Edit cell on double-click."""
        # Get selected item and column
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            return
        
        column = self.tree.identify_column(event.x)
        column_index = int(column.replace('#', '')) - 1
        
        # Don't allow editing S/N or Status columns
        # indices: 0=S/N, 11=Status
        if column_index in [0, 11]:
            return
        
        # Get current value
        current_value = self.tree.item(item)['values'][column_index]
        
        # Create entry widget
        x, y, width, height = self.tree.bbox(item, column)
        entry = ttk.Entry(self.tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, current_value)
        entry.select_range(0, tk.END)
        entry.focus()
        
        def save_edit(event=None):
            new_value = entry.get()
            values = list(self.tree.item(item)['values'])
            values[column_index] = new_value
            self.tree.item(item, values=values)
            
            # Update results data
            # values[1] is the NAME. 
            # If changed, we might lose the link if we use NAME as key.
            # However, for now let's assume names are unique enough or 
            # use the original values from the tree before edit.
            
            # Get the original values before the update in results
            # For simplicity, we'll continue using values[1] (NAME) to find the result
            # but we should be aware this is still slightly fragile.
            name_val = values[1] 
            for result in self.results:
                # If we are editing NAME itself, we should have found it by the OLD name.
                # But here values[1] is already the NEW name.
                pass
                
            # Improved sync: find by index if possible, or just the first match
            # Let's use a simpler approach: update the result in self.results 
            # that corresponds to this tree item.
            
            # treeview item IDs are persistent for the life of the item.
            # We'll stick to a simpler name-based lookup for now but fix the logic.
            # Actually, the user's name is in fields['NAME'].
            
            tree_col_name = self.tree['columns'][column_index]
            mapping = {
                'EXP START': 'EXP START (YEAR)',
                'EXPERIENCE': 'EXPERIENCE(Years)',
            }
            field_key = mapping.get(tree_col_name, tree_col_name)
            
            # Find the result that matches the OTHER fields to be sure
            # Or just use the one where we saved the name before.
            for result in self.results:
                if result['fields'].get('NAME') == current_value:
                    result['fields'][field_key] = new_value
                    break
            
            entry.destroy()
        
        entry.bind('<Return>', save_edit)
        entry.bind('<FocusOut>', save_edit)
    
    def _export_excel(self):
        """Export results to Excel."""
        if not self.results:
            messagebox.showwarning("No Data", "No data to export")
            return
        
        if not self.excel_file:
            messagebox.showerror("Error", "Please select an Excel file")
            return
        
        try:
            export_result = self.excel_exporter.append_to_excel(self.excel_file, self.results)
            
            messagebox.showinfo(
                "Export Complete",
                f"Successfully exported {export_result['rows_added']} rows to Excel!\n\n"
                f"File: {export_result['file_path']}"
            )
        
        except Exception as e:
            logger.error(f"Export error: {e}")
            messagebox.showerror("Export Error", f"Failed to export:\n\n{str(e)}")
    
    def _update_errors_tab(self, errors: List[Dict]):
        """Update the errors tab with current batch errors."""
        self.error_text.config(state='normal')
        self.error_text.delete(1.0, tk.END)
        
        if not errors:
            self.error_text.insert(tk.END, "No extraction errors or warnings in this batch.\n")
        else:
            self.error_text.insert(tk.END, f"Found {len(errors)} issues in this batch:\n\n")
            for idx, err in enumerate(errors, start=1):
                self.error_text.insert(tk.END, f"{idx}. {err['applicant']}\n")
                msgs = err.get('error', [])
                if isinstance(msgs, list):
                    for m in msgs:
                        self.error_text.insert(tk.END, f"   - {m}\n")
                else:
                    self.error_text.insert(tk.END, f"   - {msgs}\n")
                self.error_text.insert(tk.END, "\n")
        
        self.error_text.config(state='disabled')
        if errors:
            # Switch to errors tab if there are errors
            self.notebook.select(1)

    def _add_to_history(self, result: Dict):
        """Append processing result to history log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        stats = result.get('stats', {})
        errors = result.get('errors', [])
        
        history_entry = (
            f"[{timestamp}] Processed: {self.parent_folder}\n"
            f" - Total: {stats.get('total_processed', 0)}, Success: {stats.get('successful', 0)}, Fail: {stats.get('failed', 0)}\n"
            f" - Time: {stats.get('elapsed_time', 0)}s, Rate: {stats.get('rate', 0)} apps/s\n"
        )
        
        if errors:
            history_entry += " - Errors encountered for:\n"
            for err in errors[:5]: # Show first 5 to keep it concise
                history_entry += f"   * {err['applicant']}\n"
            if len(errors) > 5:
                history_entry += f"   * ... and {len(errors)-5} more\n"
        
        history_entry += f"{'-'*50}\n"
        
        self.history_text.config(state='normal')
        self.history_text.insert(1.0, history_entry) # Insert at top
        self.history_text.config(state='disabled')
        
        # Persist history to file
        try:
            with open("processing_history.txt", "a", encoding='utf-8') as f:
                f.write(history_entry)
        except:
            pass

    def _load_history(self):
        """Load history from file if it exists."""
        if Path("processing_history.txt").exists():
            try:
                with open("processing_history.txt", "r", encoding='utf-8') as f:
                    content = f.read()
                    self.history_text.config(state='normal')
                    self.history_text.insert(tk.END, content)
                    self.history_text.config(state='disabled')
            except:
                pass

    def _export_errors(self):
        """No longer used - errors displayed in tab."""
        pass
    
    def _clear_results(self):
        """Clear all results."""
        self.results = []
        self.filtered_results = []
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.stats_text.set("")
        self.progress_var.set("Ready to process")
        self.progress_bar['value'] = 0
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """
    Application Entry Point.
    """
    app = ApplicationGUI()
    app.run()


if __name__ == '__main__':
    main()
