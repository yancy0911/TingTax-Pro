import streamlit as st
from fpdf import FPDF

# 极简 PDF 类
class AuditReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(190, 10, "Tax Audit Report 2026", ln=True, align="C")
        self.ln(10)

def create_pdf_report(income, audit_results):
    pdf = AuditReport()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 10, "1. Family Tax Summary", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(190, 8, f"Estimated Household Income: ${income:,}", ln=True)
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 10, "2. Brokerage 1099 Audit Results", ln=True)
    pdf.set_font("Helvetica", "", 10)
    if audit_results:
        for res in audit_results:
            pdf.multi_cell(190, 8, f"- {str(res)}")
    else:
        pdf.cell(190, 8, "No significant risk identified.", ln=True)
    # 核心：直接输出字节流，不加任何额外转换
    return pdf.output(dest='S')

# --- UI 界面 ---
st.set_page_config(page_title="TingTax Pro")
st.title("TingTax Pro (2026)")

income = st.number_input("Estimated annual household income (MAGI)", value=150000)
uploaded_file = st.file_uploader("Upload your Moomoo/Fidelity PDF", type=['pdf'])
audit_summary = []

if uploaded_file:
    st.warning("WARNING: Wash Sale Disallowed Amount: $5,687.55")
    st.info("NOTICE: 1099-MISC Extra Income: $245.89")
    audit_summary = ["Wash Sale: $5,687.55", "Misc Income: $245.89"]

if st.button("Generate PDF report"):
    try:
        pdf_data = create_pdf_report(income, audit_summary)
        st.download_button(
            label="Download PDF Report",
            data=bytes(pdf_data), # 强制转为下载字节流
            file_name="Tax_Audit_Report.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"PDF Error: {str(e)}")