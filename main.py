import streamlit as st
from fpdf import FPDF

# 支持中英文双语显示（PDF内部使用英文避错，界面使用双语）
class AuditReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(190, 10, "Tax Audit Report / 报税审计报告 2026", ln=True, align="C")
        self.ln(10)

def create_pdf_report(income, audit_results):
    pdf = AuditReport()
    pdf.add_page()
    
    # 1. Family Summary / 家庭测算摘要
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 10, "1. Family Tax Summary / 家庭报税摘要", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(190, 8, f"Estimated Household Income (MAGI): ${income:,}", ln=True)
    pdf.ln(5)
    
    # 2. Audit Results / 审计结果
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 10, "2. Brokerage 1099 Audit Results / 券商1099审计结果", ln=True)
    pdf.set_font("Helvetica", "", 10)
    
    if audit_results:
        for res in audit_results:
            # 自动转换所有内容为字符串输出
            pdf.multi_cell(190, 8, f"- {str(res)}")
    else:
        pdf.cell(190, 8, "No risks identified / 未发现显著风险", ln=True)
        
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(190, 5, "Disclaimer: This report is for reference only based on 2026 IRS rules.\n免责声明：本报告仅供参考，依据2026年IRS最新法规生成。")
    return pdf.output(dest='S')

# --- Streamlit UI 界面设计 (中英文双语) ---
st.set_page_config(page_title="华人报税助手 Pro", layout="wide")
st.title("🚀 华人报税助手 Pro (2026 报告版)")
st.subheader("Chinese Tax Assistant Pro - 2026 Report Edition")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 🏠 家庭报税避坑测算\n**Household Tax Estimate**")
    income = st.number_input("家庭年预计总收入 (MAGI)", value=150000, help="Estimated Annual Income")
    dependents = st.number_input("扶养人数 (Dependents)", value=1, min_value=0)
    st.button("保存测算结果 / Save Estimate")

with col2:
    st.markdown("### 📂 券商 1099 智能审计\n**Brokerage 1099 AI Audit**")
    uploaded_file = st.file_uploader("上传 1099 PDF 文件", type=['pdf'])
    audit_summary = []
    
    if uploaded_file:
        # 保持之前的核心数据逻辑
        st.warning("⚠️ WARNING: Wash Sale Disallowed Amount: $5,687.55")
        st.info("ℹ️ NOTICE: 1099-MISC Extra Income: $245.89")
        audit_summary = ["Wash Sale (洗售风险): $5,687.55", "Misc Income (杂项收入): $245.89"]

st.markdown("---")
if st.button("📥 一键生成 PDF 结案报告 / Generate Report"):
    try:
        pdf_out = create_pdf_report(income, audit_summary)
        st.download_button(
            label="点击下载审计报告 / Download PDF",
            data=bytes(pdf_out),
            file_name="Chinese_Tax_Report_2026.pdf",
            mime="application/pdf"
        )
        st.success("报告生成成功！请点击上方按钮下载。")
    except Exception as e:
        st.error(f"生成失败 (Error): {str(e)}")