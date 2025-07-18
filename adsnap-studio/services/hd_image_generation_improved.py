import requests
import os
import base64
from PIL import Image
import io
from .api_base import BaseAPIService

class HDImageGenerationService(BaseAPIService):
    """Improved HD Image Generation service with proper error handling."""
    
    def generate_hd_image(
        self, 
        prompt: str, 
        width: int = 512, 
        height: int = 512, 
        num_inference_steps: int = 20, 
        guidance_scale: float = 7.5
    ) -> Image.Image:
        """
        Generate HD image from text prompt.
        
        Args:
            prompt: Text description for image generation
            width: Image width (256-1024)
            height: Image height (256-1024)
            num_inference_steps: Number of denoising steps (10-50)
            guidance_scale: Guidance scale for generation (1.0-20.0)
            
        Returns:
            PIL Image object
            
        Raises:
            ValueError: For invalid parameters
            requests.RequestException: For API errors
        """
        # Validate parameters
        if not prompt or len(prompt.strip()) == 0:
            raise ValueError("Prompt cannot be empty")
        
        if not (256 <= width <= 1024) or width % 64 != 0:
            raise ValueError("Width must be between 256-1024 and divisible by 64")
        
        if not (256 <= height <= 1024) or height % 64 != 0:
            raise ValueError("Height must be between 256-1024 and divisible by 64")
        
        if not (10 <= num_inference_steps <= 50):
            raise ValueError("Inference steps must be between 10-50")
        
        if not (1.0 <= guidance_scale <= 20.0):
            raise ValueError("Guidance scale must be between 1.0-20.0")
        
        # Prepare request data
        data = {
            'prompt': prompt.strip(),
            'width': width,
            'height': height,
            'num_inference_steps': num_inference_steps,
            'guidance_scale': guidance_scale
        }
        
        # Make API request
        response_data = self.make_request('v1/text-to-image', data=data)
        
        # Process response
        if 'result' in response_data and 'images' in response_data['result']:
            image_data = response_data['result']['images'][0]
            
            # Handle base64 encoded image
            if isinstance(image_data, str):
                image_bytes = base64.b64decode(image_data)
                return Image.open(io.BytesIO(image_bytes))
            else:
                # Handle URL or other formats
                raise ValueError("Unexpected image format in response")
        else:
            raise ValueError("Invalid response format from API")

# Global service instance
hd_image_service = HDImageGenerationService()

def generate_hd_image(prompt: str, width: int = 512, height: int = 512, 
                     num_inference_steps: int = 20, guidance_scale: float = 7.5) -> Image.Image:
    """Wrapper function for backward compatibility."""
    return hd_image_service.generate_hd_image(prompt, width, height, num_inference_steps, guidance_scale)