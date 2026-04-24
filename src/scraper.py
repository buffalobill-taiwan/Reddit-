import requests
from typing import List, Dict, Optional


def get_hot_posts(subreddit: str, limit: int = 10, sort: str = "hot") -> List[Dict]:
    """
    Fetch hot posts from a subreddit using Reddit's public JSON API.

    Args:
        subreddit: Subreddit name (e.g., 'nosleep')
        limit: Number of posts to fetch (default: 10)
        sort: Sort method - hot, new, top, rising (default: hot)

    Returns:
        List of post dictionaries with title, selftext, author, score, permalink
    """
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json"
    headers = {
        "User-Agent": "redditTrans/1.0 (Python; like PRAW)"
    }
    params = {"limit": min(limit, 100)}

    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    posts = []

    for item in data["data"]["children"]:
        post = item["data"]
        posts.append({
            "title": post.get("title", ""),
            "selftext": post.get("selftext", ""),
            "author": str(post.get("author", "[deleted]")),
            "score": post.get("score", 0),
            "permalink": f"https://reddit.com{post.get('permalink', '')}",
            "url": post.get("url", ""),
            "id": post.get("id", ""),
            "num_comments": post.get("num_comments", 0),
            "is_self": post.get("is_self", True),
        })

    return posts


def get_post_content(post: Dict) -> str:
    """Extract readable content from a post for translation."""
    if post["selftext"]:
        return f"{post['title']}\n\n{post['selftext']}"
    return post["title"]