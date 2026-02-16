# app/services/cloudinary_service.py

import cloudinary
import cloudinary.uploader
from app.core.config import Settings
import logging
from typing import Optional


# Configure Cloudinary
cloudinary.config(
    cloud_name=Settings.CLOUDINARY_CLOUD_NAME,
    api_key=Settings.CLOUDINARY_API_KEY,
    api_secret=Settings.CLOUDINARY_API_SECRET,
    secure=True
)


class CloudinaryService:
    """Service for handling Cloudinary image uploads."""
    
    @staticmethod
    async def upload_image(image_bytes: bytes, folder: str = "instagram-posts", public_id: Optional[str] = None) -> Optional[str]:
        """
        Upload image bytes to Cloudinary and return the URL.
        
        Args:
            image_bytes: Raw image bytes
            folder: Folder name in Cloudinary
            public_id: Optional public ID for the image
        
        Returns:
            Public URL of the uploaded image or None if failed
        """
        try:
            upload_options = {
                "folder": folder,
                "resource_type": "image",
                "overwrite": True
            }
            
            if public_id:
                upload_options["public_id"] = public_id
            
            # Upload directly from bytes
            result = cloudinary.uploader.upload(
                image_bytes,
                **upload_options
            )
            
           
            return result.get("secure_url")
            
        except Exception as e:
        
            return None
    
    @staticmethod
    async def upload_from_url(image_url: str, folder: str = "instagram-posts") -> Optional[str]:
        """
        Upload image from URL to Cloudinary.
        
        Args:
            image_url: Public URL of the image
            folder: Folder name in Cloudinary
        
        Returns:
            Public URL of the uploaded image or None if failed
        """
        try:
            result = cloudinary.uploader.upload(
                image_url,
                folder=folder,
                resource_type="image"
            )
            
       
            return result.get("secure_url")
            
        except Exception as e:
          
            return None
    
    @staticmethod
    async def delete_image(public_id: str) -> bool:
        """
        Delete an image from Cloudinary.
        
        Args:
            public_id: The public ID of the image to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            if result.get("result") == "ok":
              
                return True
            else:
             
                return False
        except Exception as e:
        
            return False

# Singleton instance
cloudinary_service = CloudinaryService()