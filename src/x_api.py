#!/usr/bin/env python3
"""
X-Manage: X/Twitter API Integration Module
Handles all communication with X API v2
"""

import json
import time
import os
import hashlib
import hmac
import base64
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

try:
    import httpx
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "httpx"], check=True)
    import httpx


class XAPIClient:
    """Client for X (Twitter) API v2 with OAuth 1.0a support."""

    BASE_URL = "https://api.twitter.com/2"
    UPLOAD_URL = "https://upload.twitter.com/1.1"

    def __init__(self, config_path: str = None):
        """
        Initialize X API client.
        Config should contain:
        - api_key (consumer key)
        - api_secret (consumer secret)
        - access_token
        - access_token_secret
        - bearer_token (for app-only auth)
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "..", "config", "x_api_config.json"
        )
        self.config = self._load_config()
        self.rate_limits = {}
        self.client = httpx.Client(timeout=30.0)

    def _load_config(self) -> dict:
        """Load API configuration from file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                return json.load(f)
        return {}

    def save_config(self, config: dict):
        """Save API configuration to file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)
        self.config = config

    def is_configured(self) -> bool:
        """Check if API credentials are configured."""
        required = ["api_key", "api_secret", "access_token", "access_token_secret"]
        return all(self.config.get(k) for k in required)

    # --- OAuth 1.0a Signature ---
    def _generate_oauth_signature(
        self, method: str, url: str, params: dict, 
        consumer_secret: str, token_secret: str
    ) -> str:
        """Generate OAuth 1.0a signature."""
        sorted_params = sorted(params.items())
        param_string = "&".join(f"{urllib.parse.quote(str(k), safe='')}"
                                f"={urllib.parse.quote(str(v), safe='')}"
                                for k, v in sorted_params)
        base_string = (
            f"{method.upper()}&"
            f"{urllib.parse.quote(url, safe='')}&"
            f"{urllib.parse.quote(param_string, safe='')}"
        )
        signing_key = (
            f"{urllib.parse.quote(consumer_secret, safe='')}&"
            f"{urllib.parse.quote(token_secret, safe='')}"
        )
        signature = hmac.new(
            signing_key.encode(), base_string.encode(), hashlib.sha1
        )
        return base64.b64encode(signature.digest()).decode()

    def _get_oauth_headers(self, method: str, url: str, extra_params: dict = None) -> dict:
        """Generate OAuth 1.0a Authorization header."""
        import uuid
        oauth_params = {
            "oauth_consumer_key": self.config["api_key"],
            "oauth_nonce": uuid.uuid4().hex,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_token": self.config["access_token"],
            "oauth_version": "1.0",
        }
        all_params = {**oauth_params}
        if extra_params:
            all_params.update(extra_params)

        signature = self._generate_oauth_signature(
            method, url, all_params,
            self.config["api_secret"],
            self.config["access_token_secret"]
        )
        oauth_params["oauth_signature"] = signature

        auth_header = "OAuth " + ", ".join(
            f'{urllib.parse.quote(str(k), safe="")}="{urllib.parse.quote(str(v), safe="")}"'
            for k, v in sorted(oauth_params.items())
        )
        return {"Authorization": auth_header}

    def _get_bearer_headers(self) -> dict:
        """Get Bearer token headers for app-only auth."""
        return {"Authorization": f"Bearer {self.config.get('bearer_token', '')}"}  

    def _check_rate_limit(self, endpoint: str):
        """Check and respect rate limits."""
        if endpoint in self.rate_limits:
            limit_info = self.rate_limits[endpoint]
            if limit_info["remaining"] == 0:
                wait_time = limit_info["reset"] - time.time()
                if wait_time > 0:
                    print(f"Rate limited on {endpoint}. Waiting {wait_time:.0f}s...")
                    time.sleep(wait_time + 1)

    def _update_rate_limits(self, endpoint: str, headers: dict):
        """Update rate limit tracking from response headers."""
        if "x-rate-limit-remaining" in headers:
            self.rate_limits[endpoint] = {
                "remaining": int(headers.get("x-rate-limit-remaining", 0)),
                "reset": int(headers.get("x-rate-limit-reset", 0)),
                "limit": int(headers.get("x-rate-limit-limit", 0)),
            }

    # --- Core API Methods ---
    def post_tweet(self, text: str, reply_to: str = None, quote_tweet_id: str = None) -> dict:
        """Post a tweet."""
        url = f"{self.BASE_URL}/tweets"
        payload = {"text": text}
        if reply_to:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to}
        if quote_tweet_id:
            payload["quote_tweet_id"] = quote_tweet_id

        self._check_rate_limit("post_tweet")
        headers = self._get_oauth_headers("POST", url)
        headers["Content-Type"] = "application/json"

        response = self.client.post(url, json=payload, headers=headers)
        self._update_rate_limits("post_tweet", response.headers)

        if response.status_code == 201:
            return {"success": True, "data": response.json()}
        return {"success": False, "error": response.text, "status": response.status_code}

    def post_thread(self, tweets: list) -> dict:
        """Post a thread (list of tweet texts)."""
        results = []
        previous_id = None
        for i, text in enumerate(tweets):
            result = self.post_tweet(text, reply_to=previous_id)
            results.append(result)
            if result["success"]:
                previous_id = result["data"]["data"]["id"]
                if i < len(tweets) - 1:
                    time.sleep(2)  # Small delay between thread tweets
            else:
                return {"success": False, "posted": i, "results": results, "error": result["error"]}
        return {"success": True, "posted": len(tweets), "results": results}

    def delete_tweet(self, tweet_id: str) -> dict:
        """Delete a tweet."""
        url = f"{self.BASE_URL}/tweets/{tweet_id}"
        headers = self._get_oauth_headers("DELETE", url)
        response = self.client.delete(url, headers=headers)
        return {"success": response.status_code == 200, "data": response.json()}

    def get_me(self) -> dict:
        """Get authenticated user info."""
        url = f"{self.BASE_URL}/users/me"
        params = {"user.fields": "public_metrics,description,profile_image_url"}
        headers = self._get_oauth_headers("GET", url, params)
        response = self.client.get(url, params=params, headers=headers)
        return response.json()

    def get_user_tweets(self, user_id: str, max_results: int = 10) -> dict:
        """Get recent tweets from a user."""
        url = f"{self.BASE_URL}/users/{user_id}/tweets"
        params = {
            "max_results": str(max_results),
            "tweet.fields": "created_at,public_metrics,text",
        }
        headers = self._get_bearer_headers()
        self._check_rate_limit("get_user_tweets")
        response = self.client.get(url, params=params, headers=headers)
        self._update_rate_limits("get_user_tweets", response.headers)
        return response.json()

    def get_tweet_metrics(self, tweet_id: str) -> dict:
        """Get engagement metrics for a tweet."""
        url = f"{self.BASE_URL}/tweets/{tweet_id}"
        params = {"tweet.fields": "public_metrics,created_at,organic_metrics"}
        headers = self._get_bearer_headers()
        response = self.client.get(url, params=params, headers=headers)
        return response.json()

    def search_recent(self, query: str, max_results: int = 10) -> dict:
        """Search recent tweets."""
        url = f"{self.BASE_URL}/tweets/search/recent"
        params = {
            "query": query,
            "max_results": str(max_results),
            "tweet.fields": "created_at,public_metrics,author_id",
        }
        headers = self._get_bearer_headers()
        self._check_rate_limit("search_recent")
        response = self.client.get(url, params=params, headers=headers)
        self._update_rate_limits("search_recent", response.headers)
        return response.json()

    def get_trending_topics(self, woeid: int = 1) -> dict:
        """Get trending topics (using v1.1 endpoint)."""
        url = f"https://api.twitter.com/1.1/trends/place.json"
        params = {"id": str(woeid)}
        headers = self._get_oauth_headers("GET", url, params)
        response = self.client.get(url, params=params, headers=headers)
        return response.json()

    def get_followers_count(self, user_id: str = None) -> int:
        """Get follower count for a user."""
        if user_id:
            url = f"{self.BASE_URL}/users/{user_id}"
        else:
            url = f"{self.BASE_URL}/users/me"
        params = {"user.fields": "public_metrics"}
        headers = self._get_oauth_headers("GET", url, params)
        response = self.client.get(url, params=params, headers=headers)
        data = response.json()
        try:
            return data["data"]["public_metrics"]["followers_count"]
        except (KeyError, TypeError):
            return 0


def test_connection(config_path: str = None) -> dict:
    """Test API connection and return user info."""
    client = XAPIClient(config_path)
    if not client.is_configured():
        return {"success": False, "error": "API not configured. Run setup first."}
    try:
        result = client.get_me()
        if "data" in result:
            return {"success": True, "user": result["data"]}
        return {"success": False, "error": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    result = test_connection()
    print(json.dumps(result, indent=2))
