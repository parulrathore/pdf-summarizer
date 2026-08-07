from dotenv import load_dotenv
load_dotenv()

import anthropic
import json
from schema import DocumentSummary

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

if __name__ == "__main__":
    sample_text = """
    Apple, Inc. engages in the design, manufacture, and sale of smartphones,
    personal computers, tablets, wearables and accessories. Founded by Steven
    Paul Jobs, Ronald Gerald Wayne, and Stephen G. Wozniak in April 1976,
    headquartered in Cupertino, CA.
    """
    result = summarize_text(sample_text)
    print(json.dumps(result.model_dump(), indent=2))