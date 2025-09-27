"""
Viggle AI Module - Handles interactions with Viggle AI for image animations.
"""

import os
import json
import base64
import requests
import tempfile
from io import BytesIO
from typing import Dict, Any, Optional, Tuple, List
from PIL import Image

# Constants for the Viggle API
VIGGLE_API_URL = "https://api.viggle.ai/api/v1/generate/animation"

class ViggleAI:
    """Class to interact with Viggle AI for image animation"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the ViggleAI class with optional API key"""
        self.api_key = api_key or os.environ.get('VIGGLE_API_KEY')
        if not self.api_key:
            print("⚠️ Warning: No Viggle AI API key provided")

    def animate_image(self, 
                      image_path: str, 
                      prompt: str = "",
                      animation_type: str = "default",
                      strength: float = 0.75,
                      motion_bucket_id: int = 40) -> Tuple[bool, str, Optional[bytes]]:
        """
        Animate an image using Viggle AI.
        
        Args:
            image_path: Path to the image file
            prompt: Optional prompt to guide the animation
            animation_type: Type of animation to apply ("default", "zoom", "pan", etc.)
            strength: Animation strength (0.0 to 1.0)
            motion_bucket_id: Controls the amount of motion (higher = more motion)
            
        Returns:
            Tuple of (success, message, animated_image_data)
        """
        # Validate inputs
        if not os.path.exists(image_path):
            return False, f"Error: Image file not found at {image_path}", None
            
        if not self.api_key:
            return False, "Error: Viggle AI API key is required", None
        
        try:
            # Read and encode the image
            with open(image_path, 'rb') as img_file:
                base64_image = base64.b64encode(img_file.read()).decode('utf-8')
            
            # Prepare the request payload
            payload = {
                "animation_type": animation_type,
                "image": base64_image,
                "prompt": prompt,
                "strength": min(1.0, max(0.0, strength)),  # Ensure between 0 and 1
                "motion_bucket_id": motion_bucket_id
            }
            
            # Set up headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Make the request to Viggle AI
            print("Sending request to Viggle AI...")
            response = requests.post(
                VIGGLE_API_URL,
                headers=headers,
                data=json.dumps(payload),
                timeout=60  # 60 second timeout
            )
            
            # Handle the response
            if response.status_code == 200:
                # Try to parse the response and extract the animated image
                response_data = response.json()
                
                if "result" in response_data and "animation" in response_data["result"]:
                    # Decode the base64 image
                    animation_base64 = response_data["result"]["animation"]
                    animation_data = base64.b64decode(animation_base64)
                    return True, "Animation created successfully", animation_data
                else:
                    return False, "Unexpected response format from Viggle AI", None
            else:
                error_msg = f"Viggle AI API error: {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg += f" - {error_data['error']}"
                except:
                    error_msg += f" - {response.text}"
                    
                return False, error_msg, None
                
        except Exception as e:
            return False, f"Error during Viggle AI request: {str(e)}", None
    
    @staticmethod
    def save_animation(animation_data: bytes, output_path: str) -> Tuple[bool, str]:
        """
        Save animation data to a file
        
        Args:
            animation_data: Raw animation data (bytes)
            output_path: Path to save the animation file
            
        Returns:
            Tuple of (success, message)
        """
        try:
            with open(output_path, 'wb') as output_file:
                output_file.write(animation_data)
            return True, f"Animation saved to {output_path}"
        except Exception as e:
            return False, f"Error saving animation: {str(e)}"
    
    @staticmethod
    def download_discord_image(url: str) -> Tuple[bool, str, Optional[str]]:
        """
        Download an image from a Discord URL and save to a temp file
        
        Args:
            url: Discord image URL
            
        Returns:
            Tuple of (success, message, saved_file_path)
        """
        try:
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                return False, f"Failed to download image: HTTP {response.status_code}", None
                
            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_file.write(response.content)
            temp_file_path = temp_file.name
            temp_file.close()
            
            return True, "Image downloaded successfully", temp_file_path
        except Exception as e:
            return False, f"Error downloading Discord image: {str(e)}", None