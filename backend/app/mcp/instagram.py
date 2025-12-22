import requests
from datetime import datetime


class InstagramClient:
    def __init__(self, access_token: str, page_id: str, api_version="v19.0"):
        self.token = access_token
        self.page_id = page_id
        self.api_version = api_version

    def verify_connection(self):
        url = f"https://graph.facebook.com/{self.api_version}/me"
        params = {
            "fields": "id,name,accounts{instagram_business_account{id,name,username}}",
            "access_token": self.token
        }
        return requests.get(url, params=params, timeout=30).json()

    def get_instagram_business_account(self):
        url = f"https://graph.facebook.com/{self.api_version}/{self.page_id}"
        params = {
            "fields": "instagram_business_account{id,name,username,profile_picture_url}",
            "access_token": self.token
        }
        return requests.get(url, params=params, timeout=30).json()

    def get_profile(self, instagram_id: str):
        url = f"https://graph.facebook.com/{self.api_version}/{instagram_id}"
        params = {
            "fields": (
                "id,username,biography,followers_count,"
                "follows_count,media_count,name,profile_picture_url,website"
            ),
            "access_token": self.token
        }
        return requests.get(url, params=params, timeout=30).json()

    def get_posts(self, instagram_id: str, limit=5):
        url = f"https://graph.facebook.com/{self.api_version}/{instagram_id}/media"
        params = {
            "fields": (
                "id,caption,media_type,media_url,"
                "permalink,thumbnail_url,timestamp,"
                "like_count,comments_count"
            ),
            "limit": limit,
            "access_token": self.token
        }
        return requests.get(url, params=params, timeout=30).json()

    def create_post(self, instagram_id: str, image_url: str, caption: str):
        # Step 1: Create container
        container_url = f"https://graph.facebook.com/{self.api_version}/{instagram_id}/media"
        container = requests.post(
            container_url,
            data={
                "image_url": image_url,
                "caption": caption,
                "access_token": self.token
            },
            timeout=30
        ).json()

        if "error" in container:
            return container

        # Step 2: Publish
        publish_url = f"https://graph.facebook.com/{self.api_version}/{instagram_id}/media_publish"
        return requests.post(
            publish_url,
            data={
                "creation_id": container["id"],
                "access_token": self.token
            },
            timeout=30
        ).json()

    def check_permissions(self):
        url = "https://graph.facebook.com/debug_token"
        params = {
            "input_token": self.token,
            "access_token": self.token
        }
        return requests.get(url, params=params, timeout=10).json()
