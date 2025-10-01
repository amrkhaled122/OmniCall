import argparse
import json
import os
import sys
import time
import requests
import secrets
import string
from datetime import datetime
from typing import List, Tuple

import qrcode
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.cloud import firestore
from google.cloud.firestore_v1 import Increment

# Optional screen capture (for --watch)
try:
    import cv2  # opencv-python
    import numpy as np
    import mss  # fast screen capture
except Exception:
    cv2 = None
    np = None
    mss = None

PWA_URL = "https://amrkhaled122.github.io/OmniCall/"
FIXED_MESSAGE = "Match found !! Hurry up and accept on your PC !!"

# If the env var is set, use it; otherwise look for a file next to backend.py
SERVICE_ACCOUNT_PATH = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    os.path.join(os.path.dirname(__file__), "omnicall-service-account.json")
)

SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]

# -------- Credentials / Firestore --------
def _ensure_sa_exists():
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print(f"ERROR: Service account not found at {SERVICE_ACCOUNT_PATH}")
        sys.exit(1)

def _load_credentials():
    _ensure_sa_exists()
    return service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH)

def get_access_token():
    creds = _load_credentials().with_scopes(SCOPES)
    creds.refresh(Request())
    return creds.token, creds

def db_client(project_id: str):
    creds = _load_credentials()
    return firestore.Client(project=project_id, credentials=creds)

def load_sa():
    _ensure_sa_exists()
    with open(SERVICE_ACCOUNT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# -------- IDs / Users --------
def gen_user_id(label: str | None = None) -> str:
    salt = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(16))
    lbl = (label or '').strip().lower().replace(' ', '-')
    return (lbl + '-' if lbl else '') + salt

def create_user(project_id: str, label: str | None = None) -> str:
    client = db_client(project_id)
    user_id = gen_user_id(label)
    client.collection('users').document(user_id).set({
        'label': label or '',
        'createdAt': firestore.SERVER_TIMESTAMP
    })
    # stats: total users + usersToday
    inc_stats(client, users=1, users_today=1)
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
        if tok:
            tokens.append(tok)
    return tokens

# -------- Stats --------
def today_key() -> str:
    # Use local date (Cairo time on your PC) in YYYY-MM-DD
    d = datetime.now()
    return d.strftime("%Y-%m-%d")

def inc_stats(client: firestore.Client, users: int = 0, sends: int = 0, users_today: int = 0):
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
        client.collection("stats_daily").document(today_key()).set(
            {
                "usersToday": Increment(users_today),
                "updatedAt": firestore.SERVER_TIMESTAMP,
            },
            merge=True,
        )

# -------- FCM Send --------
def send_to_token(project_id: str, access_token: str, token: str, message_body: str):
    fcm_url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
    payload = {
        "message": {
            "token": token,
            # ✅ Put your custom payload here (strings only)
            "data": {
                "title": "OmniCall",
                "message": message_body,
                "url": PWA_URL
            },
            # Optional: keep webpush for link behavior, but NO notification block
            "webpush": {
                "fcm_options": {
                    "link": PWA_URL
                }
            }
        }
    }

    resp = requests.post(
        fcm_url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8"
        },
        data=json.dumps(payload),
        timeout=10,
    )
    return (resp.ok, resp.text)


def send_fixed_message(project_id: str, user_id: str) -> int:
    tokens = list_user_tokens(project_id, user_id)
    if not tokens:
        print(f"No tokens registered for userId '{user_id}'. Pair the device first.")
        return 0

    access_token, _ = get_access_token()
    ok_count = 0
    for tok in tokens:
        ok, text = send_to_token(project_id, access_token, tok, FIXED_MESSAGE)
        print(("✅" if ok else "❌"), "token..", tok[:12], "=>", "OK" if ok else text)
        if ok:
            ok_count += 1

    # stats: increment totalSends by successful sends
    client = db_client(project_id)
    if ok_count:
        inc_stats(client, sends=ok_count)
    print(f"Done. Success: {ok_count}/{len(tokens)}")
    return ok_count

# -------- QR helper --------
def print_pairing_qr(user_id: str):
    url = f"https://amrkhaled122.github.io/OmniCall/?pair={user_id}"
    print("\nScan this QR from your phone:")
    qr = qrcode.QRCode(border=1)
    qr.add_data(url)
    qr.make(fit=True)
    qr.print_ascii(tty=True)
    print(url)
    print("\nOn iPhone, Add to Home Screen from that page, then open the app and tap Enable.")

# -------- Match detection (Windows) --------
def _load_template(path: str):
    if cv2 is None:
        raise RuntimeError("OpenCV not installed. pip install opencv-python mss pywin32")
    templ = cv2.imread(path, cv2.IMREAD_COLOR)
    if templ is None:
        raise FileNotFoundError(f"Template not found: {path}")
    return templ

def _capture_screen_bgr() -> "np.ndarray":
    # Fast, cross-monitor capture using mss (entire virtual screen)
    if mss is None:
        raise RuntimeError("mss not installed. pip install mss")
    with mss.mss() as sct:
        monitor = sct.monitors[0]  # all monitors
        img = np.array(sct.grab(monitor))  # BGRA
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

def detect_once(templ_bgr: "np.ndarray", threshold: float = 0.80) -> bool:
    screen_bgr = _capture_screen_bgr()
    th, tw = templ_bgr.shape[:2]
    if screen_bgr.shape[0] < th or screen_bgr.shape[1] < tw:
        return False
    res = cv2.matchTemplate(screen_bgr, templ_bgr, cv2.TM_CCOEFF_NORMED)
    minV, maxV, _, _ = cv2.minMaxLoc(res)
    return maxV >= threshold

def watch_and_send(project_id: str, user_id: str, template_path: str, threshold: float = 0.80,
                   debounce_seconds: int = 10, poll_ms: int = 200):
    print(f"[watch] template={template_path} threshold={threshold} debounce={debounce_seconds}s poll={poll_ms}ms")
    templ_bgr = _load_template(template_path)
    cooldown_until = 0.0
    try:
        while True:
            now = time.time()
            if now >= cooldown_until:
                if detect_once(templ_bgr, threshold=threshold):
                    print("[watch] Accept detected → sending notification")
                    sent = send_fixed_message(project_id, user_id)
                    if sent > 0:
                        cooldown_until = time.time() + debounce_seconds
                    else:
                        cooldown_until = time.time() + 3  # small delay if no tokens
            time.sleep(max(0.01, poll_ms / 1000.0))
    except KeyboardInterrupt:
        print("\n[watch] stopped")

# -------- CLI --------
def main():
    parser = argparse.ArgumentParser(description="OmniCall CLI")
    parser.add_argument("--create-user", metavar="LABEL", help="Create a user and print pairing QR")
    parser.add_argument("--user", help="Target a specific userId (pairing code)")
    parser.add_argument("--send", action="store_true", help="Send the fixed 'Match found' notification now")
    parser.add_argument("--watch", action="store_true", help="Watch screen and auto-send on Accept detection")
    parser.add_argument("--template", default="Accept.png", help="Path to Accept button template (default Accept.png)")
    parser.add_argument("--threshold", type=float, default=0.80, help="Template threshold (0..1)")
    parser.add_argument("--debounce", type=int, default=10, help="Cooldown seconds between sends")
    parser.add_argument("--poll", type=int, default=200, help="Polling interval ms")
    args = parser.parse_args()

    sa = load_sa()
    project_id = sa.get("project_id")
    if not project_id:
        print("ERROR: project_id missing in service-account.json")
        sys.exit(1)

    print(f"[omnicall] project_id={project_id}")
    print(f"[omnicall] using credentials file: {SERVICE_ACCOUNT_PATH}")

    if args.create_user:
        user_id = create_user(project_id, args.create_user)
        print_pairing_qr(user_id)
        print("\n=== OmniCall Pairing Code ===")
        print(user_id)
        return

    if not args.user:
        print("\nUsage:")
        print('  python backend.py --create-user "Khaled"')
        print('  python backend.py --user <pairing-code> --send')
        print('  python backend.py --user <pairing-code> --watch --template Accept.png')
        return

    if args.send:
        send_fixed_message(project_id, args.user)
        return

    if args.watch:
        if cv2 is None or mss is None:
            print("Install dependencies first: pip install opencv-python mss pywin32")
            sys.exit(1)
        watch_and_send(
            project_id=project_id,
            user_id=args.user,
            template_path=args.template,
            threshold=args.threshold,
            debounce_seconds=args.debounce,
            poll_ms=args.poll,
        )
        return

    # default action if only --user provided
    send_fixed_message(project_id, args.user)

if __name__ == "__main__":
    main()
