"""
Facebook Paylaşım Modülü
Sadece Facebook için publisher class
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
        """Facebook'ta paylaşım yap"""
        if not self.access_token or not self.page_id:
            return {
                "status": "error",
                "message": "Facebook credentials not configured"
            }
        
        try:
            if image_path:
                # Photo post with caption
                photo_url = f"https://graph.facebook.com/v18.0/{self.page_id}/photos"
                params = {
                    "caption": message,
                    "access_token": self.access_token
                }
                files = {'source': open(image_path, 'rb')}
                response = requests.post(photo_url, data=params, files=files)
            else:
                # Text-only post (use /feed endpoint)
                feed_url = f"https://graph.facebook.com/v18.0/{self.page_id}/feed"
                params = {
                    "message": message,
                    "access_token": self.access_token
                }
                response = requests.post(feed_url, data=params)
            
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
