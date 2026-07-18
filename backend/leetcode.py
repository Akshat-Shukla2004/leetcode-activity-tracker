"""
leetcode.py - LeetCode GraphQL API client.

Fetches recent accepted submissions for a given username.
Uses the public LeetCode GraphQL endpoint — no auth required for public data.
"""

import time
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

# GraphQL query to fetch the most recent submissions for a user
RECENT_SUBMISSIONS_QUERY = """
query recentSubmissions($username: String!, $limit: Int!) {
  recentSubmissionList(username: $username, limit: $limit) {
    title
    titleSlug
    timestamp
    statusDisplay
    lang
  }
}
"""

QUESTION_DETAILS_QUERY = """
query questionDetails($titleSlug: String!) {
    question(titleSlug: $titleSlug) {
        title
        titleSlug
        difficulty
        questionFrontendId
    }
}
"""


def fetch_accepted_submissions(username: str, limit: int = 20) -> list[dict]:
    """
    Fetch recent ACCEPTED submissions for a LeetCode user.

    Args:
        username: LeetCode username to query.
        limit:    How many recent submissions to fetch (default 20).

    Returns:
        List of dicts with keys: title, titleSlug, timestamp (int), lang.
        Returns an empty list on any failure so callers never crash.
    """
    payload = {
        "query": RECENT_SUBMISSIONS_QUERY,
        "variables": {"username": username, "limit": limit},
        "operationName": "recentSubmissions",
    }

    headers = {
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com",
    }

    try:
        response = requests.post(
            LEETCODE_GRAPHQL_URL,
            json=payload,
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        logger.error("LeetCode API timed out for user '%s'", username)
        return []
    except requests.exceptions.RequestException as exc:
        logger.error("LeetCode API request failed for '%s': %s", username, exc)
        return []
    except ValueError:
        logger.error("Failed to parse JSON response for user '%s'", username)
        return []

    # Navigate the GraphQL response safely
    submissions = data.get("data", {}).get("recentSubmissionList") or []

    # Filter to accepted only and normalize the timestamp to int
    accepted = []
    for sub in submissions:
        if sub.get("statusDisplay") == "Accepted":
            try:
                accepted.append(
                    {
                        "title": sub["title"],
                        "titleSlug": sub.get("titleSlug", ""),
                        "timestamp": int(sub["timestamp"]),
                        "lang": sub.get("lang", ""),
                    }
                )
            except (KeyError, ValueError) as exc:
                logger.warning("Skipping malformed submission entry: %s", exc)

    logger.info("Fetched %d accepted submission(s) for '%s'", len(accepted), username)
    return accepted


def get_accepted_submissions_since(
    username: str,
    since_ts: int = 0,
    limit: int = 50,
) -> list[dict]:
    """
    Return accepted submissions newer than a stored timestamp.

    The results are sorted oldest-first so callers can replay every missed
    solve in order.
    """
    submissions = fetch_accepted_submissions(username, limit=limit)
    fresh = [sub for sub in submissions if sub["timestamp"] > since_ts]
    return sorted(fresh, key=lambda sub: sub["timestamp"])


def get_latest_accepted(username: str) -> Optional[dict]:
    """
    Convenience: return only the single most recent accepted submission,
    or None if there are no accepted submissions or the API fails.
    """
    subs = fetch_accepted_submissions(username, limit=10)
    if not subs:
        return None
    # Submissions come back in reverse-chronological order; first is newest.
    return max(subs, key=lambda s: s["timestamp"])


def get_question_details(title_slug: str) -> Optional[dict]:
    """
    Fetch extra metadata for a LeetCode problem when it is available.

    Returns a dict with title, titleSlug, difficulty, and questionFrontendId,
    or None if the lookup fails.
    """
    if not title_slug:
        return None

    payload = {
        "query": QUESTION_DETAILS_QUERY,
        "variables": {"titleSlug": title_slug},
        "operationName": "questionDetails",
    }

    headers = {
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com",
    }

    try:
        response = requests.post(
            LEETCODE_GRAPHQL_URL,
            json=payload,
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        logger.error("LeetCode question lookup timed out for '%s'", title_slug)
        return None
    except requests.exceptions.RequestException as exc:
        logger.error("LeetCode question lookup failed for '%s': %s", title_slug, exc)
        return None
    except ValueError:
        logger.error("Failed to parse question metadata for '%s'", title_slug)
        return None

    question = data.get("data", {}).get("question")
    if not isinstance(question, dict):
        return None

    return {
        "title": question.get("title", ""),
        "titleSlug": question.get("titleSlug", title_slug),
        "difficulty": question.get("difficulty", ""),
        "questionFrontendId": question.get("questionFrontendId", ""),
    }


def seconds_ago(timestamp: int) -> int:
    """Return how many seconds ago a Unix timestamp was."""
    return max(0, int(time.time()) - timestamp)


def minutes_ago(timestamp: int) -> int:
    """Return how many minutes ago a Unix timestamp was (floored)."""
    return seconds_ago(timestamp) // 60
