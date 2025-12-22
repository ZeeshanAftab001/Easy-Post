# instagram_poster_from_db.py
import requests
import json
from datetime import datetime
import sys


class InstagramPoster:
    def __init__(self, user_id=3):
        self.user_id = user_id

        # Your Instagram token from database
        self.INSTAGRAM_ACCESS_TOKEN = "EAAWXzqZCmMQsBQU9e2vL1B07VUpqUbl1wNhpynM4o6wFjBTxUNXExEVqLfKIqZC4wCiZBSOpyacTOrrjDaGXWc5ddRA7ioks3xuIkAup5W0G8n7boZAlROsvXCnfZAsb1N9xauRpFaZCoHiujDS8HG4ighFlh0X9KR2MPkGuW1a8XgWZAEo2ooqHrcimS9XPqTv0ZAxhAviYif9WSDxhACojvtPbXZCe3ZCCamOvw3r3ZBOGhihug5KZBhiVQaau0alZCr5afmWjUvnuih8pLXh8tDdUQPmRJH6osZC9SrUeLslKwkEzognQZDZD"

        # Your Facebook Page ID (connected to Instagram)
        self.FACEBOOK_PAGE_ID = "299677056569924"

        # Instagram API version
        self.API_VERSION = "v19.0"

    def verify_instagram_connection(self):
        """Verify Instagram account connection"""
        print("=" * 60)
        print("VERIFYING INSTAGRAM CONNECTION")
        print("=" * 60)

        # Step 1: Check if we can access Instagram Graph API
        url = f"https://graph.facebook.com/{self.API_VERSION}/me"

        params = {
            "fields": "id,name,accounts{instagram_business_account{id,name,username}}",
            "access_token": self.INSTAGRAM_ACCESS_TOKEN
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()

            if "error" in data:
                print(f"❌ Instagram API Error: {data['error']['message']}")
                return None

            print(f"✅ Connected to Facebook User: {data.get('name')}")
            print(f"   Facebook ID: {data.get('id')}")

            # Check for Instagram Business Account
            accounts = data.get('accounts', {}).get('data', [])
            instagram_account = None

            for account in accounts:
                if 'instagram_business_account' in account:
                    instagram_account = account['instagram_business_account']
                    print(f"\n📱 Instagram Business Account Found:")
                    print(f"   Instagram ID: {instagram_account.get('id')}")
                    print(f"   Username: {instagram_account.get('username')}")
                    print(f"   Name: {instagram_account.get('name')}")
                    break

            if not instagram_account:
                print("\n⚠️  No Instagram Business Account linked to Facebook Page")
                print("   Make sure your Facebook Page is connected to Instagram")

            return data

        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return None

    def get_instagram_business_account(self):
        """Get Instagram Business Account ID from Facebook Page"""
        print("\n" + "=" * 60)
        print("GETTING INSTAGRAM BUSINESS ACCOUNT")
        print("=" * 60)

        url = f"https://graph.facebook.com/{self.API_VERSION}/{self.FACEBOOK_PAGE_ID}"

        params = {
            "fields": "instagram_business_account{id,name,username,profile_picture_url}",
            "access_token": self.INSTAGRAM_ACCESS_TOKEN
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()

            if "error" in data:
                print(f"❌ Error: {data['error']['message']}")
                return None

            instagram_account = data.get('instagram_business_account')

            if instagram_account:
                print("✅ Instagram Business Account Found!")
                print(f"   ID: {instagram_account.get('id')}")
                print(f"   Username: {instagram_account.get('username')}")
                print(f"   Name: {instagram_account.get('name')}")
                return instagram_account
            else:
                print("❌ No Instagram Business Account linked to this Facebook Page")
                print("\n💡 To post to Instagram, you need:")
                print("1. A Facebook Page")
                print("2. An Instagram Business or Creator Account")
                print("3. Both accounts connected in Facebook Business Settings")
                return None

        except Exception as e:
            print(f"❌ API Error: {e}")
            return None

    def get_instagram_user_profile(self):
        """Get Instagram user profile info"""
        print("\n" + "=" * 60)
        print("GETTING INSTAGRAM PROFILE")
        print("=" * 60)

        # Try to get Instagram account info
        instagram_account = self.get_instagram_business_account()

        if not instagram_account:
            return None

        instagram_id = instagram_account.get('id')

        url = f"https://graph.facebook.com/{self.API_VERSION}/{instagram_id}"

        params = {
            "fields": "id,username,biography,followers_count,follows_count,media_count,name,profile_picture_url,website",
            "access_token": self.INSTAGRAM_ACCESS_TOKEN
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()

            if "error" in data:
                print(f"❌ Error: {data['error']['message']}")
                return None

            print("📊 Instagram Profile Info:")
            print(f"   👤 Username: {data.get('username')}")
            print(f"   📝 Name: {data.get('name')}")
            print(f"   📖 Bio: {data.get('biography', 'No bio')}")
            print(f"   🔗 Website: {data.get('website', 'No website')}")
            print(f"   📷 Posts: {data.get('media_count', 0)}")
            print(f"   👥 Followers: {data.get('followers_count', 0)}")
            print(f"   👤 Following: {data.get('follows_count', 0)}")

            return data

        except Exception as e:
            print(f"❌ API Error: {e}")
            return None

    def get_instagram_media(self):
        """Get recent Instagram posts"""
        print("\n" + "=" * 60)
        print("GETTING INSTAGRAM POSTS")
        print("=" * 60)

        instagram_account = self.get_instagram_business_account()

        if not instagram_account:
            return None

        instagram_id = instagram_account.get('id')

        url = f"https://graph.facebook.com/{self.API_VERSION}/{instagram_id}/media"

        params = {
            "fields": "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,like_count,comments_count",
            "access_token": self.INSTAGRAM_ACCESS_TOKEN,
            "limit": 5
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()

            if "error" in data:
                print(f"❌ Error: {data['error']['message']}")
                return None

            posts = data.get('data', [])

            print(f"📱 Found {len(posts)} recent posts:")

            for i, post in enumerate(posts, 1):
                print(f"\n   Post {i}:")
                print(f"   ├─ Type: {post.get('media_type')}")
                print(f"   ├─ Caption: {post.get('caption', 'No caption')[:50]}...")
                print(f"   ├─ Likes: {post.get('like_count', 0)}")
                print(f"   ├─ Comments: {post.get('comments_count', 0)}")
                print(f"   └─ Date: {post.get('timestamp', 'Unknown')[:10]}")

                if post.get('media_url'):
                    print(f"   🔗 Media URL available")

            return posts

        except Exception as e:
            print(f"❌ API Error: {e}")
            return None

    def create_instagram_post(self, image_url, caption=""):
        """
        Create Instagram post (2-step process)

        Step 1: Create media container
        Step 2: Publish the container
        """
        print("\n" + "=" * 60)
        print("CREATING INSTAGRAM POST")
        print("=" * 60)

        # Get Instagram Business Account
        instagram_account = self.get_instagram_business_account()

        if not instagram_account:
            return None

        instagram_id = instagram_account.get('id')

        print(f"📸 Posting to Instagram: @{instagram_account.get('username')}")
        print(f"   Image URL: {image_url}")
        print(f"   Caption: {caption[:50]}..." if caption else "   No caption")

        # STEP 1: Create Media Container
        print("\n🔄 Step 1: Creating media container...")

        container_url = f"https://graph.facebook.com/{self.API_VERSION}/{instagram_id}/media"

        container_data = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.INSTAGRAM_ACCESS_TOKEN
        }

        try:
            # Create container
            response = requests.post(container_url, data=container_data, timeout=30)
            container_result = response.json()

            if "error" in container_result:
                print(f"❌ Container creation failed: {container_result['error']['message']}")
                return None

            creation_id = container_result.get('id')
            print(f"✅ Container created! ID: {creation_id}")

            # STEP 2: Publish the container
            print("\n🔄 Step 2: Publishing container...")

            publish_url = f"https://graph.facebook.com/{self.API_VERSION}/{instagram_id}/media_publish"

            publish_data = {
                "creation_id": creation_id,
                "access_token": self.INSTAGRAM_ACCESS_TOKEN
            }

            # Publish the post
            response = requests.post(publish_url, data=publish_data, timeout=30)
            publish_result = response.json()

            if "error" in publish_result:
                print(f"❌ Publish failed: {publish_result['error']['message']}")
                return None

            post_id = publish_result.get('id')
            print(f"🎉 Instagram post published successfully!")
            print(f"📝 Post ID: {post_id}")

            # Get post details
            post_url = f"https://graph.facebook.com/{self.API_VERSION}/{post_id}"
            post_params = {
                "fields": "id,permalink",
                "access_token": self.INSTAGRAM_ACCESS_TOKEN
            }

            post_response = requests.get(post_url, params=post_params, timeout=10)
            post_data = post_response.json()

            if "permalink" in post_data:
                print(f"🔗 View post: {post_data['permalink']}")

            return publish_result

        except Exception as e:
            print(f"❌ Error creating post: {e}")
            return None

    def interactive_menu(self):
        """Interactive menu for Instagram operations"""
        print("\n" + "=" * 60)
        print("📱 INSTAGRAM MANAGEMENT MENU")
        print("=" * 60)

        while True:
            print("\nSelect an option:")
            print("1. 🔍 Verify Instagram connection")
            print("2. 👤 Get Instagram profile")
            print("3. 📷 Get recent posts")
            print("4. ➕ Create new post")
            print("5. 📊 Check permissions")
            print("0. ❌ Exit")

            try:
                choice = input("\nEnter choice (0-5): ").strip()

                if choice == "1":
                    self.verify_instagram_connection()

                elif choice == "2":
                    self.get_instagram_user_profile()

                elif choice == "3":
                    self.get_instagram_media()

                elif choice == "4":
                    # Get input for new post
                    image_url = input("Enter image URL: ").strip()
                    if not image_url:
                        print("⚠️  Using demo image URL")
                        image_url = "https://images.unsplash.com/photo-1574158622682-e40e69881006"

                    caption = input("Enter caption (press Enter for none): ").strip()

                    print("\n" + "=" * 60)
                    result = self.create_instagram_post(image_url, caption)

                    if result:
                        print("✅ Post created successfully!")
                    else:
                        print("❌ Failed to create post")

                elif choice == "5":
                    self.check_permissions()

                elif choice == "0":
                    print("Goodbye! 👋")
                    break

                else:
                    print("Invalid choice. Try again.")

            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye! 👋")
                break
            except Exception as e:
                print(f"Error: {e}")

    def check_permissions(self):
        """Check what permissions the token has"""
        print("\n" + "=" * 60)
        print("🔐 CHECKING TOKEN PERMISSIONS")
        print("=" * 60)

        url = "https://graph.facebook.com/debug_token"

        params = {
            "input_token": self.INSTAGRAM_ACCESS_TOKEN,
            "access_token": self.INSTAGRAM_ACCESS_TOKEN
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if "data" in data:
                print("Token Info:")
                print(f"   Valid: {data['data'].get('is_valid')}")
                print(f"   App ID: {data['data'].get('app_id')}")
                print(f"   User ID: {data['data'].get('user_id')}")
                print(f"   Expires: {datetime.fromtimestamp(data['data'].get('expires_at', 0))}")

                scopes = data['data'].get('scopes', [])
                print(f"\n📋 Permissions ({len(scopes)}):")
                for scope in scopes:
                    print(f"   ✅ {scope}")

                # Required permissions for Instagram posting
                required = ["instagram_basic", "instagram_content_publish", "pages_show_list"]
                print(f"\n🔍 Required for posting:")
                for req in required:
                    if req in scopes:
                        print(f"   ✅ {req}")
                    else:
                        print(f"   ❌ {req} - MISSING")

        except Exception as e:
            print(f"Error checking permissions: {e}")


def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("INSTAGRAM POSTING TOOL")
    print("=" * 60)
    print("\n📊 Database Analysis:")
    print("   👤 User ID: 3")
    print("   📱 Instagram Token: Found (from database)")
    print("   ⏰ Token Expires: 2025-12-21 13:58:18")

    poster = InstagramPoster(user_id=3)

    # First check connection
    print("\n🔗 Testing Instagram connection...")
    verification = poster.verify_instagram_connection()

    if verification:
        # Show menu
        poster.interactive_menu()
    else:
        print("\n❌ Instagram connection failed. Check:")
        print("1. Token permissions")
        print("2. Instagram Business Account setup")
        print("3. Facebook Page connection")


if __name__ == "__main__":
    main()