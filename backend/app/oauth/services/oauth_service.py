# app/social/services/oauth_service.py
import httpx
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode
import secrets
from ...core.config import settings


class OAuthService:
    def __init__(self):
        self.facebook_auth_url = "https://www.facebook.com/v18.0/dialog/oauth"
        self.facebook_token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
        self.facebook_api_url = "https://graph.facebook.com/v18.0"

        self.instagram_auth_url = "https://api.instagram.com/oauth/authorize"
        self.instagram_token_url = "https://api.instagram.com/oauth/access_token"
        self.instagram_graph_url = "https://graph.instagram.com"

    def generate_state_token(self) -> str:
        """Generate a secure state token for OAuth"""
        return secrets.token_urlsafe(32)

    # In your OAuthService class, update:
    def get_facebook_auth_url(self, state_token: str) -> str:
        """Generate Facebook OAuth URL"""
        params = {
            'client_id': settings.FACEBOOK_APP_ID,
            'redirect_uri': f"{settings.BACKEND_URL}/api/oauth/social/auth/facebook/callback",  # CHANGE THIS
            'state': state_token,
            'scope': 'pages_manage_posts,pages_read_engagement,instagram_basic,instagram_content_publish',
            'response_type': 'code'
        }

        query_string = urlencode(params)
        return f"https://www.facebook.com/v19.0/dialog/oauth?{query_string}"

    def get_instagram_auth_url(self, state_token: str) -> str:
        """Generate Instagram OAuth URL"""
        params = {
            'client_id': settings.FACEBOOK_APP_ID,  # Instagram uses Facebook App ID
            'redirect_uri': f"{settings.BACKEND_URL}/api/oauth/social/auth/instagram/callback",  # CHANGE THIS
            'state': state_token,
            'scope': 'instagram_basic,instagram_content_publish',
            'response_type': 'code'
        }

        query_string = urlencode(params)
        return f"https://www.facebook.com/v19.0/dialog/oauth?{query_string}"

    async def exchange_facebook_code(self, code: str) -> Dict:
        """Exchange Facebook authorization code for access token"""
        async with httpx.AsyncClient() as client:
            # Get short-lived access token
            token_response = await client.get(self.facebook_token_url, params={
                'client_id': settings.FACEBOOK_APP_ID,
                'client_secret': settings.FACEBOOK_APP_SECRET,
                'redirect_uri': f"{settings.BACKEND_URL}/api/oauth/social/auth/facebook/callback",  # CHANGE THIS LINE
                'code': code
            })
            token_data = token_response.json()

            if 'access_token' not in token_data:
                raise Exception(f"Facebook token error: {token_data}")

            access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)

            # Get user info
            user_response = await client.get(f"{self.facebook_api_url}/me", params={
                'access_token': access_token,
                'fields': 'id,name,email'
            })
            user_data = user_response.json()

            # Get long-lived token (60 days)
            long_token_response = await client.get(f"{self.facebook_api_url}/oauth/access_token", params={
                'grant_type': 'fb_exchange_token',
                'client_id': settings.FACEBOOK_APP_ID,
                'client_secret': settings.FACEBOOK_APP_SECRET,
                'fb_exchange_token': access_token
            })
            long_token_data = long_token_response.json()

            # Get pages user manages
            pages_response = await client.get(f"{self.facebook_api_url}/me/accounts", params={
                'access_token': long_token_data.get('access_token', access_token)
            })
            pages_data = pages_response.json()

            return {
                'access_token': long_token_data.get('access_token', access_token),
                'expires_in': long_token_data.get('expires_in', expires_in),
                'user_id': user_data['id'],
                'user_name': user_data.get('name'),
                'user_email': user_data.get('email'),
                'pages': pages_data.get('data', []),
                'token_type': token_data.get('token_type', 'bearer')
            }

    async def exchange_instagram_code(self, code: str) -> Dict:
        """Exchange Instagram authorization code for access token"""
        async with httpx.AsyncClient() as client:
            # Get access token
            token_response = await client.post(self.instagram_token_url, data={
                'client_id': settings.INSTAGRAM_APP_ID,
                'client_secret': settings.INSTAGRAM_APP_SECRET,
                'grant_type': 'authorization_code',
                'redirect_uri': f"{settings.BACKEND_URL}/api/oauth/social/auth/instagram/callback",  # CHANGE THIS LINE
                'code': code
            })

            token_data = token_response.json()

            if 'access_token' not in token_data:
                raise Exception(f"Instagram token error: {token_data}")

            # Get user info
            user_response = await client.get(f"{self.instagram_graph_url}/me", params={
                'access_token': token_data['access_token'],
                'fields': 'id,username,media_count'
            })
            user_data = user_response.json()

            return {
                'access_token': token_data['access_token'],
                'user_id': user_data['id'],
                'username': user_data['username'],
                'media_count': user_data.get('media_count'),
                'token_type': 'bearer'
            }