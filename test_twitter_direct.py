"""
Twitter API v2 Direct Test
OAuth 1.0a ile basit tweet testi
"""
import os
from dotenv import load_dotenv
from requests_oauthlib import OAuth1Session

load_dotenv()

# Twitter credentials
api_key = os.getenv('TWITTER_API_KEY')
api_secret = os.getenv('TWITTER_API_SECRET')
access_token = os.getenv('TWITTER_ACCESS_TOKEN')
access_secret = os.getenv('TWITTER_ACCESS_SECRET')

print("=== TWITTER API TEST ===")
print(f"API Key: {api_key[:10]}..." if api_key else "API Key: MISSING")
print(f"Access Token: {access_token[:10]}..." if access_token else "Access Token: MISSING")

# OAuth session
oauth = OAuth1Session(
    api_key,
    client_secret=api_secret,
    resource_owner_key=access_token,
    resource_owner_secret=access_secret
)

# Test 1: Kendi hesap bilgini çek (GET /2/users/me)
print("\n--- Test 1: GET /2/users/me ---")
me_url = "https://api.twitter.com/2/users/me"
me_response = oauth.get(me_url)

print(f"Status Code: {me_response.status_code}")
print(f"Response: {me_response.text}")

if me_response.status_code == 200:
    print("SUCCESS! OAuth working! Account info retrieved.")
else:
    print("ERROR! OAuth failed! Token or permissions wrong.")
    exit()

# Test 2: Basit tweet at (POST /2/tweets)
print("\n--- Test 2: POST /2/tweets ---")
tweet_url = "https://api.twitter.com/2/tweets"
payload = {"text": "Test tweet from PawNear API - 23 Nov 2025"}

tweet_response = oauth.post(tweet_url, json=payload)

print(f"Status Code: {tweet_response.status_code}")
print(f"Response: {tweet_response.text}")

if tweet_response.status_code == 201:
    print("SUCCESS! Tweet posted!")
else:
    print("ERROR! Tweet failed!")
    error_data = tweet_response.json()
    if 'errors' in error_data:
        for error in error_data['errors']:
            print(f"   Error: {error}")
    if 'detail' in error_data:
        print(f"   Detail: {error_data['detail']}")

