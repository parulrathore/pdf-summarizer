import streamlit as st
import json
import tempfile
import os

from extract import extract_text_from_pdf, is_extraction_poor
from summarize import summarize_text
from extract_email import extract_text_from_eml
from summarize import summarize_email

st.set_page_config(page_title="PDF & Email Summarizer", page_icon="📄", layout="centered")

st.title("📄 PDF & Email Summarizer")

source_type = st.radio("Source type", ["PDF", "Email (.eml)"], horizontal=True)

if source_type == "PDF":
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            with st.spinner("Extracting text..."):
                extraction = extract_text_from_pdf(tmp_path)
                pages = extraction["pages"]
                full_text = "\n\n".join(f"[Page {p['page']}]\n{p['text']}" for p in pages)

            st.success(f"Extracted {len(pages)} pages, {len(full_text)} characters (method: {extraction['method']})")

            if extraction["low_confidence"]:
                st.error(
                    "⚠️ This appears to be a low-quality scan or a complex layout. "
                    "Text extraction may be inaccurate, and the summary below could be unreliable."
                )

            # with st.expander("View raw extracted text"):
            #     st.text(full_text[:3000] + ("..." if len(full_text) > 3000 else ""))

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

                # with st.expander("Raw JSON"):
                #     st.json(result.model_dump())

        finally:
            os.unlink(tmp_path)
    else:
        st.info("Upload a PDF file to get started.")

else:  # Email
    uploaded_file = st.file_uploader("Choose an .eml file", type="eml")

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".eml") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            with st.spinner("Extracting email..."):
                extraction = extract_text_from_eml(tmp_path)

            st.success(f"Extracted email: {extraction['metadata']['subject']}")

            with st.expander("View raw extracted text"):
                st.text(extraction["full_text"][:3000])

            if st.button("Summarize", type="primary"):
                with st.spinner("Calling Claude..."):
                    result = summarize_email(extraction["full_text"])

                st.subheader(result.subject)
                st.caption(f"From: {result.sender} · Sentiment: {result.sentiment} · Confidence: {result.confidence}")
                st.write(result.summary)

                st.subheader("Key Points")
                for kp in result.key_points:
                    st.markdown(f"- {kp}")

                if result.action_items:
                    st.subheader("Action Items")
                    for ai in result.action_items:
                        st.markdown(f"- {ai}")

                st.markdown(f"**Requires response:** {'Yes' if result.requires_response else 'No'}")

              #  with st.expander("Raw JSON"):
               #     st.json(result.model_dump())

        finally:
            os.unlink(tmp_path)
    else:
        st.info("Upload an .eml file to get started.")