import streamlit as st
from fpdf import FPDF
import os
from pypdf import PdfReader
import re

# --- 1. 智能扫描引擎：从 PDF 提取并清洗数据 ---
def extract_tax_data(file):
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        # 抓取姓名 (匹配 Form 1040 标准格式)
        name_match = re.search(r"Your first name.*?\n(.*?)\n", text)
        last_match = re.search(r"Last name.*?\n(.*?)\n", text)
        
        if name_match and last_match:
            raw_name = f"{name_match.group(1)} {last_match.group(1)}"
            # 清洗姓名：只保留字母和空格，去掉数字和特殊字符
            full_name = re.sub(r'[^a-zA-Z\s]', '', raw_name).strip()
        else:
            full_name = "未识别纳税人"
        
        # 抓取 AGI (匹配 Adjusted Gross Income)
        agi_match = re.search(r"adjusted gross income.*?(\d+[,.]\d+)", text, re.IGNORECASE)
        agi = float(agi_match.group(1).replace(',', '')) if agi_match else 0.0
        
        # 抓取报税身份
        status = "Single" if "Single" in text else "Married filing jointly"
        
        return full_name, agi, status
    except Exception as e:
        return f"扫描出错: {e}", 0.0, "Single"

# --- 2. 审计引擎：内置真实税法逻辑 ---
def run_audit_engine(income, status):
    logs = []
    # 自雇税核算逻辑 (根据真实税表 Schedule SE)
    se_tax = round(income * 0.9235 * 0.153)
    if income > 400:
        logs.append(f"⚠️ 自雇税风险预警: 您的收入属于自雇类别，需预留约 ${se_tax:,} 缴纳社会安全与医保税。")
    
    # 联邦所得税门槛检查
    std_deduction = 14600 if status == "Single" else 29200
    if income < std_deduction:
        logs.append(f"✅ 所得税豁免: 您的收入低于标准扣除额 ${std_deduction:,}，联邦个人所得税预计为 $0。")
    
    # 低收入补贴 (EIC) 资格检测
    if income < 17000:
        logs.append("💰 潜在福利提醒: 识别到低收入状态，您可能符合联邦及州 EIC 退税补贴资格。")
        
    return logs

# --- 3. 报告引擎：生成中英双语 PDF ---
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
    
    # 报告头部
    pdf.set_font(font_name, "B", 16)
    pdf.cell(190, 10, "Tax Audit Report / 华人报税助手专业审计报告", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    
    # 财务摘要
    pdf.set_font(font_name, "B", 12)
    pdf.cell(190, 10, "1. Financial Summary / 财务摘要", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(font_name, "", 10)
    pdf.cell(190, 8, f"Taxpayer / 纳税人: {name}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(190, 8, f"AGI / 调整后总收入: ${income:,}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(190, 8, f"Status / 报税身份: {status}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # 审计结论
    pdf.set_font(font_name, "B", 12)
    pdf.cell(190, 10, "2. Audit Findings / 智能审计结论", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(font_name, "", 10)
    for res in audit_results:
        pdf.multi_cell(190, 8, f"● {str(res)}")
    
    return pdf.output()

# --- 4. Streamlit UI 界面 ---
st.set_page_config(page_title="华人报税助手 Pro", layout="wide")
st.title("🚀 华人报税助手 Pro (全能自动扫描版)")
st.markdown("---")

# 上传区
uploaded_file = st.file_uploader("📂 请上传 1040 税表 PDF (系统将自动提取数据)", type=['pdf'])

scanned_name, scanned_income, scanned_status = "未识别", 0.0, "Single"

if uploaded_file:
    with st.spinner('AI 正在深度扫描税表文件...'):
        scanned_name, scanned_income, scanned_status = extract_tax_data(uploaded_file)
        st.success(f"✅ 扫描成功！识别到纳税人: {scanned_name}")

st.markdown("### 📝 数据核对与确认")
c1, c2, c3 = st.columns(3)
with c1:
    final_name = st.text_input("纳税人姓名", value=scanned_name)
with c2:
    final_income = st.number_input("AGI 收入金额", value=float(scanned_income))
with c3:
    final_status = st.selectbox("报税身份", ["Single", "Married filing jointly"], 
                               index=0 if scanned_status == "Single" else 1)

# 运行实时审计
audit_findings = run_audit_engine(final_income, final_status)

st.markdown("---")
st.markdown("### 🔍 实时审计发现")
for item in audit_findings:
    st.write(item)

# 报告生成按钮
if st.button("📥 一键生成综合 PDF 报告 / Generate Full Report"):
    try:
        pdf_bytes = create_pdf_report(final_name, final_income, final_status, audit_findings)
        st.download_button(
            label="💾 保存并下载 PDF 报告",
            data=bytes(pdf_bytes),
            file_name=f"Tax_Report_{final_name}.pdf",
            mime="application/pdf"
        )
        st.balloons()
    except Exception as e:
        st.error(f"生成失败: {e}")