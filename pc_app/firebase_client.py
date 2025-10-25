from __future__ import annotations

import json
import os
import secrets
import string
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from google.auth.transport.requests import Request
from google.cloud import firestore
from google.cloud.firestore_v1 import Increment
from google.oauth2 import service_account

PWA_URL = "https://amrkhaled122.github.io/OmniCall/"
DEFAULT_MESSAGE = "Match found !! Hurry up and accept on your PC !!"
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]

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


def _service_account_path() -> str:
    env_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if env_path:
        return env_path

    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    candidates = [
        base_dir / "omnicall-service-account.json",
        base_dir.parent / "omnicall-service-account.json",
        Path(__file__).resolve().parent / ".." / "omnicall-service-account.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return str(candidates[-1])


def _ensure_sa_exists(path: str) -> None:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Service account JSON not found at {path}. Set GOOGLE_APPLICATION_CREDENTIALS or place the file next to backend.py."
        )


def _raw_credentials():
    path = _service_account_path()
    _ensure_sa_exists(path)
    return service_account.Credentials.from_service_account_file(path)


def _messaging_token() -> Tuple[str, service_account.Credentials]:
    creds = _raw_credentials().with_scopes(SCOPES)
    creds.refresh(Request())
    return creds.token, creds


def firestore_client() -> firestore.Client:
    creds = _raw_credentials()
    project_id = creds.project_id
    if not project_id:
        raise RuntimeError("project_id missing in service account file")
    return firestore.Client(project=project_id, credentials=creds)


def project_id() -> str:
    creds = _raw_credentials()
    pid = creds.project_id
    if not pid:
        raise RuntimeError("project_id missing in service account file")
    return pid


def _generate_suffix(length: int = 16) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def create_user(label: str) -> Tuple[str, str]:
    client = firestore_client()
    clean_label = label.strip()
    suffix = _generate_suffix()
    base = clean_label.lower().replace(" ", "-") if clean_label else ""
    user_id = f"{base}-{suffix}" if base else suffix
    client.collection("users").document(user_id).set(
        {
            "label": clean_label,
            "createdAt": firestore.SERVER_TIMESTAMP,
        }
    )
    _inc_stats(client, users=1, users_today=1)
    url = f"{PWA_URL}?pair={user_id}"
    return user_id, url


def list_tokens(user_id: str) -> List[str]:
    client = firestore_client()
    docs = client.collection("users").document(user_id).collection("tokens").stream()
    tokens: List[str] = []
    for doc in docs:
        data = doc.to_dict() or {}
        tok = data.get("token")
        if tok:
            tokens.append(tok)
    return tokens


def send_notification(user_id: str, message: Optional[str] = None) -> SendResult:
    tokens = list_tokens(user_id)
    if not tokens:
        return SendResult(sent=0, total=0, failures=["No tokens registered. Pair your phone first."])

    project = project_id()
    access_token, _creds = _messaging_token()
    payload_template = {
        "message": {
            "token": None,
            "data": {
                "title": "Game Alert!",
                "message": message or DEFAULT_MESSAGE,
                "url": PWA_URL,
            },
            "webpush": {"fcm_options": {"link": PWA_URL}},
        }
    }

    url = f"https://fcm.googleapis.com/v1/projects/{project}/messages:send"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
    }

    success = 0
    failures: List[str] = []
    for token in tokens:
        body = payload_template.copy()
        message_block = body["message"].copy()
        data_block = message_block["data"].copy()
        message_block["data"] = data_block
        message_block["token"] = token
        body["message"] = message_block
        resp = requests.post(url, headers=headers, json=body, timeout=10)
        if resp.ok:
            success += 1
        else:
            failures.append(f"{token[:12]}… → {resp.text}")

    if success:
        client = firestore_client()
        _inc_stats(client, sends=success)

    return SendResult(sent=success, total=len(tokens), failures=failures)


def _inc_stats(client: firestore.Client, users: int = 0, sends: int = 0, users_today: int = 0) -> None:
    if users or sends:
        client.collection("stats").document("global").set(
            {
                **({"totalUsers": Increment(users)} if users else {}),
                **({"totalSends": Increment(sends)} if sends else {}),
                "updatedAt": firestore.SERVER_TIMESTAMP,
            },
            merge=True,
        )
    if users_today:
        client.collection("stats_daily").document(_today_key()).set(
            {
                "usersToday": Increment(users_today),
                "updatedAt": firestore.SERVER_TIMESTAMP,
            },
            merge=True,
        )


def fetch_stats() -> GlobalStats:
    client = firestore_client()
    global_doc = client.collection("stats").document("global").get()
    global_data = global_doc.to_dict() if global_doc.exists else {}
    today_doc = client.collection("stats_daily").document(_today_key()).get()
    today_data = today_doc.to_dict() if today_doc.exists else {}
    updated = global_data.get("updatedAt")
    if isinstance(updated, datetime):
        updated_at = updated
    else:
        updated_at = None
    return GlobalStats(
        total_users=int(global_data.get("totalUsers", 0) or 0),
        total_sends=int(global_data.get("totalSends", 0) or 0),
        users_today=int(today_data.get("usersToday", 0) or 0),
        updated_at=updated_at,
    )


def _today_key() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def submit_feedback(user_id: str, display_name: str, message: str) -> None:
    client = firestore_client()
    client.collection("feedback").add(
        {
            "userId": user_id,
            "displayName": display_name,
            "message": message,
            "createdAt": firestore.SERVER_TIMESTAMP,
        }
    )
