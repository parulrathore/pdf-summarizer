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

1. extract.py # PDF text extraction (native + OCR fallback)
2. schema.py # Pydantic schema for structured summary output
3. summarize.py # Claude API call with tool-forced structured output + map-reduce
4. app.py # Streamlit UI
5. requirements.txt # Python dependencies
6. .env # API key (not committed — see Setup)

## Setup

### 1. Prerequisites (system-level)

- Python 3.11+
- [Poppler](https://poppler.freedesktop.org/) (for PDF-to-image conversion)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

**macOS:**
```bash
brew install poppler tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils tesseract-ocr
```

### 2. Python environment

```bash
python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. API key

Get a key from [console.anthropic.com](https://console.anthropic.com), then create a `.env` file in the project root:

ANTHROPIC_API_KEY=your-key-here

`.env` is git-ignored — never commit your real key.

## Usage

### Command line

```bash
python3 extract.py path/to/file.pdf      # test extraction only
python3 summarize.py path/to/file.pdf    # full pipeline, prints structured JSON
```

### Web UI

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`. Upload a PDF, click **Summarize**, view the structured result.

## Known limitations

1. OCR struggles with dense forms, tables, and non-prose layouts (e.g. order forms, menus) — the UI surfaces a warning when this is detected, but extraction may still be inaccurate
2. Multi-column detection assumes a simple 2-column split at the page midpoint; irregular or 3+ column layouts aren't fully handled
3. No groundedness/hallucination check yet — structured output is schema-valid but not independently verified against source text
4. Single-source only (PDF) — no support yet for URLs, DOCX, or other formats
