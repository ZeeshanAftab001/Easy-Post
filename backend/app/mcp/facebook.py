# app/mcp/facebook.py

import requests
from typing import Optional, Dict, Any, List
import sys

from app.core.config import settings

class FacebookClient:
    def __init__(self, access_token: str, page_id: Optional[str] = None, api_version: str = settings.FACEBOOK_GRAPH_VERSION):
        self.token = access_token
        self.page_id = page_id
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to the Facebook Graph API."""
        url = f"{self.base_url}/{endpoint}"
        
        if params is None:
            params = {}
        
        params["access_token"] = self.token
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, data=data, params=params, timeout=30)
            else:
                return {"error": {"message": f"Unsupported method: {method}"}}
            
            print(f"[DEBUG] {method} {url} - Status: {response.status_code}", file=sys.stderr)
            
            if response.status_code != 200:
                print(f"[DEBUG] Error response: {response.text[:500]}", file=sys.stderr)
            
            return response.json()
        except Exception as e:
            print(f"[DEBUG] Request exception: {e}", file=sys.stderr)
            return {"error": {"message": str(e)}}

    def get_page_info(self) -> Dict[str, Any]:
        """Retrieve basic information about the connected Facebook Page."""
        if not self.page_id:
            return {"error": {"message": "page_id is required"}}
        
        return self._make_request("GET", self.page_id, params={
            "fields": "id,name,about,category,followers_count,fan_count,picture"
        })

    def create_text_post(self, message: str) -> Dict[str, Any]:
        """Create a text-only post on the Facebook Page."""
        if not self.page_id:
            return {"error": {"message": "page_id is required"}}

        return self._make_request("POST", f"{self.page_id}/feed", data={
            "message": message
        })

    def create_image_post(self, image_url: str, caption: str = "") -> Dict[str, Any]:
        """Create a post with an image on the Facebook Page."""
        if not self.page_id:
            return {"error": {"message": "page_id is required"}}

        return self._make_request("POST", f"{self.page_id}/photos", data={
            "url": image_url,
            "caption": caption
        })

    def schedule_post(self, message: str, scheduled_publish_time: int, image_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Schedule a post for a future time.
        scheduled_publish_time must be a Unix timestamp between 10 minutes and 75 days from now.
        """
        if not self.page_id:
            return {"error": {"message": "page_id is required"}}

        data = {
            "message": message,
            "published": "false",
            "scheduled_publish_time": scheduled_publish_time
        }

        if image_url:
            data["url"] = image_url
            endpoint = f"{self.page_id}/photos"
        else:
            endpoint = f"{self.page_id}/feed"

        return self._make_request("POST", endpoint, data=data)

    def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics (insights) for a specific post."""
        return self._make_request("GET", f"{post_id}/insights", params={
            "metric": "post_impressions_unique,post_engagements,post_reactions_by_type_total"
        })

    def get_page_analytics(self, period: str = "day") -> Dict[str, Any]:
        """Get analytics (insights) for the Facebook Page."""
        if not self.page_id:
            return {"error": {"message": "page_id is required"}}

        return self._make_request("GET", f"{self.page_id}/insights", params={
            "metric": "page_impressions_unique,page_engaged_users,page_fans",
            "period": period
        })

    def get_recent_posts(self, limit: int = 10) -> Dict[str, Any]:
        """Get the most recent posts from the Facebook Page feed."""
        if not self.page_id:
            return {"error": {"message": "page_id is required"}}

        return self._make_request("GET", f"{self.page_id}/published_posts", params={
            "fields": "id,message,created_time,permalink_url,shares,comments.summary(true),reactions.summary(true)",
            "limit": limit
        })

