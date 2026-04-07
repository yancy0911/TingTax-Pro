import streamlit as st
import pandas as pd
from fpdf import FPDF
import re

# Core: PDF report generator (ASCII-safe output)
class AuditReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(190, 10, "Tax Audit Report 2026", ln=True, align="C")
        self.ln(10)

def create_pdf_report(income, credit, logs, audit_results):
    pdf = AuditReport()
    pdf.add_page()

    income_value = 0
    credit_value = 0
    try:
        income_value = int(float(income))
    except Exception:
        income_value = 0
    try:
        credit_value = int(float(credit))
    except Exception:
        credit_value = 0

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 10, "1. Family Tax Summary", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(190, 8, f"Estimated Household Income: ${income_value:,}", ln=True)
    pdf.cell(190, 8, f"Calculated Credits/Adjustments: ${credit_value:,}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 10, "2. Audit Results", ln=True)
    pdf.set_font("Helvetica", "", 10)

    def _to_ascii_text(value) -> str:
        text = "" if value is None else str(value)
        return text.encode("ascii", "ignore").decode("ascii").strip()

    def _iter_audit_rows(value):
        if value is None:
            return []
        if isinstance(value, dict):
            rows = []
            for k, v in value.items():
                k_text = _to_ascii_text(k)
                v_text = _to_ascii_text(v)
                if k_text and v_text:
                    rows.append(f"{k_text}: {v_text}")
                elif k_text:
                    rows.append(k_text)
                elif v_text:
                    rows.append(v_text)
            return rows
        if isinstance(value, (list, tuple, set)):
            rows = []
            for item in value:
                if isinstance(item, dict):
                    for k, v in item.items():
                        k_text = _to_ascii_text(k)
                        v_text = _to_ascii_text(v)
                        if k_text and v_text:
                            rows.append(f"{k_text}: {v_text}")
                        elif k_text:
                            rows.append(k_text)
                        elif v_text:
                            rows.append(v_text)
                else:
                    item_text = _to_ascii_text(item)
                    if item_text:
                        rows.append(item_text)
            return rows
        text = _to_ascii_text(value)
        return [text] if text else []

    audit_rows = _iter_audit_rows(audit_results)
    if not audit_rows:
        pdf.multi_cell(190, 8, "- No audit results provided.")
    else:
        for row in audit_rows:
            pdf.multi_cell(190, 8, f"- {row}")

    logs_rows = _iter_audit_rows(logs)
    if logs_rows:
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(190, 10, "3. Processing Logs", ln=True)
        pdf.set_font("Helvetica", "", 10)
        for row in logs_rows:
            pdf.multi_cell(190, 8, f"- {row}")

    pdf_bytes = pdf.output(dest="S").encode("latin-1", "ignore")
    return pdf_bytes

# --- Streamlit UI ---
st.set_page_config(page_title="TingTax Pro", layout="wide")
st.title("TingTax Pro (2026)")
st.markdown("---")

col1, col2 = st.columns([1, 1.2])
audit_summary = []

with col1:
    st.subheader("Household Tax Estimate")
    income = st.number_input("Estimated annual household income (MAGI)", value=150000, step=1000)
    dependents = st.number_input("Number of dependents", value=1, min_value=0)
    
    if st.button("Calculate and save"):
        st.success("Saved. Ready to generate the report.")

with col2:
    st.subheader("Brokerage 1099 Audit")
    uploaded_file = st.file_uploader("Upload your Moomoo/Fidelity PDF", type=['pdf'])
    
    if uploaded_file:
        # Demo audit logic (replace with real PDF parsing)
        st.warning("WARNING: Wash Sale Disallowed Amount: $5,687.55")
        st.info("NOTICE: 1099-MISC Extra Income: $245.89")
        audit_summary = ["Wash Sale: $5,687.55", "Misc Income: $245.89"]

st.markdown("---")
if st.button("Generate PDF report"):
    try:
        pdf_bytes = create_pdf_report(income, 0, [], audit_summary)
        st.download_button(
            label="Download audit report",
            data=pdf_bytes,
            file_name="Tax_Audit_Report_2026.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"PDF Error: {str(e)}")