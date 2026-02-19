"""
Download Agent for Geospatial Data
Handles downloading geospatial datasets from various sources
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import requests
import json
import re
import os

from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)


class DownloadAgent:
    """Agent for downloading geospatial datasets"""
    
    def __init__(
        self,
        llm: BaseChatModel,
        work_dir: Path = None
    ):
        """
        Initialize download agent
        
        Args:
            llm: Language model instance
            work_dir: Working directory

        """
        self.llm = llm
        self.work_dir = work_dir or Path("./geospatial_data")
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.downloads_dir = self.work_dir / "downloads"
        self.downloads_dir.mkdir(exist_ok=True)
    
    def execute(
        self,
        task_description: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute download task
        
        Args:
            task_description: Description of download task
            parameters: Download parameters
            context: Context from previous steps (e.g., search results)
            
        Returns:
            Download results
        """
        logger.info(f"Executing download: {task_description}")
        
        downloaded_data = {}
        
        # Check for direct URL in parameters
        if "url" in parameters:
            # Single URL
            url = parameters["url"]
            if isinstance(url, list):
                url = url[0]  # Take first URL if list
            
            # Check if it's a GitHub directory URL
            # Note: URLs ending with / are directories, even if they have /blob/ in them
            github_info = self._extract_github_repo_info(url)
            if github_info and (url.endswith("/") or "/tree/" in url or ("/blob/" not in url and github_info.get("path"))):
                # It's a directory (tree) or root with path, not a single file (blob)
                logger.info(f"Detected GitHub directory: {github_info['owner']}/{github_info['repo']}/{github_info['path']}")
                # Extract file extensions from task description if mentioned, otherwise download all files
                file_extensions = None
                if "csv" in task_description.lower():
                    file_extensions = [".csv"]
                elif "json" in task_description.lower():
                    file_extensions = [".json"]
                result = self._download_from_github_directory(github_info, file_extensions)
                if result:
                    folder_name = Path(github_info['path']).name if github_info['path'] else github_info['repo']
                    downloaded_data[f"{github_info['owner']}_{github_info['repo']}_{folder_name}"] = str(result)
                    return {
                        "downloaded_data": downloaded_data,
                        "count": len(downloaded_data)
                    }
            
            # Check if it's a Zenodo URL
            zenodo_record_id = self._extract_zenodo_record_id(url)
            if zenodo_record_id:
                logger.info(f"Detected Zenodo record: {zenodo_record_id}")
                result = self._download_from_zenodo(zenodo_record_id, url)
                if result:
                    downloaded_data[f"zenodo_{zenodo_record_id}"] = str(result)
                    return {
                        "downloaded_data": downloaded_data,
                        "count": len(downloaded_data)
                    }
            
            # Check if it's a HuggingFace URL (dataset or model)
            hf_repo_id = self._extract_huggingface_dataset_id(url)
            if hf_repo_id:
                logger.info(f"Detected HuggingFace repository: {hf_repo_id}")
                # Determine if it's a dataset or model
                is_dataset = "/datasets/" in url.lower()
                result = self._download_from_huggingface({
                    "name": hf_repo_id, 
                    "source": url,
                    "repo_type": "dataset" if is_dataset else "model"
                })
                if result:
                    downloaded_data[hf_repo_id.replace("/", "_")] = str(result)
                    return {
                        "downloaded_data": downloaded_data,
                        "count": len(downloaded_data)
                    }
            
            # Regular URL download
            result = self._download_from_url(url)
            if result:
                downloaded_data[Path(url).name] = str(result)
                return {
                    "downloaded_data": downloaded_data,
                    "count": len(downloaded_data)
                }
        
        # Check for multiple URLs
        if "urls" in parameters:
            urls = parameters["urls"]
            if not isinstance(urls, list):
                urls = [urls]
            for url in urls:
                # Check if it's a Zenodo URL
                zenodo_record_id = self._extract_zenodo_record_id(url)
                if zenodo_record_id:
                    result = self._download_from_zenodo(zenodo_record_id, url)
                    if result:
                        downloaded_data[f"zenodo_{zenodo_record_id}"] = str(result)
                    continue
                
                # Check if it's a HuggingFace URL (dataset or model)
                hf_repo_id = self._extract_huggingface_dataset_id(url)
                if hf_repo_id:
                    is_dataset = "/datasets/" in url.lower()
                    result = self._download_from_huggingface({
                        "name": hf_repo_id, 
                        "source": url,
                        "repo_type": "dataset" if is_dataset else "model"
                    })
                    if result:
                        downloaded_data[hf_repo_id.replace("/", "_")] = str(result)
                else:
                    result = self._download_from_url(url)
                    if result:
                        downloaded_data[Path(url).name] = str(result)
            if downloaded_data:
                return {
                    "downloaded_data": downloaded_data,
                    "count": len(downloaded_data)
                }
        
        
        # Try to extract URL from task description
        import re
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls_in_description = re.findall(url_pattern, task_description)
        if urls_in_description:
            logger.info(f"Found URL in task description: {urls_in_description[0]}")
            url = urls_in_description[0]
            
            # Check if it's a GitHub directory URL
            # Note: URLs ending with / are directories, even if they have /blob/ in them
            github_info = self._extract_github_repo_info(url)
            if github_info and (url.endswith("/") or "/tree/" in url or "/blob/" not in url):
                logger.info(f"Detected GitHub directory: {github_info['owner']}/{github_info['repo']}/{github_info['path']}")
                # Extract file extensions from task description if mentioned
                file_extensions = None
                if "csv" in task_description.lower():
                    file_extensions = [".csv"]
                elif "json" in task_description.lower():
                    file_extensions = [".json"]
                result = self._download_from_github_directory(github_info, file_extensions)
                if result:
                    folder_name = Path(github_info['path']).name if github_info['path'] else github_info['repo']
                    downloaded_data[f"{github_info['owner']}_{github_info['repo']}_{folder_name}"] = str(result)
                    return {
                        "downloaded_data": downloaded_data,
                        "count": len(downloaded_data)
                    }
            
            # Check if it's a Zenodo URL
            zenodo_record_id = self._extract_zenodo_record_id(url)
            if zenodo_record_id:
                result = self._download_from_zenodo(zenodo_record_id, url)
                if result:
                    downloaded_data[f"zenodo_{zenodo_record_id}"] = str(result)
                    return {
                        "downloaded_data": downloaded_data,
                        "count": len(downloaded_data)
                    }
            
            # Check if it's a HuggingFace URL (dataset or model)
            hf_repo_id = self._extract_huggingface_dataset_id(url)
            if hf_repo_id:
                is_dataset = "/datasets/" in url.lower()
                result = self._download_from_huggingface({
                    "name": hf_repo_id, 
                    "source": url,
                    "repo_type": "dataset" if is_dataset else "model"
                })
                if result:
                    downloaded_data[hf_repo_id.replace("/", "_")] = str(result)
                    return {
                        "downloaded_data": downloaded_data,
                        "count": len(downloaded_data)
                    }
            
            # Try GitHub blob URL conversion for regular URLs (single files)
            url = self._convert_github_blob_url(url)
            result = self._download_from_url(url)
            if result:
                downloaded_data[Path(url).name] = str(result)
                return {
                    "downloaded_data": downloaded_data,
                    "count": len(downloaded_data)
                }
        
        # Get datasets to download from context or parameters
        if context and "search_results" in context:
            datasets = context["search_results"]
        elif "dataset_ids" in parameters:
            # Reference to previous step results
            datasets = parameters["dataset_ids"]
        else:
            # Use LLM to determine what to download
            datasets = self._determine_downloads_with_llm(task_description, context)
        
        # Download each dataset
        for dataset in datasets[:parameters.get("limit", 5)]:
            try:
                source = dataset.get("source", "")
                name = dataset.get("name", "unknown")
                
                # Handle source as dict (from enhanced search results)
                source_url = None
                if isinstance(source, dict):
                    source_url = source.get("url", "")
                    source_str = source_url or str(source)
                else:
                    source_url = source if isinstance(source, str) else ""
                    source_str = source_url
                
                # Check if it's a HuggingFace URL
                if source_url and self._extract_huggingface_dataset_id(source_url):
                    path = self._download_from_huggingface(dataset)
                elif source_url and source_url.startswith("http"):
                    path = self._download_from_url(source_url, name)
                elif isinstance(source_str, str) and "huggingface" in source_str.lower():
                    path = self._download_from_huggingface(dataset)
                else:
                    # Use LLM to generate download code
                    path = self._download_with_llm(dataset)
                
                if path:
                    downloaded_data[name] = str(path)
            except Exception as e:
                logger.error(f"Failed to download {dataset.get('name', 'unknown')}: {e}")
                import traceback
                logger.debug(traceback.format_exc())
        
        return {
            "downloaded_data": downloaded_data,
            "count": len(downloaded_data)
        }
    
    
    def _extract_zenodo_record_id(self, url: str) -> Optional[str]:
        """Extract Zenodo record ID from URL
        
        Examples:
        - https://zenodo.org/records/6534637 -> 6534637
        - https://zenodo.org/record/123456 -> 123456
        - https://doi.org/10.5281/zenodo.6534637 -> 6534637
        """
        if "zenodo.org" in url.lower() or "zenodo" in url.lower():
            import re
            # Pattern: zenodo.org/records/RECORD_ID or zenodo.org/record/RECORD_ID
            record_match = re.search(r'zenodo\.org/(?:records|record)/(\d+)', url, re.IGNORECASE)
            if record_match:
                record_id = record_match.group(1)
                logger.info(f"Extracted Zenodo record ID: {record_id}")
                return record_id
            
            # Pattern for DOI: doi.org/10.5281/zenodo.RECORD_ID
            doi_match = re.search(r'zenodo\.(\d+)', url, re.IGNORECASE)
            if doi_match:
                record_id = doi_match.group(1)
                logger.info(f"Extracted Zenodo record ID from DOI: {record_id}")
                return record_id
        return None
    
    def _extract_huggingface_dataset_id(self, url: str) -> Optional[str]:
        """Extract HuggingFace dataset or model ID from URL
        
        Examples:
        - https://huggingface.co/datasets/HC-85/flood-prediction -> HC-85/flood-prediction (dataset)
        - https://huggingface.co/ibm-nasa-geospatial/Prithvi-EO-2.0-300M-TL-Sen1Floods11 -> ibm-nasa-geospatial/Prithvi-EO-2.0-300M-TL-Sen1Floods11 (model)
        - https://huggingface.co/user/model-name -> user/model-name (model)
        """
        if "huggingface.co" in url.lower():
            import re
            # Pattern for datasets: https://huggingface.co/datasets/USER/DATASET
            dataset_match = re.search(r'huggingface\.co/datasets/([^/]+/[^/\s?#]+)', url, re.IGNORECASE)
            if dataset_match:
                dataset_id = dataset_match.group(1)
                logger.info(f"Extracted HuggingFace dataset ID: {dataset_id}")
                return dataset_id
            
            # Pattern for models: https://huggingface.co/USER/MODEL (no /datasets/ prefix)
            # Exclude common paths like /spaces/, /docs/, etc.
            model_match = re.search(r'huggingface\.co/(?!datasets|spaces|docs|models|api)([^/]+/[^/\s?#]+)', url, re.IGNORECASE)
            if model_match:
                model_id = model_match.group(1)
                logger.info(f"Extracted HuggingFace model/repo ID: {model_id}")
                return model_id
        return None
    
    def _extract_github_repo_info(self, url: str) -> Optional[Dict[str, str]]:
        """Extract GitHub repository information from URL
        
        Returns:
            Dict with 'owner', 'repo', 'branch', 'path' or None if not a GitHub URL
        """
        if "github.com" not in url.lower():
            return None
        
        import re
        # Pattern: https://github.com/owner/repo/tree/branch/path
        # Pattern: https://github.com/owner/repo/blob/branch/path
        # Pattern: https://github.com/owner/repo (root)
        match = re.search(r'github\.com/([^/]+)/([^/]+)(?:/(?:tree|blob)/([^/]+)(?:/(.+))?)?', url)
        if match:
            owner = match.group(1)
            repo = match.group(2)
            branch = match.group(3)
            path = match.group(4) or ""  # Empty if root
            
            # If no branch specified but path exists, default to main
            if not branch and path:
                branch = "main"
            elif not branch:
                branch = "main"  # Default to main for root
            
            return {
                "owner": owner,
                "repo": repo,
                "branch": branch,
                "path": path
            }
        return None
    
    def _convert_github_blob_url(self, url: str) -> str:
        """Convert GitHub blob URL to raw URL (only for files, not directories)"""
        if "github.com" in url and "/blob/" in url:
            # Don't convert if it ends with / (it's a directory)
            if url.endswith("/"):
                logger.info(f"GitHub URL ends with /, treating as directory: {url}")
                return url  # Keep as-is, handle as directory
            
            # Convert: https://github.com/user/repo/blob/branch/path/file.ext
            # To: https://raw.githubusercontent.com/user/repo/branch/path/file.ext
            url = url.replace("github.com", "raw.githubusercontent.com")
            url = url.replace("/blob/", "/")
            logger.info(f"Converted GitHub blob URL to raw URL: {url}")
        return url
    
    def _download_from_github_directory(self, repo_info: Dict[str, str], file_extensions: List[str] = None) -> Optional[Path]:
        """Download all files from a GitHub directory
        
        Args:
            repo_info: Dict with 'owner', 'repo', 'branch', 'path'
            file_extensions: List of file extensions to download (e.g., ['.csv', '.json']). 
                           If None, downloads all files.
        
        Returns:
            Path to directory containing downloaded files
        """
        owner = repo_info["owner"]
        repo = repo_info["repo"]
        branch = repo_info["branch"]
        path = repo_info["path"]
        
        logger.info(f"Downloading GitHub directory: {owner}/{repo}/{path} (branch: {branch})")
        
        try:
            # Use GitHub API to list directory contents
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
            if branch:
                api_url += f"?ref={branch}"
            
            logger.info(f"Fetching directory contents from: {api_url}")
            
            headers = {"Accept": "application/vnd.github.v3+json"}
            response = requests.get(api_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            contents = response.json()
            
            # Handle both single file and directory responses
            if not isinstance(contents, list):
                contents = [contents]
            
            # Filter files by extension if specified
            if file_extensions:
                contents = [item for item in contents if any(item.get("name", "").endswith(ext) for ext in file_extensions)]
            
            if not contents:
                logger.warning(f"No files found matching extensions: {file_extensions}")
                return None
            
            logger.info(f"Found {len(contents)} file(s) to download")
            
            # Create save path
            folder_name = Path(path).name if path else repo
            save_path = self.downloads_dir / f"{owner}_{repo}_{folder_name}"
            save_path.mkdir(parents=True, exist_ok=True)
            
            downloaded_files = []
            
            # Download each file
            for item in contents:
                if item.get("type") != "file":
                    continue  # Skip subdirectories for now
                
                filename = item.get("name", "")
                download_url = item.get("download_url") or item.get("url", "")
                
                if not download_url:
                    # If no direct download URL, construct raw URL
                    file_path_in_repo = item.get("path", f"{path}/{filename}" if path else filename)
                    download_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path_in_repo}"
                
                logger.info(f"Downloading {filename}...")
                
                file_path = save_path / filename
                
                try:
                    file_response = requests.get(download_url, stream=True, timeout=60)
                    file_response.raise_for_status()
                    
                    with open(file_path, 'wb') as f:
                        for chunk in file_response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    downloaded_files.append(file_path)
                    logger.info(f"Downloaded {filename} to {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to download {filename}: {e}")
                    continue
            
            if downloaded_files:
                logger.info(f"Successfully downloaded {len(downloaded_files)} file(s) to {save_path}")
                return save_path
            else:
                logger.error("No files were downloaded")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch GitHub directory: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
        except Exception as e:
            logger.error(f"GitHub directory download failed: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def _is_html_content(self, content: bytes, content_type: str = None) -> bool:
        """Check if content is HTML"""
        if content_type and 'text/html' in content_type.lower():
            return True
        if not content:
            return False
        # Check first few bytes for HTML markers
        content_start = content[:1024].lower()
        html_markers = [b'<html', b'<!doctype html', b'<head', b'<body', b'<!doctype']
        return any(marker in content_start for marker in html_markers)
    
    def _cleanup_html_file(self, filepath: Path) -> None:
        """Delete HTML file that was accidentally downloaded"""
        try:
            if filepath.exists():
                filepath.unlink()
                logger.info(f"Removed HTML file: {filepath}")
        except Exception as e:
            logger.warning(f"Failed to remove HTML file {filepath}: {e}")
    
    def _download_from_url(self, url: str, name: str = None) -> Optional[Path]:
        """Download from direct URL"""
        try:
            # Convert GitHub blob URLs to raw URLs
            url = self._convert_github_blob_url(url)
            
            filename = name or Path(url).name
            # Clean filename (remove query parameters)
            if '?' in filename:
                filename = filename.split('?')[0]
            filepath = self.downloads_dir / filename
            
            logger.info(f"Downloading {url}...")
            
            # Add headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*'
            }
            
            response = requests.get(url, stream=True, timeout=60, headers=headers)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('Content-Type', '').lower()
            
            # Read first chunk to check if it's HTML
            first_chunk = b''
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        if not first_chunk:
                            first_chunk = chunk
                        f.write(chunk)
            
            # Check if downloaded content is HTML
            if self._is_html_content(first_chunk, content_type):
                logger.warning(f"Downloaded content appears to be HTML, not actual data file")
                # Clean up the HTML file
                self._cleanup_html_file(filepath)
                logger.info(f"Attempting to use source-specific download method for: {url}")
                # Try to use LLM to generate proper download code
                return self._download_with_source_specific_method(url, name)
            
            # Check file extension - if no extension or .html, might be wrong
            if filepath.suffix in ['', '.html', '.htm']:
                # Try to detect actual file type from content
                if self._is_html_content(first_chunk):
                    logger.warning(f"File appears to be HTML, trying source-specific method")
                    self._cleanup_html_file(filepath)
                    return self._download_with_source_specific_method(url, name)
            
            logger.info(f"Downloaded to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"URL download failed: {e}")
            return None
    
    
    def _download_from_zenodo(self, record_id: str, url: str = None) -> Optional[Path]:
        """Download dataset from Zenodo
        
        Args:
            record_id: Zenodo record ID (e.g., "6534637")
            url: Original URL (optional, for logging)
        
        Returns:
            Path to downloaded data
        """
        logger.info(f"Downloading Zenodo record: {record_id}")
        
        try:
            # Use Zenodo API to get file information
            api_url = f"https://zenodo.org/api/records/{record_id}"
            logger.info(f"Fetching record metadata from: {api_url}")
            
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            record_data = response.json()
            
            # Extract files from record
            files = record_data.get("files", [])
            if not files:
                logger.error(f"No files found in Zenodo record {record_id}")
                return None
            
            logger.info(f"Found {len(files)} file(s) in Zenodo record")
            
            # Create save path
            save_path = self.downloads_dir / f"zenodo_{record_id}"
            save_path.mkdir(parents=True, exist_ok=True)
            
            downloaded_files = []
            
            # Download each file
            for file_info in files:
                file_url = file_info.get("links", {}).get("self", "")
                filename = file_info.get("key", file_info.get("filename", "unknown"))
                file_size = file_info.get("size", 0)
                
                if not file_url:
                    logger.warning(f"No download URL for file: {filename}")
                    continue
                
                logger.info(f"Downloading {filename} ({file_size / (1024**3):.2f} GB)...")
                
                file_path = save_path / filename
                
                # Download with progress for large files
                response = requests.get(file_url, stream=True, timeout=300)
                response.raise_for_status()
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                downloaded_files.append(file_path)
                logger.info(f"Downloaded {filename} to {file_path}")
                
                # If it's a zip file, optionally extract it (non-fatal if extraction fails)
                if filename.endswith('.zip') and file_size < 50 * 1024**3:  # Extract if < 50GB
                    try:
                        logger.info(f"Attempting to extract {filename}...")
                        import zipfile
                        
                        # First, verify it's a valid zip file
                        try:
                            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                                # Test if zip file is valid
                                zip_ref.testzip()
                        except zipfile.BadZipFile:
                            logger.warning(f"{filename} is not a valid ZIP file, skipping extraction")
                        except Exception as e:
                            logger.warning(f"Could not verify ZIP file: {e}, skipping extraction")
                        else:
                            # If valid, try to extract
                            extract_path = save_path / filename.replace('.zip', '')
                            extract_path.mkdir(exist_ok=True)
                            
                            # Try different extraction methods
                            try:
                                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                                    zip_ref.extractall(extract_path)
                                logger.info(f"Successfully extracted to {extract_path}")
                            except zipfile.BadZipFile as e:
                                logger.warning(f"ZIP file appears corrupted or uses unsupported compression: {e}")
                                logger.info(f"Keeping original ZIP file at {file_path}")
                            except Exception as e:
                                logger.warning(f"Extraction failed: {e}")
                                logger.info(f"Keeping original ZIP file at {file_path}. You can extract it manually.")
                    except Exception as e:
                        logger.warning(f"Failed to extract {filename}: {e}")
                        logger.info(f"Keeping original ZIP file at {file_path}. You can extract it manually.")
            
            if downloaded_files:
                logger.info(f"Successfully downloaded {len(downloaded_files)} file(s) from Zenodo record {record_id}")
                logger.info(f"Files saved to: {save_path}")
                return save_path
            else:
                logger.error("No files were downloaded")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch Zenodo record: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
        except Exception as e:
            logger.error(f"Zenodo download failed: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            # Even if extraction failed, if files were downloaded, return the path
            if downloaded_files:
                logger.info(f"Note: Some files were downloaded but extraction may have failed. Files are at: {save_path}")
                return save_path
            return None
    
    def _download_with_source_specific_method(self, url: str, name: str = None) -> Optional[Path]:
        """Use source-specific method to download data (not HTML page)"""
        logger.info(f"Using source-specific download method for: {url}")
        
        # Check if it's Zenodo
        zenodo_record_id = self._extract_zenodo_record_id(url)
        if zenodo_record_id:
            return self._download_from_zenodo(zenodo_record_id, url)
        
        # Create a dataset dict for LLM download
        dataset = {
            "name": name or "dataset",
            "source": url
        }
        
        # Use LLM to generate proper download code
        return self._download_with_llm(dataset)
    
    def _download_from_huggingface(self, dataset: Dict[str, Any]) -> Optional[Path]:
        """Download from HuggingFace using huggingface-cli
        
        Args:
            dataset: Dict with 'name' (repo ID), 'source' (URL), and optionally 'repo_type'
                    Examples:
                    - {"name": "HC-85/flood-prediction", "repo_type": "dataset"}
                    - {"source": "https://huggingface.co/datasets/HC-85/flood-prediction", "repo_type": "dataset"}
                    - {"source": "https://huggingface.co/ibm-nasa-geospatial/model-name", "repo_type": "model"}
        """
        import subprocess
        import shutil
        
        # Extract repo ID and type
        repo_id = dataset.get("name", "")
        source = dataset.get("source", "")
        repo_type = dataset.get("repo_type", "dataset")  # Default to dataset
        
        # If source is a URL, try to extract repo ID from it
        if not repo_id and source:
            extracted_id = self._extract_huggingface_dataset_id(source)
            if extracted_id:
                repo_id = extracted_id
                # Determine repo type from URL
                if "/datasets/" in source.lower():
                    repo_type = "dataset"
                else:
                    repo_type = "model"
        
        # If still no repo ID, try to use source as-is
        if not repo_id:
            if "/datasets/" in source.lower():
                repo_id = source.replace("https://huggingface.co/datasets/", "").strip("/")
                repo_type = "dataset"
            else:
                repo_id = source.replace("https://huggingface.co/", "").strip("/")
                repo_type = "model"
        
        if not repo_id:
            logger.error("Could not determine HuggingFace repository ID")
            return None
        
        logger.info(f"Downloading HuggingFace {repo_type}: {repo_id}")
        
        # Check if huggingface-cli is available
        if not shutil.which("huggingface-cli"):
            logger.error("huggingface-cli not found. Install with: pip install huggingface_hub[cli]")
            # Fallback to huggingface_hub library
            return self._download_from_huggingface_original_files(repo_id, repo_type)
        
        # Create save path
        save_path = self.downloads_dir / repo_id.replace("/", "_")
        save_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Use huggingface-cli download command to get original files
            # Format: huggingface-cli download REPO_ID --local-dir LOCAL_DIR --repo-type TYPE
            cmd = [
                "huggingface-cli",
                "download",
                repo_id,
                "--local-dir",
                str(save_path),
                "--repo-type", repo_type  # dataset or model
            ]
            
            logger.info(f"Running command: {' '.join(cmd)}")
            logger.info(f"Downloading original format files (not just auto-converted Parquet)")
            
            # Run the command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout for large datasets
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully downloaded HuggingFace {repo_type} to {save_path}")
                logger.debug(f"Command output: {result.stdout}")
                
                # Verify we got files (not just empty directory)
                files = list(save_path.rglob("*"))
                files = [f for f in files if f.is_file()]
                if files:
                    logger.info(f"Downloaded {len(files)} files to {save_path}")
                else:
                    logger.warning(f"No files found in {save_path}, trying alternative method")
                    return self._download_from_huggingface_original_files(repo_id, repo_type, save_path)
                
                return save_path
            else:
                logger.error(f"huggingface-cli download failed: {result.stderr}")
                # Try alternative method for original files
                return self._download_from_huggingface_original_files(repo_id, repo_type, save_path)
                
        except subprocess.TimeoutExpired:
            logger.error(f"Download timeout for {repo_type} {repo_id}")
            return None
        except Exception as e:
            logger.error(f"HuggingFace download failed: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            # Try fallback method
            return self._download_from_huggingface_original_files(repo_id, repo_type, save_path)
    
    def _download_from_huggingface_original_files(self, repo_id: str, repo_type: str = "dataset", save_path: Path = None) -> Optional[Path]:
        """Download original format files using huggingface_hub library
        
        This downloads ALL files from the repository, including:
        - Original format files (CSV, JSON, etc.)
        - Auto-converted Parquet files (usually in .parquet/ subdirectory)
        - Metadata files (README.md, dataset_infos.json, etc.)
        
        Original files are typically in the root directory or data/ subdirectory.
        
        Args:
            repo_id: Repository ID (e.g., "HC-85/flood-prediction" or "ibm-nasa-geospatial/model-name")
            repo_type: "dataset" or "model"
            save_path: Optional save path, will create one if not provided
        """
        try:
            from huggingface_hub import snapshot_download
            
            if save_path is None:
                save_path = self.downloads_dir / repo_id.replace("/", "_")
            save_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Downloading all files (including originals) using huggingface_hub for {repo_type}: {repo_id}")
            
            # Use snapshot_download to get all files including originals
            # This downloads everything: original files + auto-converted Parquet
            downloaded_path = snapshot_download(
                repo_id=repo_id,
                repo_type=repo_type,  # "dataset" or "model"
                local_dir=str(save_path),
                local_dir_use_symlinks=False,  # Copy files, don't symlink
                # Download all files including originals
                ignore_patterns=None  # Don't ignore any files
            )
            
            logger.info(f"Downloaded all files to {downloaded_path}")
            
            # List downloaded files to show what we got
            files = list(Path(downloaded_path).rglob("*"))
            files = [f for f in files if f.is_file()]
            logger.info(f"Downloaded {len(files)} files total")
            
            # Log original format files (non-parquet)
            original_files = [f for f in files if not any(x in str(f) for x in ['.parquet', 'parquet/'])]
            if original_files:
                logger.info(f"Found {len(original_files)} original format files (non-Parquet)")
                # Show a few examples
                for f in original_files[:5]:
                    logger.debug(f"  - {f.relative_to(downloaded_path)}")
            
            return Path(downloaded_path)
            
        except ImportError:
            logger.error("huggingface_hub not installed. Install with: pip install huggingface_hub")
            return None
        except Exception as e:
            logger.error(f"Failed to download original files: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def _download_from_huggingface_fallback(self, repo_id: str, repo_type: str = "dataset") -> Optional[Path]:
        """Fallback method using huggingface_hub or datasets library"""
        # First try huggingface_hub for original files
        save_path = self.downloads_dir / repo_id.replace("/", "_")
        save_path.mkdir(parents=True, exist_ok=True)
        
        result = self._download_from_huggingface_original_files(repo_id, repo_type, save_path)
        if result:
            return result
        
        # If that fails and it's a dataset, try datasets library (but note: this may give Parquet format)
        if repo_type == "dataset":
            try:
                from datasets import load_dataset
                
                logger.info(f"Using datasets library as fallback for {repo_id}")
                logger.warning("Note: datasets library may load auto-converted Parquet format, not original files")
                
                # Load the dataset
                dataset_obj = load_dataset(repo_id)
                
                # Create save path
                save_path = self.downloads_dir / repo_id.replace("/", "_")
                save_path.mkdir(parents=True, exist_ok=True)
                
                # Save the dataset
                if isinstance(dataset_obj, dict):
                    # Multiple splits
                    for split_name, split_data in dataset_obj.items():
                        split_path = save_path / split_name
                        split_path.mkdir(parents=True, exist_ok=True)
                        split_data.save_to_disk(str(split_path))
                        logger.info(f"Saved split '{split_name}' to {split_path}")
                else:
                    # Single dataset
                    dataset_obj.save_to_disk(str(save_path))
                    logger.info(f"Saved dataset to {save_path}")
                
                logger.info(f"Successfully downloaded HuggingFace dataset to {save_path}")
                return save_path
                
            except ImportError:
                logger.error("datasets library not available. Install with: pip install datasets")
            except Exception as e:
                logger.error(f"Datasets library download failed: {e}")
                import traceback
                logger.debug(traceback.format_exc())
        else:
            # For models, we can't use datasets library
            logger.warning(f"Cannot use datasets library for models. Use huggingface_hub instead.")
        
        # Final fallback failed
        logger.error("All download methods failed. Install huggingface_hub: pip install huggingface_hub")
        return None
    
    def _download_with_llm(self, dataset: Dict[str, Any]) -> Optional[Path]:
        """Use LLM to generate download code for actual data files (not HTML pages)"""
        source = dataset.get("source", "")
        source_lower = source.lower() if isinstance(source, str) else str(source).lower()
        name = dataset.get("name", "dataset")
        
        # Provide source-specific guidance
        source_guidance = ""
        if "usgs" in source_lower or "earthexplorer" in source_lower:
            source_guidance = """
For USGS EarthExplorer:
- DO NOT download HTML pages. You need to use the USGS API or search for actual data files.
- Use the USGS EarthExplorer API: https://earthexplorer.usgs.gov/inventory/json
- Or search for direct download links to .tif, .hdf, .nc, .tar.gz files
- Example: Search for Landsat scenes, then download the actual .tar.gz or .tif files
- Use library: landsatxplore or eodag for easier access
- If URL is HTML, parse it or use API to find actual data file download links
"""
        elif "sentinel" in source_lower:
            source_guidance = """
For Sentinel Hub:
- DO NOT download HTML pages. Download actual .tif files.
- Use sentinelhub package (official SDK): pip install sentinelhub
  - Requires credentials: SENTINELHUB_CLIENT_ID and SENTINELHUB_CLIENT_SECRET
  - Example: from sentinelhub import SHConfig, SentinelHubRequest, DataCollection
- Register at: https://www.sentinel-hub.com/
- Supports Sentinel-1, Sentinel-2, Sentinel-3 data
"""
        elif "openstreetmap" in source_lower or "osm" in source_lower:
            source_guidance = """
For OpenStreetMap:
- DO NOT download HTML pages. Download actual .osm, .pbf, .shp, or .geojson files.
- Use osmnx library: pip install osmnx
- Example: import osmnx as ox; G = ox.graph_from_place("City Name"); ox.save_graphml(G, "file.graphml")
- Or download from Geofabrik: https://download.geofabrik.de/ (direct .osm.pbf or .shp.zip files)
- Or use Overpass API to query and download .osm or .geojson files
- For specific regions: Use Geofabrik's direct download links to .osm.pbf files
- Example Geofabrik URL: https://download.geofabrik.de/north-america/us/california-latest.osm.pbf
"""
        elif "natural earth" in source_lower:
            source_guidance = """
For Natural Earth:
- DO NOT download HTML pages. Download actual .shp, .geojson, or .zip files.
- Direct download links from naturalearthdata.com/downloads/
- Example: https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip
- Available formats: Shapefile (.shp.zip), GeoJSON, SQLite
- No authentication needed
"""
        elif "worldpop" in source_lower:
            source_guidance = """
For WorldPop:
- DO NOT download HTML pages. Download actual .tif, .zip, or .csv files.
- Direct download from worldpop.org or use API
- API: https://www.worldpop.org/rest/data
- Download links point to .tif (GeoTIFF) or .zip files
- Example: Download population density GeoTIFF files (.tif format)
"""
        elif "huggingface" in source_lower or "hf" in source_lower:
            source_guidance = """
For HuggingFace (datasets or models):
- DO NOT download HTML pages or parse HTML
- Use huggingface_hub.snapshot_download() to download all files including originals
- Example: from huggingface_hub import snapshot_download; snapshot_download(repo_id="USER/REPO", repo_type="dataset", local_dir="path")
- Or use huggingface-cli: huggingface-cli download USER/REPO --local-dir path --repo-type dataset
- For models: use repo_type="model" instead of "dataset"
- No authentication needed for public repositories
- This downloads ALL files including original format files (not just Parquet)
"""
        elif "zenodo" in source_lower:
            source_guidance = """
For Zenodo:
- DO NOT download HTML pages. Use Zenodo API to get actual file download links.
- Zenodo API: https://zenodo.org/api/records/RECORD_ID
- Extract record ID from URL: https://zenodo.org/records/6534637 -> record_id = "6534637"
- Get files from API response: record["files"] -> each file has "links.self" for download URL
- Download files directly using the download URLs from the API
- Example: 
  1. GET https://zenodo.org/api/records/6534637
  2. Extract files[0]["links"]["self"] to get download URL
  3. Download the file using requests.get(download_url, stream=True)
- Files are usually .zip, .tar.gz, or data files - download and extract if needed
"""
        elif "noaa" in source_lower or "ncdc" in source_lower:
            source_guidance = """
For NOAA:
- DO NOT download HTML pages. Download actual .csv, .nc, .grb, or .txt files.
- Use NOAA API or direct download links to data files
- Example: Download climate data as .csv or NetCDF (.nc) files
- API: https://www.ncdc.noaa.gov/cdo-web/webservices/v2
"""
        elif "nasa" in source_lower or "earthdata" in source_lower:
            source_guidance = """
For NASA Earthdata:
- DO NOT download HTML pages. Download actual .hdf, .nc, .tif, or .h5 files.
- Use NASA Earthdata API or direct download links
- Example: Download MODIS .hdf files or Landsat .tar.gz files
- May require authentication (NASA Earthdata account)
"""
        
        prompt = f"""Generate Python code to download this geospatial dataset as ACTUAL DATA FILES (not HTML pages):

Dataset: {json.dumps(dataset, indent=2)}
Source URL: {source if isinstance(source, str) else json.dumps(source)}

{source_guidance}

CRITICAL: The source URL might be an HTML page. You MUST:
1. Find the actual data download links (look for .tif, .shp, .zip, .pbf, .osm, .nc, .hdf, .csv, .geojson files)
2. Use appropriate APIs or libraries to access the real data
3. DO NOT download HTML pages - download actual data files

The code should:
1. Download ACTUAL DATA FILES (not HTML) from the source
2. Save to: {self.downloads_dir}
3. Handle authentication if needed (check environment variables)
4. Extract compressed files (.zip, .tar.gz) if necessary
5. Return the path to downloaded data as 'result_path'

Use appropriate libraries:
- huggingface_hub.snapshot_download() for HuggingFace (datasets or models) - DO NOT parse HTML
- huggingface-cli command for HuggingFace via subprocess
- requests for HTTP downloads (but only for direct file links, not HTML pages)
- datasets library for HuggingFace datasets (but may give Parquet format)
- geopandas for vector data
- rasterio for raster data
- zipfile/tarfile for extraction
- sentinelhub for Sentinel data
- osmnx/overpy for OpenStreetMap data

IMPORTANT: 
- For HuggingFace URLs, ALWAYS use huggingface_hub.snapshot_download() or huggingface-cli - NEVER parse HTML
- If the URL is an HTML page from other sources, use the appropriate API/library instead of parsing HTML

Return only executable Python code, no explanations.
"""
        
        from langchain_core.messages import SystemMessage, HumanMessage
        
        messages = [
            SystemMessage(content="You are a geospatial data download expert. Generate executable Python code."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        code = response.content
        
        # Extract code block if present
        code_match = re.search(r'```python\n(.*?)\n```', code, re.DOTALL)
        if code_match:
            code = code_match.group(1)
        
        # Execute code
        try:
            exec_globals = {
                "requests": requests,
                "Path": Path,
                "self": self,
                "logger": logger
            }
            exec(code, exec_globals)
            # Assume code sets a variable 'result_path'
            return exec_globals.get("result_path")
        except Exception as e:
            logger.error(f"LLM-generated download code failed: {e}")
            return None
    
    def _determine_downloads_with_llm(
        self,
        task_description: str,
        context: Dict[str, Any]
    ) -> list:
        """Use LLM to determine what datasets to download"""
        prompt = f"""Based on this task: "{task_description}"

        And available search results: {json.dumps(context.get('search_results', []), indent=2)}

        Determine which datasets should be downloaded. Return a JSON list of dataset names/IDs to download.
        """
        
        from langchain_core.messages import SystemMessage, HumanMessage
        
        messages = [
            SystemMessage(content="You are a geospatial data expert. Return JSON list of datasets to download."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        text = response.content
        
        try:
            json_match = re.search(r'\[.*?\]', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            logger.warning(f"Failed to parse download list: {e}")
        
        return []
