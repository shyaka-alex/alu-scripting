#!/usr/bin/python3
"""Prints the titles of the first 10 hot posts of a subreddit."""
import requests


def top_ten(subreddit):
    """Prints the titles of the first 10 hot posts of a subreddit.

    Prints None if the subreddit is invalid.
    """
    url = "https://www.reddit.com/r/{}/hot.json?limit=10".format(subreddit)
    headers = {"User-Agent": "linux:alu.api_advanced:v1.0 (by /u/alu_student)"}
    response = requests.get(url, headers=headers, allow_redirects=False)
    try:
        data = response.json().get("data")
    except (AttributeError, ValueError):
        data = None
    if data is None:
        print(None)
        return
    for post in data.get("children", []):
        print(post.get("data", {}).get("title"))
