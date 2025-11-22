"""
Social Media Publisher Modülü
Facebook, Twitter ve Instagram için publisher classes
"""
import os
import requests
from abc import ABC, abstractmethod


class SocialMediaPublisher(ABC):
    """Base class for social media publishers"""
    
    @abstractmethod
    def publish(self, message: str, image_path: str = None) -> dict:
        """Publish content to the platform"""
        pass


class FacebookPublisher(SocialMediaPublisher):
    """Facebook page posting"""
    
    def __init__(self):
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.page_id = os.getenv('FACEBOOK_PAGE_ID')
    
    def publish(self, message: str, image_path: str = None) -> dict:
        """Facebook'ta paylaşım yap - Graph API v21.0"""
        if not self.access_token or not self.page_id:
            return {
                "status": "error",
                "message": "Facebook credentials not configured"
            }
        
        try:
            # Her zaman photo endpoint kullan (görsel varsa caption, yoksa hata)
            if image_path:
                # Photo post with caption
                photo_url = f"https://graph.facebook.com/v21.0/{self.page_id}/photos"
                params = {
                    "caption": message,
                    "access_token": self.access_token,
                    "published": "true"
                }
                with open(image_path, 'rb') as img_file:
                    files = {'source': img_file}
                    response = requests.post(photo_url, data=params, files=files)
            else:
                # Text-only post - /feed endpoint
                feed_url = f"https://graph.facebook.com/v21.0/{self.page_id}/feed"
                params = {
                    "message": message,
                    "access_token": self.access_token
                }
                response = requests.post(feed_url, params=params)
            
            result = response.json()
            
            if response.status_code == 200 and ('id' in result or 'post_id' in result):
                return {
                    "status": "success",
                    "post_id": result.get('id') or result.get('post_id'),
                    "platform": "facebook"
                }
            else:
                error_msg = result.get('error', {}).get('message', 'Unknown error')
                error_code = result.get('error', {}).get('code', 'N/A')
                return {
                    "status": "error",
                    "message": f"Facebook API Error ({error_code}): {error_msg}",
                    "platform": "facebook"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Exception: {str(e)}",
                "platform": "facebook"
            }


class TwitterPublisher(SocialMediaPublisher):
    """Twitter posting with API v2"""
    
    def __init__(self):
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_secret = os.getenv('TWITTER_ACCESS_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Debug
        print(f"🔍 Twitter Init: API_KEY={'✅' if self.api_key else '❌'}, ACCESS_TOKEN={'✅' if self.access_token else '❌'}")
    
    def _get_oauth1_session(self):
        """OAuth 1.0a için requests-oauthlib gerekir"""
        try:
            from requests_oauthlib import OAuth1Session
            return OAuth1Session(
                self.api_key,
                client_secret=self.api_secret,
                resource_owner_key=self.access_token,
                resource_owner_secret=self.access_secret
            )
        except ImportError:
            return None
    
    def publish(self, message: str, image_path: str = None) -> dict:
        """Twitter'da paylaşım yap - API v2"""
        if not all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            return {
                "status": "error",
                "message": "Twitter credentials not configured",
                "platform": "twitter"
            }
        
        try:
            oauth = self._get_oauth1_session()
            if not oauth:
                return {
                    "status": "error",
                    "message": "requests-oauthlib not installed",
                    "platform": "twitter"
                }
            
            media_id = None
            
            # Görsel varsa yükle
            if image_path:
                # Media upload
                upload_url = "https://upload.twitter.com/1.1/media/upload.json"
                with open(image_path, 'rb') as img_file:
                    files = {'media': img_file}
                    upload_response = oauth.post(upload_url, files=files)
                
                if upload_response.status_code == 200:
                    media_id = upload_response.json().get('media_id_string')
                else:
                    return {
                        "status": "error",
                        "message": f"Media upload failed: {upload_response.text}",
                        "platform": "twitter"
                    }
            
            # Tweet gönder (API v2)
            tweet_url = "https://api.twitter.com/2/tweets"
            payload = {"text": message}
            
            if media_id:
                payload["media"] = {"media_ids": [media_id]}
            
            response = oauth.post(tweet_url, json=payload)
            result = response.json()
            
            if response.status_code == 201:
                return {
                    "status": "success",
                    "post_id": result.get('data', {}).get('id'),
                    "platform": "twitter"
                }
            else:
                error_msg = result.get('detail', result.get('errors', 'Unknown error'))
                return {
                    "status": "error",
                    "message": f"Twitter API Error: {error_msg}",
                    "platform": "twitter"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Exception: {str(e)}",
                "platform": "twitter"
            }


class InstagramPublisher(SocialMediaPublisher):
    """Instagram posting with Graph API"""
    
    def __init__(self):
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.instagram_account_id = os.getenv('INSTAGRAM_ACCOUNT_ID')
    
    def publish(self, message: str, image_path: str = None) -> dict:
        """Instagram'da paylaşım yap - Graph API"""
        if not self.access_token or not self.instagram_account_id:
            return {
                "status": "error",
                "message": "Instagram credentials not configured",
                "platform": "instagram"
            }
        
        if not image_path:
            return {
                "status": "error",
                "message": "Instagram requires an image",
                "platform": "instagram"
            }
        
        try:
            # Step 1: Create media container
            container_url = f"https://graph.facebook.com/v21.0/{self.instagram_account_id}/media"
            
            # Upload image and get URL (using Facebook hosting)
            with open(image_path, 'rb') as img_file:
                files = {'source': img_file}
                upload_response = requests.post(
                    f"https://graph.facebook.com/v21.0/{self.instagram_account_id}/media",
                    data={
                        'caption': message,
                        'access_token': self.access_token
                    },
                    files=files
                )
            
            if upload_response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"Media upload failed: {upload_response.text}",
                    "platform": "instagram"
                }
            
            container_id = upload_response.json().get('id')
            
            # Step 2: Publish the container
            publish_url = f"https://graph.facebook.com/v21.0/{self.instagram_account_id}/media_publish"
            publish_response = requests.post(
                publish_url,
                data={
                    'creation_id': container_id,
                    'access_token': self.access_token
                }
            )
            
            result = publish_response.json()
            
            if publish_response.status_code == 200 and 'id' in result:
                return {
                    "status": "success",
                    "post_id": result.get('id'),
                    "platform": "instagram"
                }
            else:
                error_msg = result.get('error', {}).get('message', 'Unknown error')
                return {
                    "status": "error",
                    "message": f"Instagram API Error: {error_msg}",
                    "platform": "instagram"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Exception: {str(e)}",
                "platform": "instagram"
            }
