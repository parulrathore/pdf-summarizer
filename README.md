# PDF Summarizer

A proof-of-concept AI agent that converts unstructured PDF documents into reliable, structured summaries using Claude's tool-forced structured output.

## What it does

Upload a PDF → extract its text → get back a structured summary with:
- Title, document type, and a short overview
- Key points with page references
- Extracted entities (people, organizations, dates)
- A confidence rating

## Features

- **Native text extraction** for standard text-based PDFs (via PyMuPDF)
- **OCR fallback** for scanned/image-based PDFs (via Tesseract), with a low-confidence warning when extraction quality is poor (e.g. complex forms, tables, dense grids)
- **Multi-column layout handling** — sorts text blocks by column position instead of raw left-to-right reading order
- **Long-document support** via map-reduce summarization — chunks large PDFs, summarizes each chunk, then merges into one final structured summary
- **Schema-validated output** — every summary is validated against a Pydantic model, so the structure is guaranteed reliable, not just prompted for
- **Streamlit UI** for uploading a PDF and viewing the structured summary in-browser

## Project structure

1. extract.py # PDF text extraction (native + OCR fallback
2. schema.py # Pydantic schema for structured summary output
3. summarize.py # Claude API call with tool-forced structured output + map-reduce
4. app.py # Streamlit UI
5. requirements.txt # Python dependencies

