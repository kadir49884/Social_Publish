"""
Social Media Publisher Modülü
Facebook, Twitter ve Instagram için publisher classes
"""
import os
import time
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
        """Instagram'da paylaşım yap - Graph API (URL ile)"""
        if not self.access_token or not self.instagram_account_id:
            return {
                "status": "error",
                "message": "Instagram credentials not configured",
                "platform": "instagram"
            }
        
        if not image_path:
            return {
                "status": "error",
                "message": "Instagram requires an image URL",
                "platform": "instagram"
            }
        
        try:
            # Instagram için image_path aslında URL olmalı
            image_url = image_path
            
            # Step 1: Create media container with image URL
            container_url = f"https://graph.facebook.com/v21.0/{self.instagram_account_id}/media"
            container_params = {
                'image_url': image_url,
                'caption': message,
                'access_token': self.access_token
            }
            
            container_response = requests.post(container_url, data=container_params)
            container_result = container_response.json()
            
            if container_response.status_code != 200 or 'id' not in container_result:
                error_msg = container_result.get('error', {}).get('message', 'Unknown error')
                return {
                    "status": "error",
                    "message": f"Media container creation failed: {error_msg}",
                    "platform": "instagram"
                }
            
            container_id = container_result['id']
            
            # Step 2: Wait for media to be ready (Instagram genelde 10-20 saniye işler)
            # Optimize edilmiş: Daha az API call, daha uzun bekleme
            time.sleep(15)  # İlk bekleme: Instagram genelde 10-15 saniyede hazır
            
            max_attempts = 3  # En fazla 3 kontrol (15s → 25s → 40s)
            for attempt in range(max_attempts):
                status_url = f"https://graph.facebook.com/v21.0/{container_id}"
                status_params = {
                    'fields': 'status_code',
                    'access_token': self.access_token
                }
                status_response = requests.get(status_url, params=status_params)
                status_result = status_response.json()
                
                status_code = status_result.get('status_code')
                
                if status_code == 'FINISHED':
                    break
                elif status_code == 'ERROR':
                    return {
                        "status": "error",
                        "message": "Instagram media processing failed",
                        "platform": "instagram"
                    }
                
                # Exponential backoff: 10s → 15s
                wait_time = 10 if attempt == 0 else 15
                time.sleep(wait_time)
            
            # Step 3: Publish the container
            publish_url = f"https://graph.facebook.com/v21.0/{self.instagram_account_id}/media_publish"
            publish_params = {
                'creation_id': container_id,
                'access_token': self.access_token
            }
            
            publish_response = requests.post(publish_url, data=publish_params)
            publish_result = publish_response.json()
            
            if publish_response.status_code == 200 and 'id' in publish_result:
                return {
                    "status": "success",
                    "post_id": publish_result['id'],
                    "platform": "instagram"
                }
            else:
                error_msg = publish_result.get('error', {}).get('message', 'Unknown error')
                return {
                    "status": "error",
                    "message": f"Instagram publish error: {error_msg}",
                    "platform": "instagram"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Exception: {str(e)}",
                "platform": "instagram"
            }
