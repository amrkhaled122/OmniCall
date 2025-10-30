"""
Secure Firebase Client - Uses Cloud Functions instead of direct Firebase access.
No service account needed in the desktop app!
"""

from __future__ import annotations

import requests
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

# Your Firebase project configuration
FIREBASE_PROJECT_ID = "omnicall-d3630"
FIREBASE_REGION = "us-central1"
PWA_URL = "https://amrkhaled122.github.io/OmniCall/"
DEFAULT_MESSAGE = "Match found !! Hurry up and accept on your PC !!"

# Cloud Function URLs
BASE_URL = f"https://{FIREBASE_REGION}-{FIREBASE_PROJECT_ID}.cloudfunctions.net"
CREATE_USER_URL = f"{BASE_URL}/createUser"
SEND_NOTIFICATION_URL = f"{BASE_URL}/sendNotification"
SUBMIT_FEEDBACK_URL = f"{BASE_URL}/submitFeedback"
GET_STATS_URL = f"{BASE_URL}/getStats"


@dataclass
class SendResult:
    sent: int
    total: int
    failures: List[str]


@dataclass
class GlobalStats:
    total_users: int
    total_sends: int
    users_today: int
    updated_at: Optional[datetime]


@dataclass
class PersonalStats:
    matches_found: int
    notifications_sent: int


# Session for connection pooling (performance optimization)
_http_session: Optional[requests.Session] = None


def _get_session() -> requests.Session:
    """Get or create a persistent HTTP session for connection pooling."""
    global _http_session
    if _http_session is None:
        _http_session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=0
        )
        _http_session.mount('https://', adapter)
    return _http_session


def _call_function(url: str, data: dict, timeout: int = 10) -> dict:
    """
    Call a Firebase Cloud Function.
    
    Args:
        url: The function URL
        data: The data to send
        timeout: Request timeout in seconds
    
    Returns:
        The response data
    
    Raises:
        Exception: If the request fails
    """
    session = _get_session()
    
    try:
        response = session.post(
            url,
            json={"data": data},
            headers={"Content-Type": "application/json"},
            timeout=timeout
        )
        response.raise_for_status()
        
        result = response.json()
        
        # Check for Cloud Function errors
        if "error" in result:
            raise Exception(f"Cloud Function error: {result['error'].get('message', 'Unknown error')}")
        
        return result.get("result", {})
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error calling Cloud Function: {str(e)}")


def create_user(label: str) -> tuple[str, str]:
    """
    Create a new user via Cloud Function.
    
    Args:
        label: Display name for the user
    
    Returns:
        Tuple of (user_id, pairing_url)
    """
    result = _call_function(CREATE_USER_URL, {"displayName": label})
    
    if not result.get("success"):
        raise Exception("Failed to create user")
    
    return result["userId"], result["pairingUrl"]


def send_notification(user_id: str, message: Optional[str] = None) -> SendResult:
    """
    Send notification to user's devices via Cloud Function.
    
    Args:
        user_id: The user ID
        message: Optional custom message (defaults to DEFAULT_MESSAGE)
    
    Returns:
        SendResult with send statistics
    """
    data = {"userId": user_id}
    if message:
        data["message"] = message
    
    # Use shorter timeout for notifications (fast failure)
    result = _call_function(SEND_NOTIFICATION_URL, data, timeout=5)
    
    if not result.get("success"):
        raise Exception("Failed to send notification")
    
    return SendResult(
        sent=result.get("sent", 0),
        total=result.get("total", 0),
        failures=result.get("failures", [])
    )


def submit_feedback(user_id: str, display_name: str, message: str) -> None:
    """
    Submit user feedback via Cloud Function.
    
    Args:
        user_id: The user ID
        display_name: User's display name
        message: Feedback message
    """
    result = _call_function(
        SUBMIT_FEEDBACK_URL,
        {
            "userId": user_id,
            "displayName": display_name,
            "message": message
        }
    )
    
    if not result.get("success"):
        raise Exception("Failed to submit feedback")


def fetch_stats(user_id: str) -> tuple[PersonalStats, GlobalStats]:
    """
    Fetch user statistics via Cloud Function.
    
    Args:
        user_id: The user ID
    
    Returns:
        Tuple of (PersonalStats, GlobalStats)
    """
    result = _call_function(GET_STATS_URL, {"userId": user_id})
    
    if not result.get("success"):
        raise Exception("Failed to fetch stats")
    
    personal_data = result.get("personal", {})
    global_data = result.get("global", {})
    
    personal = PersonalStats(
        matches_found=personal_data.get("matchesFound", 0),
        notifications_sent=personal_data.get("notificationsSent", 0)
    )
    
    updated_at = None
    if global_data.get("updatedAt"):
        try:
            updated_at = datetime.fromisoformat(global_data["updatedAt"].replace('Z', '+00:00'))
        except:
            pass
    
    global_stats = GlobalStats(
        total_users=global_data.get("totalUsers", 0),
        total_sends=global_data.get("totalSends", 0),
        users_today=global_data.get("usersToday", 0),
        updated_at=updated_at
    )
    
    return personal, global_stats


# Keep these for backward compatibility (not used with Cloud Functions)
def warmup_cache(user_id: str) -> None:
    """No-op for Cloud Functions - caching happens on the server."""
    pass


def refresh_token_cache(user_id: str) -> None:
    """No-op for Cloud Functions - token management happens on the server."""
    pass
