"""
Dataset Download Module
Handles downloading datasets from URLs and various sources
"""

import os
import logging
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import zipfile
import tarfile

logger = logging.getLogger(__name__)


class DatasetDownloader:
    """Download datasets from URLs and various sources"""
    
    def __init__(self, work_dir: str = "./data"):
        """
        Initialize the downloader
        
        Args:
            work_dir: Working directory for storing downloaded datasets
        """
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"DatasetDownloader initialized with work_dir: {self.work_dir}")
    
    def download_from_url(self, url: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Download a dataset from a URL
        
        Args:
            url: URL to download from
            filename: Optional filename (if not provided, extracted from URL)
            
        Returns:
            Dictionary with download results: {'success': bool, 'path': str, 'size': int, 'error': str}
        """
        try:
            logger.info(f"Downloading from URL: {url}")
            
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {
                    'success': False,
                    'error': f"Invalid URL: {url}",
                    'path': None
                }
            
            # Determine filename
            if not filename:
                filename = os.path.basename(parsed_url.path) or "dataset"
                # If no extension, try to get from Content-Type header
            
            # Create downloads directory
            downloads_dir = self.work_dir / "downloads"
            downloads_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = downloads_dir / filename
            
            # Download with progress
            print(f"Downloading {url}...")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get file size if available
            total_size = int(response.headers.get('content-length', 0))
            
            # Download file
            downloaded = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rProgress: {percent:.1f}%", end='', flush=True)
            
            print()  # New line after progress
            
            file_size = file_path.stat().st_size
            
            # Try to extract if it's a compressed file
            extracted_path = self._extract_if_needed(file_path)
            
            logger.info(f"Downloaded to: {extracted_path or file_path}")
            
            return {
                'success': True,
                'path': str(extracted_path) if extracted_path else str(file_path),
                'size': file_size,
                'original_path': str(file_path),
                'extracted': extracted_path is not None
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Download error: {e}")
            return {
                'success': False,
                'error': f"Download failed: {str(e)}",
                'path': None
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'path': None
            }
    
    def _extract_if_needed(self, file_path: Path) -> Optional[Path]:
        """Extract compressed files if needed"""
        try:
            # Check file extension
            ext = file_path.suffix.lower()
            
            extract_dir = file_path.parent / file_path.stem
            extract_dir.mkdir(exist_ok=True)
            
            if ext == '.zip':
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                logger.info(f"Extracted ZIP to: {extract_dir}")
                return extract_dir
            
            elif ext in ['.tar', '.gz', '.bz2']:
                mode = 'r'
                if ext == '.gz':
                    mode = 'r:gz'
                elif ext == '.bz2':
                    mode = 'r:bz2'
                
                with tarfile.open(file_path, mode) as tar_ref:
                    tar_ref.extractall(extract_dir)
                logger.info(f"Extracted TAR to: {extract_dir}")
                return extract_dir
            
            # Not a compressed file, return None
            return None
            
        except Exception as e:
            logger.warning(f"Could not extract file: {e}")
            return None
    
    def download_huggingface(self, dataset_id: str, subset: Optional[str] = None) -> Dict[str, Any]:
        """
        Download a dataset from HuggingFace
        
        Args:
            dataset_id: HuggingFace dataset identifier
            subset: Optional subset name
            
        Returns:
            Dictionary with download results
        """
        try:
            from datasets import load_dataset
            
            logger.info(f"Downloading HuggingFace dataset: {dataset_id}")
            
            # Create dataset directory
            dataset_dir = self.work_dir / "huggingface" / dataset_id.replace("/", "_")
            dataset_dir.mkdir(parents=True, exist_ok=True)
            
            # Load dataset
            if subset:
                dataset = load_dataset(dataset_id, subset)
            else:
                dataset = load_dataset(dataset_id)
            
            # Save dataset
            if isinstance(dataset, dict):
                # Multiple splits
                for split_name, split_data in dataset.items():
                    split_path = dataset_dir / split_name
                    split_data.save_to_disk(str(split_path))
            else:
                # Single split
                dataset.save_to_disk(str(dataset_dir))
            
            logger.info(f"Dataset saved to: {dataset_dir}")
            
            return {
                'success': True,
                'path': str(dataset_dir),
                'size': sum(f.stat().st_size for f in dataset_dir.rglob('*') if f.is_file()),
                'source': 'huggingface'
            }
            
        except ImportError:
            return {
                'success': False,
                'error': "datasets library not installed. Install with: pip install datasets",
                'path': None
            }
        except Exception as e:
            logger.error(f"Error downloading HuggingFace dataset: {e}")
            return {
                'success': False,
                'error': str(e),
                'path': None
            }
    
    def download(self, source: str, url_or_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generic download method that determines source type
        
        Args:
            source: Source type ('url', 'huggingface', or auto-detect)
            url_or_id: URL or dataset identifier
            
        Returns:
            Dictionary with download results
        """
        if not url_or_id:
            return {
                'success': False,
                'error': "No URL or dataset ID provided",
                'path': None
            }
        
        # Auto-detect source if not specified
        if source == 'auto' or not source:
            if url_or_id.startswith('http://') or url_or_id.startswith('https://'):
                source = 'url'
            elif '/' in url_or_id or 'huggingface.co' in url_or_id.lower():
                source = 'huggingface'
            else:
                source = 'url'  # Default to URL
        
        if source == 'url':
            return self.download_from_url(url_or_id)
        elif source == 'huggingface':
            # Extract dataset ID from URL if needed
            if 'huggingface.co/datasets/' in url_or_id:
                dataset_id = url_or_id.split('huggingface.co/datasets/')[-1].split('/')[0]
            else:
                dataset_id = url_or_id
            return self.download_huggingface(dataset_id)
        else:
            return {
                'success': False,
                'error': f"Unknown source type: {source}",
                'path': None
            }