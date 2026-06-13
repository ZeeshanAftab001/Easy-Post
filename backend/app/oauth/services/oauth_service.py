# app/social/services/oauth_service.py
import httpx
import json
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
            'redirect_uri': f"{settings.BACKEND_URL}/api/oauth/auth/facebook/callback",
            'state': state_token,
            'scope': 'pages_manage_posts,pages_read_engagement,instagram_basic,instagram_content_publish',
            'response_type': 'code'
        }

        query_string = urlencode(params)
        return f"https://www.facebook.com/v19.0/dialog/oauth?{query_string}"

    def get_instagram_auth_url(self, state_token: str) -> str:
        """Generate Instagram OAuth URL (using Facebook Login for Instagram Graph API)"""
        params = {
            'client_id': settings.FACEBOOK_APP_ID,
            'redirect_uri': f"{settings.BACKEND_URL}/api/oauth/auth/instagram/callback",
            'state': state_token,
            'scope': 'pages_show_list,pages_read_engagement,pages_manage_posts,instagram_basic,instagram_content_publish,business_management',
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
                'redirect_uri': f"{settings.BACKEND_URL}/api/oauth/auth/facebook/callback",
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

            # Get pages user manages (IMPORTANT: must ask for access_token explicitly)
            pages_response = await client.get(f"{self.facebook_api_url}/me/accounts", params={
                'access_token': long_token_data.get('access_token', access_token),
                'fields': 'name,id,access_token,category,tasks'
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

    # In oauth_service.py - Update exchange_instagram_code method

    # In oauth_service.py - Update exchange_instagram_code method

    # In oauth_service.py - Update exchange_instagram_code method

    async def exchange_instagram_code(self, code: str) -> Dict:
        """Exchange Instagram authorization code for access token"""
        print(f"\n=== INSTAGRAM TOKEN EXCHANGE DEBUG ===")

        async with httpx.AsyncClient() as client:
            # For Instagram Graph API, we use the Facebook token exchange endpoint
            data = {
                'client_id': settings.FACEBOOK_APP_ID,
                'client_secret': settings.FACEBOOK_APP_SECRET,
                'redirect_uri': f"{settings.BACKEND_URL}/api/oauth/auth/instagram/callback",
                'code': code,
                'grant_type': 'authorization_code'
            }

            print(
                f"Request data (client_secret hidden): { {k: '***' if k == 'client_secret' else v for k, v in data.items()} }")

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            try:
                # Use Facebook's token exchange endpoint
                token_response = await client.get(
                    "https://graph.facebook.com/v19.0/oauth/access_token",
                    params=data
                )

                print(f"Instagram token response status: {token_response.status_code}")
                print(f"Instagram token response headers: {dict(token_response.headers)}")

                # Log response text before parsing JSON
                response_text = token_response.text
                print(f"Instagram token response text (first 500 chars): {response_text[:500]}")

                if token_response.status_code != 200:
                    print(f"Instagram API error: {response_text}")

                    # Try alternative endpoint for Instagram Graph API
                    print("Trying Instagram Graph API endpoint...")

                    # For Instagram Graph API (connected to Facebook App)
                    graph_response = await client.get(
                        "https://graph.facebook.com/v18.0/oauth/access_token",
                        params={
                            'client_id': settings.FACEBOOK_APP_ID,
                            'client_secret': settings.FACEBOOK_APP_SECRET,
                            'redirect_uri': f"{settings.BACKEND_URL}/api/oauth/auth/instagram/callback",
                            'code': code,
                            'grant_type': 'authorization_code'
                        }
                    )

                    print(f"Graph API response status: {graph_response.status_code}")
                    graph_response_text = graph_response.text
                    print(f"Graph API response text: {graph_response_text[:500]}")

                    if graph_response.status_code == 200:
                        token_data = graph_response.json()
                    else:
                        raise Exception(f"Instagram API error {token_response.status_code}: {response_text}")
                else:
                    token_data = token_response.json()

                print(f"Instagram token data: {token_data}")

            except json.decoder.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Raw response: {response_text}")
                raise Exception(f"Invalid response from Instagram API: {response_text}")
            except Exception as e:
                print(f"Instagram API error: {str(e)}")
                raise Exception(f"Instagram API error: {str(e)}")

            if 'access_token' not in token_data:
                raise Exception(f"Instagram token error: {token_data}")

            access_token = token_data['access_token']

            # For Instagram Graph API, we find the Instagram Business Account linked to the Facebook Page
            try:
                print("Searching for linked Instagram Business Accounts via Facebook Graph API...")
                # 1. Get the list of pages the user manages
                pages_response = await client.get(
                    "https://graph.facebook.com/v19.0/me/accounts",
                    params={
                        "access_token": access_token,
                        "fields": "name,instagram_business_account{id,username}"
                    }
                )
                pages_data = pages_response.json()
                print(f"Pages data: {pages_data}")

                # 2. Find a page that has an Instagram Business Account linked
                for page in pages_data.get('data', []):
                    ig_account = page.get('instagram_business_account')
                    if ig_account:
                        print(f"✅ Found linked Instagram Business Account: {ig_account['username']} ({ig_account['id']})")
                        return {
                            'access_token': access_token,
                            'user_id': ig_account['id'],
                            'username': ig_account['username'],
                            'expires_in': token_data.get('expires_in', 3600),
                            'token_type': 'bearer',
                            'page_id': page['id']
                        }

                print("⚠️ No linked Instagram Business Accounts found on any of your Facebook Pages.")
                # Fallback to a placeholder so registration doesn't fail, but warn the user
                return {
                    'access_token': access_token,
                    'user_id': f"no_ig_linked_{secrets.token_hex(4)}",
                    'username': 'Manual Link Required',
                    'expires_in': token_data.get('expires_in', 3600),
                    'token_type': 'bearer'
                }

            except Exception as e:
                print(f"❌ Failed to lookup Instagram accounts: {e}")
                raise Exception(f"Lookup error: {e}")

    async def refresh_facebook_token(self, existing_token: str) -> Dict:
        """
        Refresh a Facebook long-lived token.
        Actually, long-lived tokens for pages don't expire if they are from a never-expire system,
        but for users they last 60 days. This exchanges a valid token for a fresh long-lived one.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.facebook_api_url}/oauth/access_token", params={
                'grant_type': 'fb_exchange_token',
                'client_id': settings.FACEBOOK_APP_ID,
                'client_secret': settings.FACEBOOK_APP_SECRET,
                'fb_exchange_token': existing_token
            })
            data = response.json()
            if 'access_token' not in data:
                raise Exception(f"Facebook refresh error: {data}")
            return data