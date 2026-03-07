#!/usr/bin/env python3
"""Runtime path and credential helpers for X posting flows."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Tuple


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def data_dir() -> Path:
    return project_root() / "data"


def drafts_file() -> Path:
    return data_dir() / "drafts" / "latest_batch.json"


def logs_dir() -> Path:
    p = project_root() / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p


def cookie_file() -> Path:
    return project_root() / "config" / "x_cookies.json"


def x_api_repo_config_file() -> Path:
    return project_root() / "config" / "x_api_config.json"


def x_api_local_secret_file() -> Path:
    return Path.home() / ".clawdbot" / "secrets" / "x-api.json"


def _read_json(path: Path) -> Dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _normalize_api_creds(data: Dict) -> Dict:
    out = {
        "api_key": data.get("api_key") or data.get("X_API_KEY") or data.get("consumer_key"),
        "api_secret": data.get("api_secret") or data.get("X_API_SECRET") or data.get("consumer_secret"),
        "access_token": data.get("access_token") or data.get("X_ACCESS_TOKEN"),
        "access_token_secret": data.get("access_token_secret") or data.get("X_ACCESS_SECRET"),
        "bearer_token": data.get("bearer_token") or data.get("X_BEARER_TOKEN"),
    }
    return {k: v for k, v in out.items() if v}


def resolve_api_credentials() -> Tuple[Dict, str]:
    env_map = {
        "api_key": os.getenv("X_API_KEY"),
        "api_secret": os.getenv("X_API_SECRET"),
        "access_token": os.getenv("X_ACCESS_TOKEN"),
        "access_token_secret": os.getenv("X_ACCESS_SECRET"),
        "bearer_token": os.getenv("X_BEARER_TOKEN"),
    }
    if all(env_map.get(k) for k in ("api_key", "api_secret", "access_token", "access_token_secret")):
        return env_map, "env"

    local_secret = x_api_local_secret_file()
    if local_secret.exists():
        creds = _normalize_api_creds(_read_json(local_secret))
        if all(creds.get(k) for k in ("api_key", "api_secret", "access_token", "access_token_secret")):
            return creds, f"file:{local_secret}"

    repo_cfg = x_api_repo_config_file()
    if repo_cfg.exists():
        creds = _normalize_api_creds(_read_json(repo_cfg))
        if all(creds.get(k) for k in ("api_key", "api_secret", "access_token", "access_token_secret")):
            return creds, f"file:{repo_cfg}"

    return {}, "missing"
