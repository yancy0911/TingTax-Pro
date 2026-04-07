import streamlit as st
from fpdf import FPDF
import os
from pypdf import PdfReader
import re

# --- 智能扫描逻辑：从 PDF 提取数据 ---
def extract_tax_data(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    # 1. 抓取姓名 (匹配 TINGTING FU)
    name_match = re.search(r"Your first name.*?\n(.*?)\n", text)
    last_match = re.search(r"Last name.*?\n(.*?)\n", text)
    full_name = f"{name_match.group(1)} {last_match.group(1)}" if name_match and last_match else "未识别"
    
    # 2. 抓取 AGI (匹配 Adjusted Gross Income 9,293)
    agi_match = re.search(r"adjusted gross income.*?(\d+[,.]\d+)", text, re.IGNORECASE)
    agi = float(agi_match.group(1).replace(',', '')) if agi_match else 0.0
    
    # 3. 抓取报税身份 (匹配 Single)
    status = "Single" if "Single" in text else "Married filing jointly"
    
    return full_name, agi, status

# --- PDF 生成逻辑 (保持中英双语) ---
def create_pdf_report(name, income, status, audit_results):
    pdf = FPDF()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(current_dir, "font.ttf")
    
    if os.path.exists(font_path):
        pdf.add_font("Chinese", style="", fname=font_path)
        pdf.add_font("Chinese", style="B", fname=font_path)
        pdf.set_font("Chinese", size=10)
        has_chinese = True
    else:
        pdf.set_font("helvetica", size=10)
        has_chinese = False
    
    pdf.add_page()
    font_name = "Chinese" if has_chinese else "helvetica"
    
    pdf.set_font(font_name, "B", 16)
    pdf.cell(190, 10, f"Tax Audit Report for {name}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    
    pdf.set_font(font_name, "B", 12)
    pdf.cell(190, 10, "1. Financial Summary / 财务摘要", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(font_name, "", 10)
    pdf.cell(190, 8, f"Taxpayer / 纳税人: {name}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(190, 8, f"Filing Status / 报税身份: {status}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(190, 8, f"AGI / 调整后总收入: ${income:,}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font(font_name, "B", 12)
    pdf.cell(190, 10, "2. Smart Audit / 智能审计预警", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(font_name, "", 10)
    for res in audit_results:
        pdf.multi_cell(190, 8, f"● {str(res)}")
        
    return pdf.output()

# --- 审计逻辑 (复刻 TINGTING FU 案例) ---
def run_audit_engine(income, status):
    logs = []
    se_tax = round(income * 0.9235 * 0.153)
    if income > 400:
        logs.append(f"⚠️ 自雇税预警: 您的收入属于自雇，需缴纳约 ${se_tax:,} 自雇税。")
    if income < 14600:
        logs.append("✅ 所得税豁免: 收入低于标准扣除额，预计联邦所得税为 $0。")
    if income < 17000:
        logs.append("💰 福利提醒: 您可能符合联邦及州 EIC 退税补贴资格。")
    return logs

# --- Streamlit UI ---
st.set_page_config(page_title="华人报税助手 Pro", layout="wide")
st.title("🚀 华人报税助手 Pro (全自动扫描版)")

st.markdown("### 📂 第一步：上传税表扫描")
uploaded_file = st.file_uploader("请上传 1040 税表 PDF 进行全自动审计", type=['pdf'])

scanned_name = "未识别"
scanned_income = 10000.0
scanned_status = "Single"

if uploaded_file:
    with st.spinner('正在进行 AI 深度扫描...'):
        scanned_name, scanned_income, scanned_status = extract_tax_data(uploaded_file)
        st.success(f"✅ 扫描完成！识别到纳税人: **{scanned_name}**")

st.markdown("---")
st.markdown("### 📝 第二步：核对并确认数据")
col1, col2, col3 = st.columns(3)
with col1:
    final_name = st.text_input("纳税人姓名", value=scanned_name)
with col2:
    final_income = st.number_input("AGI 收入", value=float(scanned_income))
with col3:
    final_status = st.selectbox("报税身份", ["Single", "Married filing jointly"], 
                               index=0 if scanned_status == "Single" else 1)

audit_results = run_audit_engine(final_income, final_status)

st.markdown("---")
st.markdown("### 🔍 第三步：查看审计结果")
for item in audit_results:
    st.write(item)

if st.button("📥 下载全自动结案报告"):
    pdf_bytes = create_pdf_report(final_name, final_income, final_status, audit_results)
    st.download_button("点击下载 PDF", data=bytes(pdf_bytes), file_name=f"Report_{final_name}.pdf")