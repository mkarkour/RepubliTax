import os
import sys
from datetime import datetime

import pandas as pd
import pymupdf
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.reader import Reader
from src.utils_files import FileUtils
from src.writer import Writer

sys.path.append(os.path.abspath("../"))

reader = Reader()
writer = Writer()


def display_dataframes(user_data: dict[str, dict]) -> None:
    """Display extracted tax data in Streamlit.

    Args:
        user_data (dict[str, dict]): Extracted data structured by page.
    """
    st.subheader("📊 Extracted Tax Information")

    for i in range(1, len(user_data)):
        page_info = user_data[f"page_{i}"]
        purpose = page_info["purpose"]
        rate = page_info["rate"]
        summary = page_info["summary"]

        st.header(f"📄 Page {i}: {purpose} (Rate: {rate})")

        st.dataframe(pd.DataFrame(page_info["df"]),
                     use_container_width=True,
                     hide_index=True,
                     column_config={
                         "DATE": st.column_config.DateColumn("Date", format="DD/MM/YYYY")}
                     )

        # Summary section
        tax_basis = summary.get("TOTAL_TAX_BASIS_IN_EUR", 0.0)
        tax_amount = summary.get("TOTAL_TAX_AMOUNT_IN_EUR", 0.0)
        transactions = summary.get("TOTAL_TRANSACTIONS", 0)

        summary_html = f"""
        <div style="display: flex; gap: 1.5rem; margin: 1rem 0; padding: 1rem;
        background: #f8f9fa; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="flex: 1;">
            <div style="font-size: 0.8rem; color: #6c757d;">Tax Basis</div>
            <div style="font-size: 1.2rem; color: #28a745; font-weight: 600;">
            €{tax_basis:,.2f}
            </div>
        </div>
        <div style="flex: 1;">
            <div style="font-size: 0.8rem; color: #6c757d;">Tax Amount</div>
            <div style="font-size: 1.2rem; color: #dc3545; font-weight: 600;">
            €{tax_amount:.2f}
            </div>
        </div>
        <div style="flex: 1;">
            <div style="font-size: 0.8rem; color: #6c757d;">Total Transactions</div>
            <div style="font-size: 1.2rem; font-weight: 600;">{transactions}</div>
        </div>
        </div>
        """
        st.markdown(summary_html, unsafe_allow_html=True)


def upload_section() -> None:
    """Handles the document upload and processing with an improved user experience."""
    st.header("📤 Upload Your PDF Documents")

    upload_tab, sample_tab = st.tabs(["Upload PDF", "Use Sample Document"])

    with upload_tab:
        uploaded_file = st.file_uploader("Upload source PDF", type=["pdf"],
                                         help="Upload your Trade Republic tax report PDF")

        if not uploaded_file:
            st.info("Please upload a Tax Report to start processing", icon="ℹ️")

    with sample_tab:
        docs_dir = FileUtils.get_path("../docs")
        form_path = os.path.join(docs_dir, "form.pdf")

        st.subheader("📄 Form Document")

        if os.path.exists(form_path):
            st.info("A form document (`form.pdf`) is already available.")
            if st.toggle("Do you want to display it?"):
                form_doc = pymupdf.open(form_path)
                preview_bytes_form = form_doc.write()
                preview_form = pymupdf.open(stream=preview_bytes_form, filetype="pdf")
                for page_num in range(preview_form.page_count):
                    page = preview_form[page_num]
                    zoom_x = 2.0
                    zoom_y = 2.0
                    matrix = pymupdf.Matrix(zoom_x, zoom_y)
                    pix = page.get_pixmap(matrix=matrix)
                    img_bytes = pix.tobytes("png")
                    st.image(
                        img_bytes,
                        caption=f"Page {page_num + 1}",
                        use_container_width=True)

            with open(form_path, "rb") as f:
                st.download_button("📥 Download Existing Form", f, file_name="form.pdf")

            if st.checkbox("Replace the existing document"):
                uploaded_form = st.file_uploader("Upload a new form (PDF only)",
                                                 type=["pdf"])
                if uploaded_form is not None:
                    new_form_path = os.path.join(docs_dir, "form.pdf")
                    with open(new_form_path, "wb") as f:
                        f.write(uploaded_form.read())
                    st.success("The form document has been successfully replaced.")
        else:
            st.warning("No form document (`form.pdf`) was found.")

            uploaded_form = st.file_uploader("Upload a form (PDF only)", type=["pdf"])
            if uploaded_form is not None:
                new_form_path = os.path.join(docs_dir, "form.pdf")
                with open(new_form_path, "wb") as f:
                    f.write(uploaded_form.read())
                st.success("The form document has been uploaded successfully.")

    if uploaded_file:
        national_n = (
            st.text_input(
                "Enter your national number:",
                placeholder="e.g., 99.99.99-999.99",
                help="Your Belgian national number in format XX.XX.XX-XXX.XX"))

        signature_path = os.path.join(FileUtils.get_path("../docs"), "signature.png")

        signed = st.toggle(
            "Add signature to document",
            help="Enable this to add your signature to the final document"
        )

        if signed:
            if os.path.exists(signature_path) or any(
                os.path.exists(os.path.join(FileUtils.get_path("../docs"), f"signature{ext}"))
                for ext in [".jpg", ".jpeg", ".png"]
            ):

                signature_files = [
                    os.path.join(FileUtils.get_path("../docs"), f)
                    for f in os.listdir(FileUtils.get_path("../docs"))
                    if f.startswith("signature") and f.split(".")[-1].lower() in ["jpg",
                                                                                  "jpeg",
                                                                                  "png"]
                ]

                if signature_files:
                    signature_path = signature_files[0]
                    st.info(f"Existing signature found: {os.path.basename(signature_path)}")

                    replace_signature = st.radio(
                        "Do you want to use the existing signature or upload a new one?",
                        options=["Use existing", "Upload new"],
                        index=0
                    )

                    if replace_signature == "Upload new":
                        sign = st.file_uploader(
                            "Upload new signature image:",
                            type=["jpg", "jpeg", "png"],
                            help="""Upload a clear image of your signature on white
                            background"""
                        )

                        if sign is not None:
                            docs_path = FileUtils.get_path("../docs")
                            _, file_extension = os.path.splitext(sign.name)
                            new_file_name = f"signature{file_extension}"
                            file_path = os.path.join(docs_path, new_file_name)

                            with open(file_path, "wb") as f:
                                f.write(sign.getbuffer())
                            signature_path = file_path
                            st.success("Signature updated successfully!")
                else:
                    sign = st.file_uploader(
                        "Upload signature image:",
                        type=["jpg", "jpeg", "png"],
                        help="Upload a clear image of your signature on white background"
                    )

                    if sign is not None:
                        docs_path = FileUtils.get_path("../docs")
                        _, file_extension = os.path.splitext(sign.name)
                        new_file_name = f"signature{file_extension}"
                        file_path = os.path.join(docs_path, new_file_name)

                        with open(file_path, "wb") as f:
                            f.write(sign.getbuffer())
                        signature_path = file_path
                        st.success("Signature uploaded successfully!")
            else:
                sign = st.file_uploader(
                    "Upload signature image:",
                    type=["jpg", "jpeg", "png"],
                    help="Upload a clear image of your signature on white background"
                )

                if sign is not None:
                    docs_path = FileUtils.get_path("../docs")
                    _, file_extension = os.path.splitext(sign.name)
                    new_file_name = f"signature{file_extension}"
                    file_path = os.path.join(docs_path, new_file_name)

                    with open(file_path, "wb") as f:
                        f.write(sign.getbuffer())
                    signature_path = file_path
                    st.success("Signature uploaded successfully!")

        if st.button("Validate infos"):
            with st.status("Processing document...", expanded=True) as status:
                try:
                    pdf_bytes = uploaded_file.read()
                    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

                    extracted_data = reader.extract_full_content(doc)

                    extracted_data["page_0"]["user_infos"]["national_number"] = national_n

                    status.update(label="✅ Processing completed!", state="complete")

                    st.subheader("📋 Results")

                    data_tab, preview_tab, email_tab = (
                        st.tabs(["📊 Extracted Data", "👁️ Preview", "📧 Email"]))

                    with data_tab:
                        display_dataframes(extracted_data)

                    with preview_tab:
                        with st.spinner("Generating your filled document..."):
                            use_signature = (
                                signed
                                and signature_path
                                and os.path.exists(signature_path)
                            )

                            filled_form = (
                                writer.fill_document(
                                    extracted_data,
                                    to_sign=use_signature,
                                    save_it=False))

                        preview_bytes = filled_form.write()

                        st.download_button(
                            label="⬇️ Download Filled PDF",
                            data=preview_bytes,
                            file_name=(
                                f"filled_form_{datetime.now().strftime("%Y-%m")}.pdf"),
                            mime="application/pdf",
                            use_container_width=True
                        )

                        preview_doc = pymupdf.open(stream=preview_bytes, filetype="pdf")
                        for page_num in range(preview_doc.page_count):
                            page = preview_doc[page_num]
                            zoom_x = 2.0
                            zoom_y = 2.0
                            matrix = pymupdf.Matrix(zoom_x, zoom_y)
                            pix = page.get_pixmap(matrix=matrix)
                            img_bytes = pix.tobytes("png")
                            st.image(
                                img_bytes,
                                caption=f"Page {page_num + 1}",
                                use_container_width=True)

                    with email_tab:
                        email = (
                            st.text_input(
                                "Email address:",
                                placeholder="your@email.com"))

                        if st.button("Send Document") and email:
                            # Add email sending logic here
                            st.success(f"Document sent to {email}")

                except ValueError as e:
                    status.update(label=f"❌ Error: {str(e)}", state="error")
                    st.error(f"Error details: {str(e)}")
                    st.info("Please ensure you've uploaded a valid Tax Report document")


def sidebar() -> None:
    """Creates the sidebar with instructions and features."""
    with st.sidebar:
        st.header("ℹ️ Instructions")
        st.markdown("""
        1. Upload your source PDF document
        2. Enter your national number
        3. Wait for automatic processing
        4. Download your filled PDF form
        """)

        st.header("🛠️ Features")
        st.markdown("""
        - PDF content extraction
        - Automated tax form filling
        - Secure local processing
        """)


def footer() -> None:
    """Displays the footer with credits."""
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>Powered by mkarkour
    • Secure Document Processing</div>
    """, unsafe_allow_html=True)


def main() -> None:
    """Main function that runs the Streamlit app."""
    st.set_page_config(page_title="MTO Form Filler", page_icon="✏️", layout="centered")

    # Load custom styles
    css_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "style.css"))
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Header section with logo
    col1, col2 = st.columns([1, 4])
    with col1:
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "tr.png"))
        if os.path.exists(logo_path):
            st.image(logo_path, width=100)

    with col2:
        st.title("📑 Automated Monthly Tax Report")
        st.caption(
            "Automate your tax document processing with code-powered form filling.")

    # Main content
    upload_section()
    sidebar()
    footer()


if __name__ == "__main__":
    main()
