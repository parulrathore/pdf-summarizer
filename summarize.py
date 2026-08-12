from dotenv import load_dotenv
load_dotenv()

import anthropic
import json
from schema import DocumentSummary, EmailSummary

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from .env

def build_tool_schema():
    return {
        "name": "structured_summary",
        "description": "Return a structured summary of the document",
        "input_schema": DocumentSummary.model_json_schema()
    }

def summarize_text(full_text: str) -> DocumentSummary:
    tool = build_tool_schema()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        tools=[tool],
        tool_choice={"type": "tool", "name": "structured_summary"},
        messages=[{
            "role": "user",
            "content": f"Summarize this document:\n\n{full_text}"
        }]
    )
    # Extract the tool_use block
    tool_use_block = next(
        block for block in response.content if block.type == "tool_use"
    )
    # Validate against Pydantic schema
    result = DocumentSummary.model_validate(tool_use_block.input)
    return result

def summarize_email(full_text: str) -> EmailSummary:
    tool = {
        "name": "structured_email_summary",
        "description": "Return a structured summary of the email",
        "input_schema": EmailSummary.model_json_schema()
    }
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        tools=[tool],
        tool_choice={"type": "tool", "name": "structured_email_summary"},
        messages=[{"role": "user", "content": f"Summarize this email:\n\n{full_text}"}]
    )
    tool_use_block = next(b for b in response.content if b.type == "tool_use")
    return EmailSummary.model_validate(tool_use_block.input)

if __name__ == "__main__":
    import sys
    from extract import extract_text_from_pdf

    if len(sys.argv) < 2:
        print("Usage: python summarize.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    pages = extract_text_from_pdf(pdf_path)

    # Combine all pages into one text block, keeping page markers
    full_text = "\n\n".join(f"[Page {p['page']}]\n{p['text']}" for p in pages)

    print(f"Extracted {len(pages)} pages, {len(full_text)} total chars\n")

    result = summarize_text(full_text)
    print(json.dumps(result.model_dump(), indent=2))