import os
import re
from pathlib import Path

from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from config.settings import YOUTUBE_UPLOAD_SCOPE, BASE_DIR


ENV_PATH = BASE_DIR / ".env"

CLIENT_CONFIG = {
    "installed": {
        "client_id": "",
        "client_secret": "",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"],
    }
}


def _load_env() -> dict[str, str]:
    vars_ = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            vars_[key.strip()] = val.strip()
    return vars_


def _save_refresh_token(token: str):
    if not ENV_PATH.exists():
        ENV_PATH.write_text("", encoding="utf-8")

    lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
    new_lines = []
    replaced = False
    for line in lines:
        if re.match(r"^YOUTUBE_REFRESH_TOKEN\s*=", line):
            new_lines.append(f"YOUTUBE_REFRESH_TOKEN={token}")
            replaced = True
        else:
            new_lines.append(line)
    if not replaced:
        new_lines.append(f"YOUTUBE_REFRESH_TOKEN={token}")

    ENV_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def get_credentials() -> Credentials | None:
    env = _load_env()
    refresh_token = env.get("YOUTUBE_REFRESH_TOKEN", "")
    client_id = env.get("YOUTUBE_CLIENT_ID", "")
    client_secret = env.get("YOUTUBE_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        return None

    config = dict(CLIENT_CONFIG)
    config["installed"]["client_id"] = client_id
    config["installed"]["client_secret"] = client_secret

    creds = None
    if refresh_token:
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri=config["installed"]["token_uri"],
            client_id=client_id,
            client_secret=client_secret,
            scopes=[YOUTUBE_UPLOAD_SCOPE],
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

    return creds


def run_oauth_flow() -> Credentials:
    env = _load_env()
    client_id = env.get("YOUTUBE_CLIENT_ID", "")
    client_secret = env.get("YOUTUBE_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        raise ValueError(
            "YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET must be set in .env"
        )

    config = dict(CLIENT_CONFIG)
    config["installed"]["client_id"] = client_id
    config["installed"]["client_secret"] = client_secret

    flow = InstalledAppFlow.from_client_config(
        config, scopes=[YOUTUBE_UPLOAD_SCOPE]
    )
    creds = flow.run_local_server(port=0)

    if creds and creds.refresh_token:
        _save_refresh_token(creds.refresh_token)

    return creds
