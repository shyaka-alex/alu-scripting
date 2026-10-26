#!/usr/bin/python3
"""Recursively counts keywords in titles of the hot posts of a subreddit."""
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


def count_words(subreddit, word_list, after=None, counts=None):
    """Prints a sorted count of the given keywords found in hot post titles.

    Keywords are case-insensitive. Duplicates in word_list are summed.
    Nothing is printed if the subreddit is invalid or nothing matches.
    """
    if counts is None:
        counts = {}
    wanted = {}
    for word in word_list:
        wanted[word.lower()] = wanted.get(word.lower(), 0) + 1

    base, headers = _reddit_access()
    url = "{}/r/{}/hot.json".format(base, subreddit)
    params = {"limit": 100}
    if after is not None:
        params["after"] = after
    response = requests.get(url, headers=headers, params=params,
                            allow_redirects=False)
    if response.status_code == 200:
        try:
            data = response.json().get("data", {})
        except ValueError:
            data = {}
        for post in data.get("children", []):
            title = post.get("data", {}).get("title", "")
            for token in title.lower().split():
                if token in wanted:
                    counts[token] = counts.get(token, 0) + 1
        after = data.get("after")
        if after is not None:
            return count_words(subreddit, word_list, after, counts)

    results = [(word, counts[word] * wanted[word]) for word in counts]
    for word, total in sorted(results, key=lambda item: (-item[1], item[0])):
        print("{}: {}".format(word, total))
