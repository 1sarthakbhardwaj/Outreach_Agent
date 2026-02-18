"""Request logger for tracking all outreach email generation requests and feedback."""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional


LOG_FILE = "outreach_log.jsonl"


def log_request(
    person_name: str,
    linkedin_url: str,
    company_website: str,
    x_profile_url: str,
    word_limit: int,
    thinking_level: str,
    past_conversation: str,
    custom_instructions: str,
    generated_emails: list,
    token_usage: Dict[str, int],
    resources: list,
) -> str:
    """
    Log a generation request with all inputs and outputs. Returns the log entry ID.
    """
    entry_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    entry = {
        "id": entry_id,
        "timestamp": datetime.now().isoformat(),
        "inputs": {
            "person_name": person_name,
            "linkedin_url": linkedin_url,
            "company_website": company_website,
            "x_profile_url": x_profile_url,
            "word_limit": word_limit,
            "thinking_level": thinking_level,
            "past_conversation": past_conversation,
            "custom_instructions": custom_instructions,
        },
        "outputs": {
            "generated_emails": generated_emails,
            "token_usage": token_usage,
            "resources": resources,
        },
        "feedback": {
            "emails_actually_sent": [None, None, None],
        },
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return entry_id


def log_feedback(entry_id: str, email_index: int, actual_email_sent: str):
    """
    Append feedback for a specific log entry — what the user actually sent.
    Reads all entries, updates the matching one, and rewrites the file.
    """
    entries = _read_all_entries()
    updated = False
    for entry in entries:
        if entry.get("id") == entry_id:
            entry["feedback"]["emails_actually_sent"][email_index] = actual_email_sent
            entry["feedback"][f"feedback_timestamp_{email_index}"] = datetime.now().isoformat()
            updated = True
            break

    if updated:
        _write_all_entries(entries)

    return updated


def get_recent_entries(limit: int = 20) -> list:
    """Return the most recent log entries."""
    entries = _read_all_entries()
    return entries[-limit:]


def _read_all_entries() -> list:
    """Read all log entries from the JSONL file."""
    if not os.path.exists(LOG_FILE):
        return []
    entries = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def _write_all_entries(entries: list):
    """Rewrite all entries back to the JSONL file."""
    with open(LOG_FILE, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
