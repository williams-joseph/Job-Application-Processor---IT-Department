"""
Main GUI application for ECOWAS Application Processor.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import logging
from pathlib import Path
from typing import List, Dict, Optional
import json

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


class ApplicationGUI:
    """Main GUI application."""
    
    def __init__(self):
        if THEMES_AVAILABLE:
            self.root = ThemedTk(theme="arc")
        else:
            self.root = tk.Tk()
        
        self.root.title("ECOWAS Application Processor")
        
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
        
    def _setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
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
        ttk.Button(control_frame, text="Export Error Log", command=self._export_errors).pack(side=tk.LEFT, padx=5)
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
        
        # === Section 4: Results Table ===
        table_frame = ttk.LabelFrame(main_frame, text="Extracted Data", padding="10")
        table_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Create treeview with scrollbars
        tree_scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        columns = ('S/N', 'Applicant', 'Name', 'DOB', 'Qualification', 'Nationality', 'Sex', 'Status')
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Configure columns
        column_widths = {
            'S/N': 60,
            'Applicant': 150,
            'Name': 150,
            'DOB': 100,
            'Qualification': 200,
            'Nationality': 100,
            'Sex': 60,
            'Status': 100,
        }
        
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_by_column(c))
            self.tree.column(col, width=column_widths[col], minwidth=50)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Double-click to edit
        self.tree.bind("<Double-1>", self._edit_cell)
        
        # === Section 5: Statistics ===
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.stats_text = tk.StringVar(value="No data processed yet")
        ttk.Label(stats_frame, textvariable=self.stats_text, justify=tk.LEFT).pack(anchor=tk.W)
    
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
                result.get('applicant_name', ''),
                fields.get('Name', ''),
                fields.get('Date of Birth', ''),
                fields.get('Qualification', ''),
                fields.get('Nationality', ''),
                fields.get('Sex', ''),
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
        
    def _edit_cell(self, event):
        """Edit cell on double-click."""
        # Get selected item and column
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            return
        
        column = self.tree.identify_column(event.x)
        column_index = int(column.replace('#', '')) - 1
        
        # Don't allow editing S/N, Applicant, or Status columns
        # indices: 0=S/N, 1=Applicant, 7=Status
        if column_index in [0, 1, 7]:
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
            # values[1] is the Applicant Name
            applicant_name = values[1]
            for result in self.results:
                if result.get('applicant_name') == applicant_name:
                    field_name = self.tree['columns'][column_index]
                    if field_name in ['Name', 'Date of Birth', 'Qualification', 'Nationality', 'Sex']:
                        result['fields'][field_name] = new_value
                        # Update specific field keys if they match the column name text
                        # The column names in tree are: S/N, Applicant, Name, DOB, Qualification, Nationality, Sex, Status
                        # The keys in result['fields'] are: Name, Date of Birth, Qualification, Nationality, Sex
                        
                        # Mapping column name to field key if they differ
                        key_map = {'DOB': 'Date of Birth'}
                        actual_key = key_map.get(field_name, field_name)
                        result['fields'][actual_key] = new_value
            
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
    
    def _export_errors(self):
        """Export error log."""
        if not self.processor.errors:
            messagebox.showinfo("No Errors", "No errors to export")
            return
        
        file = filedialog.asksaveasfilename(
            title="Save Error Log",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file:
            try:
                self.processor.export_error_log(file)
                messagebox.showinfo("Export Complete", f"Error log saved to:\n{file}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to save error log:\n\n{str(e)}")
    
    def _clear_results(self):
        """Clear all results."""
        self.results = []
        self.filtered_results = []
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.stats_text.set("No data processed yet")
        self.progress_var.set("Ready to process")
        self.progress_bar['value'] = 0
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


class SplashScreen:
    """
    Splash screen window displayed during application startup.
    
    Displays:
    - ECOWAS CCJ Logo
    - Application Name
    - Department Name
    - Indeterminate progress bar
    """
    def __init__(self, root):
        self.root = root
        # Remove standard window title bar and borders for a cleaner look
        self.root.overrideredirect(True)
        
        # Calculate position to center the splash screen on the monitor
        width = 600
        height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.root.configure(bg='#004d40')  # ECOWAS Green background
        
        # Main Layout Frame
        frame = tk.Frame(self.root, bg='#004d40')
        frame.pack(expand=True, fill='both')
        
        # 1. Load and Display Logo (The Mockup)
        try:
            image_path = Path("logo.png")
            if image_path.exists():
                pil_image = Image.open(image_path)
                # Resize image to fit nicely within the 600x400 window
                # preserving aspect ratio
                pil_image.thumbnail((560, 320)) 
                self.logo_image = ImageTk.PhotoImage(pil_image)
                logo_label = tk.Label(frame, image=self.logo_image, bg='#004d40')
                logo_label.pack(expand=True, pady=10)
        except Exception as e:
            logger.error(f"Could not load logo: {e}")
        
        # 2. Progress Bar Background Style
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Splash.Horizontal.TProgressbar", 
            background="#ffeb3b", 
            troughcolor="#00695c", 
            bordercolor="#004d40",
            thickness=10
        )
        
        # 3. Loading Text (Subtle at the bottom)
        self.loading_label = tk.Label(
            frame, 
            text="Initialising Job Application Processor...", 
            font=("Segoe UI", 9, "italic"), 
            bg="#004d40", 
            fg="#b2dfdb"
        ).pack(side=tk.BOTTOM, pady=(0, 5))
        
        # 4. Progress Bar
        self.progress = ttk.Progressbar(frame, mode='indeterminate', style="Splash.Horizontal.TProgressbar")
        self.progress.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 20))
        self.progress.start(15)

def main():
    """
    Application Entry Point.
    
    Flow:
    1. Show Splash Screen (15 seconds)
    2. Initialize Main GUI
    3. Launch Main Event Loop
    """
    # Create the root window for the splash screen
    splash_root = tk.Tk()
    splash = SplashScreen(splash_root)
    
    def launch_main_app():
        """Destroy splash and launch main application."""
        # Stop the progress bar before destruction to prevent "application has been destroyed" errors
        try:
            splash.progress.stop()
        except Exception:
            pass
            
        splash_root.destroy()
        
        # Initialize the main application
        app = ApplicationGUI()
        app.run()
        
    # Schedule main app launch after 15000ms (15 seconds)
    splash_root.after(15000, launch_main_app)
    
    # Start the splash screen event loop
    splash_root.mainloop()


if __name__ == '__main__':
    main()
