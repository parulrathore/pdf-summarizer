# PDF & Email Summarizer

A proof-of-concept AI agent that converts unstructured PDFs and emails into reliable, structured summaries using Claude's tool-forced structured output.

## What it does

Upload a PDF or email (or connect Gmail) → extract its content → get back a structured summary.

**For PDFs:**
- Title, document type, and a short overview
- Key points with page references
- Extracted entities (people, organizations, dates)
- A confidence rating

**For emails (.eml upload or Gmail):**
- From, To, Subject, Date, and clickable links, shown immediately after extraction
- Gmail category (Primary, Promotional, Updates, Social, Forums) where available
- A structured summary with key points and action items
- Urgency flagged clearly in red when detected
- Whether a response is likely required

## Features

- **Native text extraction** for standard text-based PDFs (via PyMuPDF)
- **OCR fallback** for scanned/image-based PDFs (via Tesseract), with a low-confidence warning when extraction quality is poor (e.g. complex forms, tables, dense grids)
- **Email parsing** for local `.eml` files, including plain-text body extraction and link detection
- **Gmail integration** via OAuth2 — browse and summarize recent inbox emails directly, no manual export needed
- **Schema-validated output** — every summary is validated against a Pydantic model, so the structure is guaranteed reliable, not just prompted for
- **Streamlit UI** with a source-type selector (PDF / Email (.eml) / Gmail) and clickable link rendering by domain

## Project structure

1. extract.py # PDF text extraction (native + OCR fallback
2. extract_email.py # .eml file parsing (headers, body, links)
3. extract_gmail.py # Gmail API integration (list + fetch messages, link/category extraction)
4. gmail_auth.py # Gmail OAuth2 login flow
5. schema.py # Pydantic schemas (DocumentSummary, EmailSummary)
6. summarize.py # Claude API calls with tool-forced structured output
7. app.py # Streamlit UI
8. requirements.txt # Python dependencies


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

### 3. Anthropic API key

Get a key from [console.anthropic.com](https://console.anthropic.com), then create a `.env` file in the project root:

ANTHROPIC_API_KEY=your-key-here


### 4. Gmail API setup (only needed for the Gmail source option)

1. Create a project in [Google Cloud Console](https://console.cloud.google.com), enable the **Gmail API**
2. Configure the OAuth consent screen (External, add your Gmail account under **Test users**)
3. Create an **OAuth client ID** (type: Desktop app), download the JSON
4. Save it in the project root as `google_email_credentials.json`

On first run of the Gmail option, a browser window opens for login/consent, and a `token.json` is saved locally so future runs don't require re-login.

`.env`, `google_email_credentials.json`, and `token.json` are all git-ignored — never commit any of them.

## Usage

### Command line

```bash
python3 extract.py path/to/file.pdf         # PDF extraction only
python3 summarize.py path/to/file.pdf        # full PDF pipeline, prints structured JSON
python3 extract_email.py path/to/file.eml     # .eml extraction only
```

### Web UI

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`. Choose a source type (PDF / Email (.eml) / Gmail), then summarize.

## Known limitations

- OCR struggles with dense forms, tables, and non-prose layouts (e.g. order forms, menus) — the UI surfaces a warning when this is detected, but extraction may still be inaccurate
- Multi-column PDF layouts aren't correctly handled yet — text may read out of order
- No support yet for PDFs over ~30 pages — long documents aren't chunked, so very large files may exceed context limits
- No groundedness/hallucination check yet — structured output is schema-valid but not independently verified against source text
- "Confidence" in summaries is self-reported by the model, not independently verified
- Gmail integration is read-only and limited to the 10 most recent inbox emails; no search or full inbox browsing yet
- Link previews show the linking domain, which for marketing emails is often a tracking/redirect domain rather than the final destination
