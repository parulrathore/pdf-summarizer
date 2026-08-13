from googleapiclient.discovery import build
from gmail_auth import get_gmail_credentials
import base64


def get_gmail_service():
    creds = get_gmail_credentials()
    return build("gmail", "v1", credentials=creds)


def list_recent_emails(max_results: int = 10) -> list[dict]:
    """Returns a list of {id, subject, sender, snippet} for recent inbox emails."""
    service = get_gmail_service()
    results = service.users().messages().list(
        userId="me", maxResults=max_results, labelIds=["INBOX"]
    ).execute()

    messages = results.get("messages", [])
    summaries = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me", id=msg["id"], format="metadata",
            metadataHeaders=["Subject", "From", "Date"]
        ).execute()

        headers = {h["name"]: h["value"] for h in msg_data["payload"]["headers"]}
        summaries.append({
            "id": msg["id"],
            "subject": headers.get("Subject", "(no subject)"),
            "sender": headers.get("From", ""),
            "date": headers.get("Date", ""),
            "snippet": msg_data.get("snippet", "")
        })

    return summaries


def extract_text_from_gmail_message(message_id: str) -> dict:
    """Fetches a single email's full body and returns it in the same shape as extract_email.py."""
    service = get_gmail_service()
    msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()

    headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
    subject = headers.get("Subject", "")
    sender = headers.get("From", "")
    to = headers.get("To", "")
    date = headers.get("Date", "")

    body = _extract_body(msg["payload"])

    full_text = f"From: {sender}\nTo: {to}\nDate: {date}\nSubject: {subject}\n\n{body.strip()}"

    return {
        "source_type": "email",
        "metadata": {"sender": sender, "to": to, "date": date, "subject": subject},
        "full_text": full_text,
        "method": "native",
        "low_confidence": False,
    }


def _extract_body(payload) -> str:
    """Recursively find the text/plain part of a Gmail message payload."""
    if payload.get("mimeType") == "text/plain" and "data" in payload.get("body", {}):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

    if "parts" in payload:
        for part in payload["parts"]:
            result = _extract_body(part)
            if result:
                return result

    return ""