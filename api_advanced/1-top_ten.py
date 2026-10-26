#!/usr/bin/python3
"""Prints the titles of the first 10 hot posts of a subreddit."""
import os
import requests

USER_AGENT = "linux:alu.api_advanced:v1.0 (by /u/alu_student)"
TOKEN_CACHE = {}


def _reddit_access():
    """Returns (base_url, headers) for Reddit requests.

    Uses OAuth when REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET are set,
    otherwise falls back to plain requests.
    """
    headers = {"User-Agent": USER_AGENT}
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    secret = os.environ.get("REDDIT_CLIENT_SECRET")
    if not client_id or not secret:
        return "https://www.reddit.com", headers
    if "token" not in TOKEN_CACHE:
        token = None
        response = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=(client_id, secret), headers=headers,
            data={"grant_type": "client_credentials"})
        if response.status_code == 200:
            try:
                token = response.json().get("access_token")
            except ValueError:
                token = None
        TOKEN_CACHE["token"] = token
    if TOKEN_CACHE["token"] is None:
        return "https://www.reddit.com", headers
    headers["Authorization"] = "bearer {}".format(TOKEN_CACHE["token"])
    return "https://oauth.reddit.com", headers


def top_ten(subreddit):
    """Prints the titles of the first 10 hot posts of a subreddit.

    Prints None if the subreddit is invalid.
    """
    base, headers = _reddit_access()
    url = "{}/r/{}/hot.json".format(base, subreddit)
    params = {"limit": 10}
    response = requests.get(url, headers=headers, params=params,
                            allow_redirects=False)
    if response.status_code != 200:
        print(None)
        return
    try:
        posts = response.json().get("data", {}).get("children", [])
    except ValueError:
        print(None)
        return
    for post in posts:
        print(post.get("data", {}).get("title"))
