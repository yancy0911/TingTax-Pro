import streamlit as st
import pdfplumber
import re
from fpdf import FPDF
import io

# --- 核心逻辑引擎：2026 IRS 避坑算法 ---
def calculate_tax_logic(income, dependents):
    total_credit = 0
    details = []
    # 2026 标准额度 (对标最新法案)
    CHILD_CREDIT = 2200  # 17岁以下且有SSN
    OTHER_CREDIT = 500   # 父母/ITIN/学生
    
    for dep in dependents:
        if dep['age'] < 17 and dep['has_ssn']:
            total_credit += CHILD_CREDIT
            details.append(f"✅ {dep['name']}: 符合 Child Tax Credit, 预估获得 ${CHILD_CREDIT}")
        else:
            total_credit += OTHER_CREDIT
            details.append(f"✅ {dep['name']}: 符合 Other Dependent Credit, 预估获得 ${OTHER_CREDIT}")
    
    # 自动识别高收入缩减 (Phase-out)
    if income > 400000:
        reduction = ((income - 400000) // 1000) * 50
        total_credit = max(0, total_credit - reduction)
        details.append(f"⚠️ 会计预警：您的MAGI超过$40万，抵税额依法缩减了 ${reduction}。")
    return total_credit, details

# --- PDF 报告生成函数 ---
def create_pdf_report(income, credit, logs, audit_results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "2026 Chinese Tax Compliance Audit Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Household MAGI: ${income}", ln=True)
    pdf.cell(0, 10, f"Estimated Tax Credits: ${credit}", ln=True)
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Dependent Breakdown:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for log in logs:
        pdf.multi_cell(0, 8, log)
    
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Brokerage 1099 Audit Summary:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for res in audit_results:
        pdf.multi_cell(0, 8, res)
    
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(0, 8, "Disclaimer: Based on 2026 OBBBA IRS rules. Please provide this to your CPA for final review.")
    return pdf.output()

# --- Streamlit UI 界面设计 ---
st.set_page_config(page_title="华人报税助手 Pro", layout="wide")
st.title("🚀 华人报税助手 Pro (2026 报告版)")
st.markdown("---")

col1, col2 = st.columns([1, 1.2])
logs = []
credit = 0
audit_summary = []

with col1:
    st.header("🏠 家庭报税避坑测算")
    inc = st.number_input("家庭年预计总收入 (MAGI)", value=150000)
    num = st.number_input("抚养人数", min_value=0, value=1)
    deps = []
    for i in range(num):
        with st.expander(f"家属 #{i+1} 详情"):
            name = st.text_input("姓名", key=f"n{i}", value=f"家属{i+1}")
            age = st.number_input("年龄", key=f"a{i}", value=10)
            ssn = st.checkbox("有 SSN (非ITIN)", key=f"s{i}", value=True)
            deps.append({"name": name, "age": age, "has_ssn": ssn})
    
    if st.button("开始测算并保存结果"):
        credit, logs = calculate_tax_logic(inc, deps)
        st.metric("应得抵免总额", f"${credit}")
        for log in logs: st.write(log)

with col2:
    st.header("📂 券商 1099 智能审计")
    file = st.file_uploader("上传 Moomoo/Fidelity 原始 PDF", type="pdf")
    if file:
        with st.spinner("审计中..."):
            with pdfplumber.open(file) as pdf:
                txt = "".join([p.extract_text() for p in pdf.pages])
                pro = re.findall(r"Grand total\s+([\d,]+\.\d+)", txt)
                wash = re.findall(r"Total Short-term\s+[\d,.]+\s+[\d,.]+\s+[\d,.]+\s+([\d,]+\.\d+)", txt)
                misc = re.findall(r"3-\s+Other\s+income\s+([\d,]+\.\d+)", txt)
                
                if pro: audit_summary.append(f"Total Proceeds: ${pro[0]}")
                if wash: audit_summary.append(f"WARNING: Wash Sale Disallowed Amount: ${wash[0]}")
                if misc: audit_summary.append(f"NOTICE: 1099-MISC Extra Income: ${misc[0]}")
                
                for item in audit_summary: st.info(item)

st.markdown("---")
if st.button("📥 一键生成 PDF 结案报告"):
    if not audit_summary and not logs:
        st.error("请先完成左侧测算或右侧 PDF 上传")
    else:
        pdf_bytes = create_pdf_report(inc, credit, logs, audit_summary)
        st.download_button(
            label="点击下载您的税务诊断报告",
            data=pdf_bytes,
            file_name="Tax_Audit_Report_2026.pdf",
            mime="application/pdf"
        )

st.caption("© 2026 Tingting Tax Tech. 算法严格对标 IRS 2026 最新法规。")