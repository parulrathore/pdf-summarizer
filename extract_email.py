import email
from email import policy
from email.parser import BytesParser
import sys
from extract_gmail import extract_links  # reuse the same regex logic


def extract_text_from_eml(eml_path: str) -> dict:
    """
    Parses a .eml file into structured metadata + plain text body.
    Returns a dict compatible with the existing summarize_text() flow.
    """
    with open(eml_path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    subject = msg.get("Subject", "")
    sender = msg.get("From", "")
    to = msg.get("To", "")
    date = msg.get("Date", "")

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_content()
                break
        if not body:
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    body = part.get_content()
                    break
    else:
        body = msg.get_content()

    links = extract_links(body)

    full_text = (
        f"From: {sender}\nTo: {to}\nDate: {date}\nSubject: {subject}\n\n{body.strip()}"
    )

    return {
        "source_type": "email",
        "metadata": {
            "sender": sender, "to": to, "date": date, "subject": subject,
            "links": links, "category": "N/A (local file)",
        },
        "full_text": full_text,
        "method": "native",
        "low_confidence": False,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_email.py <path_to_eml>")
        sys.exit(1)

    result = extract_text_from_eml(sys.argv[1])
    print(f"Subject: {result['metadata']['subject']}")
    print(f"From: {result['metadata']['sender']}\n")
    print(result["full_text"][:1000])