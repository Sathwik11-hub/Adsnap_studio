import requests
import time
import os
from typing import Optional, Dict, Any
import logging

class BaseAPIService:
    """Base class for all API services with common functionality."""
    
    def __init__(self):
        self.api_key = os.getenv('BRIA_API_KEY')
        self.base_url = "https://engine.prod.bria-api.com"
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if not self.api_key:
            raise ValueError("BRIA_API_KEY not found in environment variables")
    
    def get_headers(self) -> Dict[str, str]:
        """Get standard headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def make_request(
        self, 
        endpoint: str, 
        method: str = "POST", 
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Make API request with error handling and monitoring.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            data: JSON data for request
            files: Files for multipart upload
            timeout: Request timeout in seconds
            
        Returns:
            Response data dictionary
            
        Raises:
            requests.RequestException: For API errors
        """
        url = f"{self.base_url}/{endpoint}"
        
        # Prepare headers
        headers = self.get_headers() if not files else {"Authorization": f"Bearer {self.api_key}"}
        
        start_time = time.time()
        
        try:
            if method.upper() == "POST":
                if files:
                    response = requests.post(url, headers=headers, data=data, files=files, timeout=timeout)
                else:
                    response = requests.post(url, headers=headers, json=data, timeout=timeout)
            elif method.upper() == "GET":
                response = requests.get(url, headers=headers, params=data, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            duration = time.time() - start_time
            
            # Log request details
            self.logger.info(f"API Request: {method} {endpoint} - Status: {response.status_code} - Duration: {duration:.2f}s")
            
            # Handle response
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise requests.RequestException(error_msg)
                
        except requests.Timeout:
            error_msg = f"Request timeout after {timeout}s for {endpoint}"
            self.logger.error(error_msg)
            raise requests.RequestException(error_msg)
        except requests.ConnectionError:
            error_msg = f"Connection error for {endpoint}"
            self.logger.error(error_msg)
            raise requests.RequestException(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error for {endpoint}: {str(e)}"
            self.logger.error(error_msg)
            raise requests.RequestException(error_msg)
    
    def validate_image_file(self, image_file) -> bool:
        """Validate image file before upload."""
        if not image_file:
            return False
        
        # Check file size (max 10MB)
        if hasattr(image_file, 'size') and image_file.size > 10 * 1024 * 1024:
            raise ValueError("Image file too large (max 10MB)")
        
        # Check file type
        if hasattr(image_file, 'type'):
            valid_types = ['image/jpeg', 'image/png', 'image/webp']
            if image_file.type not in valid_types:
                raise ValueError(f"Invalid file type. Supported: {', '.join(valid_types)}")
        
        return True