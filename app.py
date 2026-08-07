import streamlit as st
import json
import tempfile
import os

from extract import extract_text_from_pdf, is_extraction_poor
from summarize import summarize_text

st.set_page_config(page_title="PDF Summarizer", page_icon="📄", layout="centered")

st.title("📄 PDF Summarizer")
st.caption("Upload a PDF to get a structured summary with key points, entities, and page references.")

uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

if uploaded_file is not None:
    # Save uploaded file to a temp path so extract.py can open it by path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        with st.spinner("Extracting text..."):
            pages = extract_text_from_pdf(tmp_path)
            full_text = "\n\n".join(f"[Page {p['page']}]\n{p['text']}" for p in pages)

        st.success(f"Extracted {len(pages)} pages, {len(full_text)} characters")

        if is_extraction_poor(pages):
            st.warning("⚠️ This looks like a scanned/image-based PDF. Extraction quality may be poor — OCR isn't wired in yet.")

        with st.expander("View raw extracted text"):
            st.text(full_text[:3000] + ("..." if len(full_text) > 3000 else ""))

        if st.button("Summarize", type="primary"):
            with st.spinner("Calling Claude..."):
                result = summarize_text(full_text)

            st.subheader(result.title)
            st.caption(f"Type: {result.document_type} · Confidence: {result.confidence}")
            st.write(result.summary)

            st.subheader("Key Points")
            for kp in result.key_points:
                page_note = f" (p.{kp.page_ref})" if kp.page_ref else ""
                st.markdown(f"- {kp.point}{page_note}")

            st.subheader("Entities")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**People**")
                for p in result.entities.people:
                    st.markdown(f"- {p}")
            with col2:
                st.markdown("**Organizations**")
                for o in result.entities.organizations:
                    st.markdown(f"- {o}")
            with col3:
                st.markdown("**Dates**")
                for d in result.entities.dates:
                    st.markdown(f"- {d}")

            with st.expander("Raw JSON"):
                st.json(result.model_dump())

    finally:
        os.unlink(tmp_path)  # clean up temp file
else:
    st.info("Upload a PDF to get started.")