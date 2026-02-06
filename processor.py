"""
Main processing engine with progress tracking and error handling.
"""

import logging
import time
from typing import List, Dict, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from scanner import FolderScanner
from extractor import FieldExtractor

import json
import hashlib

logger = logging.getLogger(__name__)


class ApplicationProcessor:
    """Main processor for batch application extraction."""
    
    def __init__(self, max_workers: int = 4):
        self.scanner = FolderScanner()
        self.extractor = FieldExtractor()
        self.max_workers = max_workers
        
        self.total_processed = 0
        self.successful = 0
        self.failed = 0
        self.errors = []
        self.cache = {}
        self.cache_file = None

    def _load_cache(self, parent_folder: str):
        """Load cache for the parent folder."""
        # Create a unique cache file based on parent folder hash to avoid collisions
        folder_hash = hashlib.md5(parent_folder.encode()).hexdigest()
        self.cache_file = Path(parent_folder) / f".processing_cache_{folder_hash}.json"
        
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                logger.info(f"Loaded cache with {len(self.cache)} entries")
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                self.cache = {}
        else:
            self.cache = {}

    def _save_cache(self):
        """Save current cache to disk."""
        if self.cache_file:
            try:
                with open(self.cache_file, 'w') as f:
                    json.dump(self.cache, f)
            except Exception as e:
                logger.warning(f"Failed to save cache: {e}")
        
    def process_applications(
        self,
        parent_folder: str,
        progress_callback: Optional[Callable] = None,
    ) -> Dict:
        """
        Process all applications in parent folder.
        
        Args:
            parent_folder: Path to folder containing applicant subfolders
            progress_callback: Function to call with progress updates
                              Signature: callback(current, total, message)
        
        Returns:
            Dictionary with processing results
        """
        logger.info(f"Starting batch processing: {parent_folder}")
        start_time = time.time()
        
        # Reset counters
        self.total_processed = 0
        self.successful = 0
        self.failed = 0
        self.errors = []
        
        # Scan folders
        if progress_callback:
            progress_callback(0, 0, "Scanning folders...")
        
        # Load cache
        self._load_cache(parent_folder)
        
        applicants = self.scanner.scan_folders(parent_folder)
        total_applicants = len(applicants)
        
        if total_applicants == 0:
            return {
                'status': 'error',
                'message': 'No applicant folders found',
                'results': [],
                'stats': self._get_stats(0),
            }
        
        logger.info(f"Found {total_applicants} applicant folders")
        
        # Process applications
        results = []
        
        # Use thread pool for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_applicant = {
                executor.submit(self._process_single_application, applicant): applicant
                for applicant in applicants
            }
            
            # Process completed tasks
            for future in as_completed(future_to_applicant):
                applicant = future_to_applicant[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    self.total_processed += 1
                    
                    if result['extraction_status'] == 'success':
                        self.successful += 1
                    else:
                        self.failed += 1
                        self.errors.append({
                            'applicant': applicant['applicant_name'],
                            'error': result.get('error_message', 'Unknown error'),
                        })
                    
                    # Update cache if successful
                    if result['extraction_status'] == 'success':
                        self.cache[applicant['folder_path']] = result
                        # Save cache periodically (e.g., every 10 updates) to avoid too much I/O
                        if self.total_processed % 10 == 0:
                            self._save_cache()
                    
                    # Progress update
                    if progress_callback:
                        elapsed = time.time() - start_time
                        rate = self.total_processed / elapsed if elapsed > 0 else 0
                        remaining = (total_applicants - self.total_processed) / rate if rate > 0 else 0
                        
                        message = (
                            f"Processing {applicant['applicant_name']} "
                            f"({self.total_processed}/{total_applicants}) - "
                            f"~{int(remaining)}s remaining"
                        )
                        progress_callback(self.total_processed, total_applicants, message)
                
                except Exception as e:
                    logger.error(f"Error processing {applicant['applicant_name']}: {e}")
                    self.failed += 1
                    self.errors.append({
                        'applicant': applicant['applicant_name'],
                        'error': str(e),
                    })
        
        elapsed_time = time.time() - start_time
        logger.info(f"Batch processing complete in {elapsed_time:.1f}s")
        
        # Final cache save
        self._save_cache()
        
        return {
            'status': 'complete',
            'results': results,
            'stats': self._get_stats(elapsed_time),
            'errors': self.errors,
        }
    
    def _process_single_application(self, applicant: Dict) -> Dict:
        """
        Process a single application.
        
        Args:
            applicant: Dictionary with applicant folder info
        
        Returns:
            Dictionary with extraction results
        """
        # Check cache first
        if applicant['folder_path'] in self.cache:
            return self.cache[applicant['folder_path']]

        result = {
            'applicant_name': applicant['applicant_name'],
            'folder_path': applicant['folder_path'],
            'extraction_status': 'pending',
            'error_message': None,
            'fields': {},
        }
        
        # Check if form exists
        if not applicant['application_form']:
            # No form found - include just the folder name
            result['extraction_status'] = 'no_form'
            result['error_message'] = 'Application form not found in folder'
            result['fields'] = {
                'NAME': applicant['applicant_name'],  # Use folder name
                'POSITION CODE': self.extractor.default_position_code,
                'GENDER': '',
                'INT/EXT': self.extractor.default_int_ext,
                'DOB': '',
                'AGE': '',
                'NATIONALITY': '',
                'EXP START (YEAR)': '',
                'EXPERIENCE(Years)': '',
                'QUALIFICATIONS': '',
            }
            return result
        
        try:
            # Extract data from form
            extraction = self.extractor.extract_from_file(applicant['application_form'])
            
            result['extraction_status'] = extraction['extraction_status']
            result['error_message'] = extraction['error_message']
            result['fields'] = extraction['fields']
            result['file_name'] = extraction['file_name']
            
            # If name is empty but we have folder name, use it
            if not result['fields'].get('NAME'):
                result['fields']['NAME'] = applicant['applicant_name']
            
        except Exception as e:
            logger.error(f"Error extracting from {applicant['application_form']}: {e}")
            result['extraction_status'] = 'error'
            result['error_message'] = str(e)
            # Even on error, include the folder name
            result['fields'] = {
                'NAME': applicant['applicant_name'],
                'POSITION CODE': self.extractor.default_position_code,
                'GENDER': '',
                'INT/EXT': self.extractor.default_int_ext,
                'DOB': '',
                'AGE': '',
                'NATIONALITY': '',
                'EXP START (YEAR)': '',
                'EXPERIENCE(Years)': '',
                'QUALIFICATIONS': '',
            }
        
        return result
    
    def _get_stats(self, elapsed_time: float) -> Dict:
        """Get processing statistics."""
        return {
            'total_processed': self.total_processed,
            'successful': self.successful,
            'failed': self.failed,
            'success_rate': round(self.successful / self.total_processed * 100, 1) if self.total_processed > 0 else 0,
            'elapsed_time': round(elapsed_time, 1),
            'rate': round(self.total_processed / elapsed_time, 2) if elapsed_time > 0 else 0,
        }
    
    def export_error_log(self, output_path: str):
        """Export error log to text file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("ECOWAS Application Processor - Error Log\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"Total Errors: {len(self.errors)}\n\n")
            
            for idx, error in enumerate(self.errors, start=1):
                f.write(f"{idx}. {error['applicant']}\n")
                f.write(f"   Error: {error['error']}\n\n")
        
        logger.info(f"Error log exported to {output_path}")
