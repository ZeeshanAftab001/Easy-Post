# app/mcp/instagram.py

import requests
from typing import Optional, Dict, Any, List
import json
import sys
import time

class InstagramClient:
    def __init__(self, access_token: str, page_id: Optional[str] = None, api_version: str = "v19.0"):
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

    def get_instagram_business_account(self) -> Dict[str, Any]:
        """Get Instagram Business Account ID from a Facebook Page."""
        if not self.page_id:
            return {"error": "page_id is required"}
        
        return self._make_request("GET", self.page_id, params={
            "fields": "instagram_business_account{id,username}"
        })

    def get_profile(self, instagram_id: str) -> Dict[str, Any]:
        """Get Instagram profile information."""
        return self._make_request("GET", instagram_id, params={
            "fields": "id,username,name,followers_count,media_count,biography,website,profile_picture_url"
        })

    def get_posts(self, instagram_id: str, limit: int = 5) -> Dict[str, Any]:
        """Get recent Instagram posts."""
        return self._make_request("GET", f"{instagram_id}/media", params={
            "fields": "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count",
            "limit": min(limit, 25)
        })

    def create_image_post(self, instagram_id: str, image_url: str, caption: str = "") -> Dict[str, Any]:
        """
        Create a single image post.
        
        Args:
            instagram_id: Instagram Business Account ID
            image_url: Publicly accessible URL of the image
            caption: Optional caption for the post
        
        Returns: Creation result with container ID and final post ID
        """
        print(f"[DEBUG] Creating image post for {instagram_id}", file=sys.stderr)
        
        # Step 1: Create media container
        container = self._make_request("POST", f"{instagram_id}/media", data={
            "image_url": image_url,
            "caption": caption
        })
        
        if "error" in container:
            return container
        
        container_id = container.get("id")
        print(f"[DEBUG] Container created: {container_id}", file=sys.stderr)
        
        # Step 2: Publish the container
        result = self._make_request("POST", f"{instagram_id}/media_publish", data={
            "creation_id": container_id
        })
        
        return result

    def create_video_post(self, instagram_id: str, video_url: str, caption: str = "", cover_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a video post.
        
        Args:
            instagram_id: Instagram Business Account ID
            video_url: Publicly accessible URL of the video
            caption: Optional caption for the post
            cover_url: Optional URL for video cover image
        
        Returns: Creation result with container ID and final post ID
        """
        print(f"[DEBUG] Creating video post for {instagram_id}", file=sys.stderr)
        
        data = {
            "media_type": "VIDEO",
            "video_url": video_url,
            "caption": caption
        }
        
        if cover_url:
            data["cover_url"] = cover_url
        
        # Step 1: Create media container
        container = self._make_request("POST", f"{instagram_id}/media", data=data)
        
        if "error" in container:
            return container
        
        container_id = container.get("id")
        print(f"[DEBUG] Video container created: {container_id}", file=sys.stderr)
        
        # Videos need time to process, so we'll check status
        print(f"[DEBUG] Waiting for video processing...", file=sys.stderr)
        time.sleep(5)  # Brief pause
        
        # Step 2: Publish the container
        result = self._make_request("POST", f"{instagram_id}/media_publish", data={
            "creation_id": container_id
        })
        
        return result

    def create_carousel_post(self, instagram_id: str, media_urls: List[str], media_types: List[str], caption: str = "") -> Dict[str, Any]:
        """
        Create a carousel post with multiple images/videos.
        
        Args:
            instagram_id: Instagram Business Account ID
            media_urls: List of media URLs (max 10)
            media_types: List of media types ('IMAGE' or 'VIDEO')
            caption: Optional caption for the post
        
        Returns: Creation result with carousel ID and final post ID
        """
        print(f"[DEBUG] Creating carousel post with {len(media_urls)} items", file=sys.stderr)
        
        if len(media_urls) > 10:
            return {"error": {"message": "Maximum 10 items allowed in carousel"}}
        
        if len(media_urls) != len(media_types):
            return {"error": {"message": "Number of URLs must match number of types"}}
        
        # Step 1: Create individual containers for each media item
        children = []
        
        for i, (media_url, media_type) in enumerate(zip(media_urls, media_types)):
            print(f"[DEBUG] Creating container {i+1} for {media_type}", file=sys.stderr)
            
            data = {
                "media_type": media_type,
                "is_carousel_item": "true"
            }
            
            if media_type == "IMAGE":
                data["image_url"] = media_url
            elif media_type == "VIDEO":
                data["video_url"] = media_url
            else:
                return {"error": {"message": f"Invalid media type: {media_type}"}}
            
            container = self._make_request("POST", f"{instagram_id}/media", data=data)
            
            if "error" in container:
                return container
            
            children.append(container.get("id"))
            print(f"[DEBUG] Container {i+1} created: {children[-1]}", file=sys.stderr)
        
        # Step 2: Create carousel container
        carousel = self._make_request("POST", f"{instagram_id}/media", data={
            "media_type": "CAROUSEL",
            "children": ",".join(children),
            "caption": caption
        })
        
        if "error" in carousel:
            return carousel
        
        carousel_id = carousel.get("id")
        print(f"[DEBUG] Carousel container created: {carousel_id}", file=sys.stderr)
        
        # Step 3: Publish the carousel
        result = self._make_request("POST", f"{instagram_id}/media_publish", data={
            "creation_id": carousel_id
        })
        
        return result

    def create_story(self, instagram_id: str, media_url: str, media_type: str = "IMAGE") -> Dict[str, Any]:
        """
        Create an Instagram story.
        
        Args:
            instagram_id: Instagram Business Account ID
            media_url: URL of the image/video for the story
            media_type: 'IMAGE' or 'VIDEO'
        
        Returns: Creation result with story ID
        """
        print(f"[DEBUG] Creating {media_type} story", file=sys.stderr)
        
        data = {
            "media_type": media_type
        }
        
        if media_type == "IMAGE":
            data["image_url"] = media_url
        else:
            data["video_url"] = media_url
        
        # Stories are created directly, no separate publish step
        return self._make_request("POST", f"{instagram_id}/media", data=data)

    def create_post_with_location(self, instagram_id: str, image_url: str, location_id: str, caption: str = "") -> Dict[str, Any]:
        """
        Create a post with location tag.
        
        Args:
            instagram_id: Instagram Business Account ID
            image_url: URL of the image
            location_id: Facebook location ID
            caption: Optional caption
        
        Returns: Creation result with post ID
        """
        print(f"[DEBUG] Creating post with location {location_id}", file=sys.stderr)
        
        # Step 1: Create media container with location
        container = self._make_request("POST", f"{instagram_id}/media", data={
            "image_url": image_url,
            "caption": caption,
            "location_id": location_id
        })
        
        if "error" in container:
            return container
        
        container_id = container.get("id")
        
        # Step 2: Publish
        result = self._make_request("POST", f"{instagram_id}/media_publish", data={
            "creation_id": container_id
        })
        
        return result

    def get_media_status(self, container_id: str) -> Dict[str, Any]:
        """
        Check the status of a media container.
        Useful for checking if video processing is complete.
        
        Args:
            container_id: The container ID to check
        
        Returns: Status information
        """
        return self._make_request("GET", container_id, params={
            "fields": "status_code,status"
        })

    def get_comments(self, media_id: str) -> Dict[str, Any]:
        """Get comments on a specific media post."""
        return self._make_request("GET", f"{media_id}/comments", params={
            "fields": "text,username,timestamp"
        })

    def reply_to_comment(self, comment_id: str, message: str) -> Dict[str, Any]:
        """Reply to a comment."""
        return self._make_request("POST", f"{comment_id}/replies", data={
            "message": message
        })

    def get_insights(self, instagram_id: str, metrics: str = "impressions,reach,profile_views", period: str = "day") -> Dict[str, Any]:
        """
        Get account insights.
        
        Args:
            instagram_id: Instagram Business Account ID
            metrics: Comma-separated list of metrics
            period: 'day', 'week', 'month', or 'days_28'
        
        Returns: Insights data
        """
        from datetime import datetime, timedelta
        
        since = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        until = datetime.now().strftime("%Y-%m-%d")
        
        return self._make_request("GET", f"{instagram_id}/insights", params={
            "metric": metrics,
            "period": period,
            "since": since,
            "until": until
        })

    def get_media_insights(self, media_id: str) -> Dict[str, Any]:
        """Get insights for a specific media post."""
        return self._make_request("GET", f"{media_id}/insights", params={
            "metric": "engagement,impressions,reach,saved"
        })

    def get_hashtag_info(self, hashtag_name: str) -> Dict[str, Any]:
        """Get information about a hashtag."""
        # First, search for the hashtag
        search_result = self._make_request("GET", "ig_hashtag_search", params={
            "user_id": self.page_id,
            "q": hashtag_name
        })
        
        if "error" in search_result:
            return search_result
        
        hashtag_id = search_result.get("data", [{}])[0].get("id")
        if not hashtag_id:
            return {"error": {"message": "Hashtag not found"}}
        
        # Get hashtag info
        return self._make_request("GET", hashtag_id)

    def get_hashtag_media(self, hashtag_name: str, limit: int = 25) -> Dict[str, Any]:
        """Get recent media for a hashtag."""
        # First, search for the hashtag
        search_result = self._make_request("GET", "ig_hashtag_search", params={
            "user_id": self.page_id,
            "q": hashtag_name
        })
        
        if "error" in search_result:
            return search_result
        
        hashtag_id = search_result.get("data", [{}])[0].get("id")
        if not hashtag_id:
            return {"error": {"message": "Hashtag not found"}}
        
        # Get recent media
        return self._make_request("GET", f"{hashtag_id}/recent_media", params={
            "user_id": self.page_id,
            "fields": "id,caption,media_type,media_url,permalink,timestamp",
            "limit": min(limit, 25)
        })

    def get_mentions(self, instagram_id: str, limit: int = 25) -> Dict[str, Any]:
        """Get recent mentions of the account."""
        return self._make_request("GET", f"{instagram_id}/mentions", params={
            "fields": "id,media_id,username,text,timestamp",
            "limit": min(limit, 25)
        })

    def get_followed_hashtags(self, instagram_id: str) -> Dict[str, Any]:
        """Get hashtags followed by the account."""
        return self._make_request("GET", f"{instagram_id}/followed_hashtags")

    def follow_hashtag(self, instagram_id: str, hashtag_name: str) -> Dict[str, Any]:
        """Follow a hashtag."""
        # First, get hashtag ID
        search_result = self._make_request("GET", "ig_hashtag_search", params={
            "user_id": self.page_id,
            "q": hashtag_name
        })
        
        if "error" in search_result:
            return search_result
        
        hashtag_id = search_result.get("data", [{}])[0].get("id")
        if not hashtag_id:
            return {"error": {"message": "Hashtag not found"}}
        
        # Follow the hashtag
        return self._make_request("POST", f"{instagram_id}/followed_hashtags", data={
            "hashtag_id": hashtag_id
        })

    def unfollow_hashtag(self, instagram_id: str, hashtag_id: str) -> Dict[str, Any]:
        """Unfollow a hashtag by ID."""
        return self._make_request("DELETE", f"{instagram_id}/followed_hashtags", data={
            "hashtag_id": hashtag_id
        })