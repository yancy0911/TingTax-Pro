import streamlit as st
from fpdf import FPDF
import os
from pypdf import PdfReader
import re

# --- 1. 深度扫描引擎：多维度数据抓取 ---
def extract_tax_data(file):
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        # A. 抓取姓名并深度去重 [cite: 11, 12, 14, 15]
        name_match = re.search(r"Your first name.*?\n(.*?)\n", text)
        last_match = re.search(r"Last name.*?\n(.*?)\n", text)
        if name_match and last_match:
            first = re.sub(r'[^a-zA-Z]', '', name_match.group(1).strip())
            last = re.sub(r'[^a-zA-Z]', '', last_match.group(1).strip())
            full_name = f"{first} {last}".strip()
            words = full_name.split()
            full_name = " ".join(sorted(set(words), key=words.index))
        else:
            full_name = "未识别纳税人"

        # B. 抓取业务类型 (从 Schedule C 识别) [cite: 718]
        biz_match = re.search(r"Principal business or profession.*?\n(.*?)\n", text, re.IGNORECASE)
        business_type = biz_match.group(1).strip() if biz_match else "通用劳务"

        # C. 抓取 AGI (调整后总收入) [cite: 209, 211]
        agi_match = re.search(r"adjusted gross income.*?(\d+[,.]\d+)", text, re.IGNORECASE)
        agi = float(agi_match.group(1).replace(',', '')) if agi_match else 0.0
        
        # D. 识别报税年份 [cite: 4, 231, 1156]
        year_match = re.search(r"Form 1040 \((\d{4})\)", text)
        tax_year = year_match.group(1) if year_match else "2024"
        
        return full_name, agi, business_type, tax_year
    except Exception as e:
        return "识别失败", 0.0, "未知", "2024"

# --- 2. 全能审计引擎：场景化分析 ---
def run_audit_engine(income, status, biz_type):
    logs = []
    # 自雇税核心预警 [cite: 659, 934]
    se_tax = round(income * 0.9235 * 0.153)
    if income > 400:
        logs.append(f"⚠️ 自雇税核算: 您在【{biz_type}】领域的收入需缴纳约 ${se_tax:,} 的社保医保税。")
    
    # 联邦所得税门槛 [cite: 183, 213, 228]
    std_deduction = 14600 if status == "Single" else 29200
    if income < std_deduction:
        logs.append(f"✅ 所得税豁免: 收入低于门槛 ${std_deduction:,}，联邦所得税预计为 $0。")
    
    # 低收入补贴 (EIC) 与 QBI 扣除提醒 [cite: 299, 508, 1009]
    if income < 17000:
        logs.append("💰 福利预警: 检测到低收入状态，您可能符合联邦及州 EIC 退税补贴（参考退税额 $632）。")
    if income > 0:
        logs.append(f"🛡️ 减税提醒: 针对您的【{biz_type}】收入，请核实 Form 8995 的 20% QBI 业务扣除。")
        
    return logs

# --- 3. 专业报告引擎：中英双语版 ---
def create_pdf_report(name, income, status, biz_type, year, audit_results):
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
    
    # 报告标题
    pdf.set_font(font_name, "B", 16)
    pdf.cell(190, 10, f"{year} Tax Comprehensive Report / 综合报税审计报告", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    
    # 财务档案
    pdf.set_font(font_name, "B", 12)
    pdf.cell(190, 10, "1. Taxpayer Profile / 纳税人画像", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(font_name, "", 10)
    pdf.cell(190, 8, f"Name / 姓名: {name}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(190, 8, f"Business / 业务类型: {biz_type}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(190, 8, f"AGI / 调整后总收入: ${income:,}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(190, 8, f"Status / 报税身份: {status}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # 审计专家意见
    pdf.set_font(font_name, "B", 12)
    pdf.cell(190, 10, "2. Expert Audit Opinions / 专家审计意见", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(font_name, "", 10)
    for res in audit_results:
        pdf.multi_cell(190, 8, f"● {str(res)}")
    
    return pdf.output()

# --- 4. Streamlit UI 界面 ---
st.set_page_config(page_title="华人报税助手 Pro", layout="wide")
st.title("🚀 华人报税助手 Pro (全能全自动进化版)")
st.markdown("---")

# 侧边栏：上传区
st.sidebar.header("📁 文件中心")
uploaded_file = st.sidebar.file_uploader("上传 1040 税表 PDF", type=['pdf'])

sc_name, sc_income, sc_biz, sc_year = "待扫描", 0.0, "待识别", "2024"

if uploaded_file:
    with st.spinner('AI 正在进行全表扫描...'):
        sc_name, sc_income, sc_biz, sc_year = extract_tax_data(uploaded_file)
        st.sidebar.success(f"扫描成功！年份: {sc_year}")

# 主界面：数据核对
st.markdown(f"### 📝 {sc_year} 年度数据自动核对")
c1, c2, c3 = st.columns(3)
with c1:
    f_name = st.text_input("纳税人姓名", value=sc_name)
    f_biz = st.text_input("主要业务/职业类型", value=sc_biz)
with c2:
    f_income = st.number_input("AGI 收入总额", value=float(sc_income))
    f_year = st.text_input("报税年度", value=sc_year)
with c3:
    f_status = st.selectbox("报税身份", ["Single", "Married filing jointly"], 
                             index=0 if "Single" in sc_name or "Single" == "Single" else 0)

# 实时引擎
results = run_audit_engine(f_income, f_status, f_biz)

st.markdown("---")
st.markdown("### 🔍 AI 深度审计发现")
for item in results:
    st.write(item)

# 终极报告
if st.button("📥 生成全能报税审计结案报告 / Final Report"):
    try:
        report_bytes = create_pdf_report(f_name, f_income, f_status, f_biz, f_year, results)
        st.download_button(
            label="💾 下载并保存专业报告",
            data=bytes(report_bytes),
            file_name=f"Tax_Full_Report_{f_year}_{f_name}.pdf",
            mime="application/pdf"
        )
        st.balloons()
    except Exception as e:
        st.error(f"生成失败: {e}")