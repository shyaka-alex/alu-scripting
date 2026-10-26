#!/usr/bin/python3
"""Recursively collects the titles of all hot posts of a subreddit."""
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


def recurse(subreddit, hot_list=None, after=None):
    """Returns a list of the titles of all hot posts of a subreddit.

    Returns None if the subreddit is invalid or has no results.
    """
    if hot_list is None:
        hot_list = []
    base, headers = _reddit_access()
    url = "{}/r/{}/hot.json".format(base, subreddit)
    params = {"limit": 100}
    if after is not None:
        params["after"] = after
    response = requests.get(url, headers=headers, params=params,
                            allow_redirects=False)
    if response.status_code != 200:
        return hot_list if hot_list else None
    try:
        data = response.json().get("data", {})
    except ValueError:
        return hot_list if hot_list else None
    for post in data.get("children", []):
        hot_list.append(post.get("data", {}).get("title"))
    after = data.get("after")
    if after is not None:
        return recurse(subreddit, hot_list, after)
    return hot_list if hot_list else None
