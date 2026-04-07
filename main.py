import streamlit as st
import pandas as pd
from fpdf import FPDF
import re

# 核心：PDF 报告生成类（纯英文版，彻底避开编码报错）
class AuditReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Tax Audit Report 2026", ln=True, align="C")
        self.ln(10)

def create_pdf_report(income, credit, logs, audit_results):
    pdf = AuditReport()
    pdf.add_page()
    
    # 第一部分：家庭报税摘要
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "1. Family Tax Summary", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Estimated Household Income: ${income:,}", ln=True)
    pdf.cell(0, 8, f"Calculated Credits/Adjustments: ${credit:,}", ln=True)
    pdf.ln(5)

    # 第二部分：1099 审计结果
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "2. Brokerage 1099 Audit Results", ln=True)
    pdf.set_font("Helvetica", "", 10)
    
    if audit_results:
        for res in audit_results:
            # 强制转换为纯英文文本输出
            # 第 33 行左右，把 0 改成 190
    pdf.cell(190, 8, f"Estimated Household Income: ${income:,}", ln=True)
    pdf.cell(190, 8, f"Calculated Credits/Adjustments: ${credit:,}", ln=True)
    
    # 第 41 行左右，把 0 改成 190
    for res in audit_results:
        safe_text = str(res).encode('ascii', 'ignore').decode('ascii')
        pdf.multi_cell(190, 8, f"- {safe_text}")

# --- Streamlit UI 界面设计 ---
st.set_page_config(page_title="TingTax Pro", layout="wide")
st.title("🚀 华人报税助手 Pro (2026 结案版)")
st.markdown("---")

col1, col2 = st.columns([1, 1.2])
audit_summary = []

with col1:
    st.subheader("🏠 家庭报税避坑测算")
    income = st.number_input("家庭年预计总收入 (MAGI)", value=150000, step=1000)
    dependents = st.number_input("扶养人数", value=1, min_value=0)
    
    if st.button("开始测算并保存结果"):
        st.success("✅ 数据已锁定，准备生成报告")

with col2:
    st.subheader("📂 券商 1099 智能审计")
    uploaded_file = st.file_uploader("上传 Moomoo/Fidelity 原始 PDF", type=['pdf'])
    
    if uploaded_file:
        # 模拟审计逻辑（抓取你 PDF 里的关键金额）
        st.warning("WARNING: Wash Sale Disallowed Amount: $5,687.55")
        st.info("NOTICE: 1099-MISC Extra Income: $245.89")
        audit_summary = ["Wash Sale: $5,687.55", "Misc Income: $245.89"]

st.markdown("---")
if st.button("📥 一键生成 PDF 结案报告"):
    try:
        pdf_bytes = create_pdf_report(income, 0, [], audit_summary)
        st.download_button(
            label="点击下载审计报告",
            data=pdf_bytes,
            file_name="Tax_Audit_Report_2026.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"PDF Error: {str(e)}")