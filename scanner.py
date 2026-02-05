"""
File system operations for scanning applicant folders.
"""

import os
from pathlib import Path
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class FolderScanner:
    """Scans parent folder and locates application forms."""
    
    APPLICATION_FORM_NAMES = [
        'application form',
        'application',
        'form',
        'applicant form',
    ]
    
    SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.doc', '.jpg', '.jpeg', '.png', '.tiff', '.bmp']
    
    def __init__(self):
        pass
    
    def scan_folders(self, parent_folder: str) -> List[Dict]:
        """
        Scan parent folder for applicant subfolders.
        
        Args:
            parent_folder: Path to parent folder containing applicant folders
            
        Returns:
            List of dictionaries with applicant folder info
        """
        parent_path = Path(parent_folder)
        
        if not parent_path.exists():
            raise ValueError(f"Parent folder does not exist: {parent_folder}")
        
        if not parent_path.is_dir():
            raise ValueError(f"Path is not a directory: {parent_folder}")
        
        applicants = []
        
        # Get all subdirectories
        for item in parent_path.iterdir():
            if item.is_dir():
                applicant_info = {
                    'folder_path': str(item),
                    'applicant_name': item.name,
                    'application_form': None,
                    'status': 'pending',
                    'error': None,
                }
                
                # Try to find application form
                form_path = self.find_application_form(str(item))
                if form_path:
                    applicant_info['application_form'] = form_path
                else:
                    applicant_info['status'] = 'no_form'
                    applicant_info['error'] = 'Application form not found'
                
                applicants.append(applicant_info)
        
        logger.info(f"Found {len(applicants)} applicant folders")
        return applicants
    
    def find_application_form(self, folder_path: str) -> Optional[str]:
        """
        Look for application form in folder.
        
        Selection hierarchy:
        1. Score (matches 'application', 'form' keywords)
        2. File size (larger files preferred, likely specific form)
        3. Recency (newer files preferred)
        
        Args:
            folder_path: Path to applicant folder
            
        Returns:
            Path to application form or None if not found
        """
        folder = Path(folder_path)
        
        if not folder.exists() or not folder.is_dir():
            return None
        
        # Collect all files with supported extensions
        candidates = []
        
        for file in folder.iterdir():
            if file.is_file() and file.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                file_name_lower = file.stem.lower()
                
                # Score based on keyword matches
                score = 0
                for keyword in self.APPLICATION_FORM_NAMES:
                    if keyword in file_name_lower:
                        score += 3  # High weight for exact keyword
                    elif keyword in file_name_lower.replace(' ', ''):
                         score += 1 # Lower weight for partial/compressed match (e.g., applicationform)

                # Get file metadata
                try:
                    stats = file.stat()
                    size = stats.st_size
                    mtime = stats.st_mtime
                except Exception:
                    size = 0
                    mtime = 0

                candidates.append({
                    'path': str(file),
                    'score': score,
                    'size': size,
                    'mtime': mtime
                })
        
        # Return highest scoring file
        if candidates:
            # Sort by: Score (desc), Size (desc), Mtime (desc)
            # We prioritize explicit keywords first. If tied, pick largest file (likely the scan).
            # If still tied, pick newest.
            candidates.sort(key=lambda x: (x['score'], x['size'], x['mtime']), reverse=True)
            return candidates[0]['path']
        
        return None
    
    def get_folder_statistics(self, parent_folder: str) -> Dict:
        """
        Get statistics about the folder structure.
        
        Returns:
            Dictionary with folder stats
        """
        applicants = self.scan_folders(parent_folder)
        
        stats = {
            'total_folders': len(applicants),
            'with_forms': sum(1 for a in applicants if a['application_form']),
            'without_forms': sum(1 for a in applicants if not a['application_form']),
            'file_types': {},
        }
        
        # Count file types
        for applicant in applicants:
            if applicant['application_form']:
                ext = Path(applicant['application_form']).suffix.lower()
                stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
        
        return stats
