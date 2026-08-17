import streamlit as st
import json
import tempfile
import os

from extract import extract_text_from_pdf
from summarize import summarize_text, summarize_email
from extract_email import extract_text_from_eml
from extract_gmail import list_recent_emails, extract_text_from_gmail_message

st.set_page_config(page_title="PDF & Email Summarizer", page_icon="📄", layout="centered")

st.title("📄 PDF & Email Summarizer")

source_type = st.radio("Source type", ["PDF", "Email (.eml)", "Gmail"], horizontal=True)


def render_email_result(extraction):
    """Shared rendering logic for .eml and Gmail branches."""
    metadata = extraction["metadata"]

    st.subheader(metadata["subject"])
    st.caption(f"{metadata['date']} · Category: {metadata['category']}")

    st.markdown(f"""
1. **From:** {metadata['sender']}
2. **To:** {metadata['to']}
3. **Subject:** {metadata['subject']}
4. **Date:** {metadata['date']}
""")

    # if metadata['links']:
    #     for i, link in enumerate(metadata['links'], start=1):
    #         st.markdown(f"   - [Link {i}]({link})")
    # else:
    #     st.markdown("   - None")

    if st.button("Summarize", type="primary"):
        with st.spinner("Calling Claude..."):
            result = summarize_email(extraction["full_text"])

        if result.sentiment == "urgent":
            st.markdown("6. **Urgency:** :red[**URGENT**]")
        else:
            st.markdown(f"6. **Urgency:** Not urgent (sentiment: {result.sentiment})")

        st.write(result.summary)

        st.subheader("Key Points")
        for kp in result.key_points:
            st.markdown(f"- {kp}")

        if result.action_items:
            st.subheader("Action Items")
            for ai in result.action_items:
                st.markdown(f"- {ai}")

        st.markdown(f"**Requires response:** {'Yes' if result.requires_response else 'No'}")

        # with st.expander("Raw JSON"):
        #     st.json(result.model_dump())


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

elif source_type == "Email (.eml)":
    uploaded_file = st.file_uploader("Choose an .eml file", type="eml")

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".eml") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            with st.spinner("Extracting email..."):
                extraction = extract_text_from_eml(tmp_path)

            render_email_result(extraction)

        finally:
            os.unlink(tmp_path)
    else:
        st.info("Upload an .eml file to get started.")

else:  # Gmail
    with st.spinner("Fetching recent emails..."):
        recent = list_recent_emails(max_results=10)

    options = {f"{e['subject']} — {e['sender']}": e["id"] for e in recent}
    selected_label = st.selectbox("Choose a recent email", list(options.keys()))

    if selected_label:
        message_id = options[selected_label]
        extraction = extract_text_from_gmail_message(message_id)
        render_email_result(extraction)