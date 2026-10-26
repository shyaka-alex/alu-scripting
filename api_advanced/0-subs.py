#!/usr/bin/python3
"""Queries the Reddit API for the number of subscribers of a subreddit."""
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


def number_of_subscribers(subreddit):
    """Returns the number of subscribers of a subreddit.

    Returns 0 if the subreddit is invalid.
    """
    base, headers = _reddit_access()
    url = "{}/r/{}/about.json".format(base, subreddit)
    response = requests.get(url, headers=headers, allow_redirects=False)
    if response.status_code != 200:
        return 0
    try:
        return response.json().get("data", {}).get("subscribers", 0)
    except ValueError:
        return 0
