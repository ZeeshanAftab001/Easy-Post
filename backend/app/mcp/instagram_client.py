# app/mcp/instagram_client.py

import json
from typing import Tuple
from app.core.database import AsyncSessionLocal
from app.mcp.instagram import InstagramClient
from sqlalchemy import select
from app.oauth.models.social import SocialAccount
from app.oauth.services.social_account_service import get_active_facebook_account


async def get_instagram_client(user_id: int) -> Tuple[InstagramClient, str]:
    """Get Instagram client using Facebook page token."""
    
  
    
    async with AsyncSessionLocal() as db:
        # Get Facebook account
   
        facebook_account = await get_active_facebook_account(db, user_id)
        
        if not facebook_account:
            # Double-check with direct query
           
            result = await db.execute(
                select(SocialAccount).where(
                    SocialAccount.user_id == user_id,
                    SocialAccount.platform == "facebook"
                )
            )
            facebook_account = result.scalars().first()
            if facebook_account:
               
                if not facebook_account.is_active:
                    raise ValueError("Facebook account exists but is inactive. Please reactivate it.")
            else:
                raise ValueError("No Facebook account found. Please connect your Facebook page first.")
        
    
        
        if not facebook_account.pages:
            raise ValueError("Facebook account has no pages data")
        
        # Parse the pages JSON
        try:
            
            pages = json.loads(facebook_account.pages)
         
            
            if not pages:
                raise ValueError("No pages found in Facebook account")
            
            # Get the first page
            page = pages[0]
            page_name = page.get('name', 'Unknown')
            page_id = page.get('id')
            
                                       
            
            # Get the page token (your working token)
            page_token = page.get('access_token')
            if not page_token:
              
                page_token = facebook_account.access_token
            
           
            
            # Create client with page token
            client = InstagramClient(
                access_token=page_token,
                page_id=page_id,
                api_version="v19.0"
            )
            
            # Get Instagram Business Account ID from Facebook
           
            ig_info = client.get_instagram_business_account()
            
          
            
            if "error" in ig_info:
                error_msg = ig_info["error"].get("message", "Unknown error")
             
                raise ValueError(f"Facebook API error: {error_msg}")
            
            if "instagram_business_account" not in ig_info:
              
                raise ValueError("No Instagram Business Account linked to this page")
            
            instagram_data = ig_info["instagram_business_account"]
            instagram_id = instagram_data.get("id")
            instagram_username = instagram_data.get("username")
            
          
            return client, instagram_id
            
        except json.JSONDecodeError as e:
            
            raise ValueError("Failed to parse pages data")
        except Exception as e:
          
            raise ValueError(f"Failed to get Instagram client: {str(e)}")