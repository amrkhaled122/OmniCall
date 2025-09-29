import argparse
import json
import os
import sys
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Where your PWA lives (used to deep-link back in the payload)
PWA_URL = "https://amrkhaled122.github.io/OmniCall/"

# Paths / env
SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service-account.json")
TOKEN_FILE = "fcm_token.txt"
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]

def load_service_account_info():
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

def read_device_token():
    if not os.path.exists(TOKEN_FILE):
        print(f"ERROR: {TOKEN_FILE} not found. Paste your FCM token there.")
        sys.exit(1)
    return open(TOKEN_FILE, "r", encoding="utf-8").read().strip()

def send_push(message_body: str):
    sa_info = load_service_account_info()
    project_id = sa_info.get("project_id")
    if not project_id:
        print("ERROR: project_id missing in service-account.json")
        sys.exit(1)

    fcm_url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

    token = read_device_token()
    access_token, creds = get_access_token()

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

    print(f"[omnicall] project_id={project_id} sa_email={creds.service_account_email}")
    resp = requests.post(
        fcm_url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        data=json.dumps(payload),
        timeout=10,
    )

    if resp.ok:
        print("✅ Sent:", message_body)
    else:
        print("❌ Send failed:", resp.status_code, resp.text)

def main():
    parser = argparse.ArgumentParser(description="OmniCall push CLI")
    parser.add_argument("--message", "-m", help="Send one notification and exit")
    args = parser.parse_args()

    if args.message:
        send_push(args.message)
        return

    print('Interactive mode. Type:  OmniCall - <your message>')
    print('Type "exit" to quit.')
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break
        if not line:
            continue
        if line.lower() == "exit":
            break
        if line.lower().startswith("omnicall -"):
            msg = line.split("-", 1)[1].strip()
            if msg:
                send_push(msg)
            else:
                print("No message found after '-'.")
        else:
            print('Format: OmniCall - <message>')

if __name__ == "__main__":
    main()
