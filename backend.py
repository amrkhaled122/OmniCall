import argparse
import json
import os
import sys
import requests
import secrets
import string
from typing import List

from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.cloud import firestore

PWA_URL = "https://amrkhaled122.github.io/OmniCall/"
SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service-account.json")
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]

def load_sa():
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print(f"ERROR: Service account not found at {SERVICE_ACCOUNT_PATH}")
        sys.exit(1)
    with open(SERVICE_ACCOUNT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_access_token():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_PATH, scopes=SCOPES
    )
    creds.refresh(Request())
    return creds.token, creds

def db_client(project_id: str):
    return firestore.Client(project=project_id)

def gen_user_id(label: str | None = None) -> str:
    # lowercase letters + digits, 16 chars
    salt = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(16))
    return (label.lower().replace(' ','-') + '-' if label else '') + salt

def create_user(project_id: str, label: str | None = None) -> str:
    client = db_client(project_id)
    user_id = gen_user_id(label)
    client.collection('users').document(user_id).set({
        'label': label or '',
        'createdAt': firestore.SERVER_TIMESTAMP
    })
    return user_id

def list_user_tokens(project_id: str, user_id: str) -> List[str]:
    client = db_client(project_id)
    q = client.collection('users').document(user_id).collection('tokens').order_by(
        'createdAt', direction=firestore.Query.DESCENDING
    )
    tokens = []
    for doc in q.stream():
        data = doc.to_dict() or {}
        tok = data.get("token")
        if tok: tokens.append(tok)
    return tokens

def send_to_token(project_id: str, access_token: str, token: str, message_body: str) -> tuple[bool, str]:
    fcm_url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
    payload = {
        "message": {
            "token": token,
            "webpush": {
                "data": {
                    "title": "OmniCall",
                    "message": message_body,
                    "url": PWA_URL
                }
            }
        }
    }
    resp = requests.post(
        fcm_url,
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json; charset=UTF-8"},
        data=json.dumps(payload),
        timeout=10,
    )
    return (resp.ok, resp.text)

def main():
    parser = argparse.ArgumentParser(description="OmniCall push CLI (per-user)")
    parser.add_argument("--create-user", metavar="LABEL", help="Create a user and print pairing code (userId)")
    parser.add_argument("--user", help="Target a specific userId (pairing code)")
    parser.add_argument("--message", "-m", help="Message to send")
    args = parser.parse_args()

    sa = load_sa()
    project_id = sa.get("project_id")
    if not project_id:
        print("ERROR: project_id missing in service-account.json")
        sys.exit(1)

    access_token, creds = get_access_token()
    print(f"[omnicall] project_id={project_id} sa_email={creds.service_account_email}")

    if args.create_user:
        user_id = create_user(project_id, args.create_user)
        print("\n=== OmniCall Pairing Code ===")
        print(user_id)
        print("\nOn the phone, open the OmniCall PWA, tap Enable Notifications, and paste this code when prompted.")
        return

    if not args.user or not args.message:
        print("\nUsage:")
        print('  python backend.py --create-user "Khaled"')
        print('  python backend.py --user khaled-7v9m8a2q1e3r --message "Match found! Tap ACCEPT!"')
        return

    tokens = list_user_tokens(project_id, args.user)
    if not tokens:
        print(f"No tokens registered for userId '{args.user}'. Pair the device first.")
        return

    ok_count = 0
    for tok in tokens:
        ok, text = send_to_token(project_id, access_token, tok, args.message)
        print(("✅" if ok else "❌"), "token..", tok[:12], "=>", "OK" if ok else text)
        if ok: ok_count += 1
    print(f"Done. Success: {ok_count}/{len(tokens)}")

if __name__ == "__main__":
    main()
