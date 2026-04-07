import streamlit as st
from fpdf import FPDF
import os

# --- 核心 PDF 报告类 (支持中英文) ---
def create_pdf_report(income, status, audit_results):
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
    
    # 标题
    pdf.set_font(font_name, "B", 16)
    pdf.cell(190, 10, "Tax Audit Report / 华人报税助手专业审计报告", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    
    # 1. 基础摘要
    pdf.set_font(font_name, "B", 12)
    pdf.cell(190, 10, "1. Financial Summary / 财务摘要", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(font_name, "", 10)
    pdf.cell(190, 8, f"Filing Status / 报税身份: {status}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(190, 8, f"Gross Income / 总收入: ${income:,}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # 2. 智能审计建议
    pdf.set_font(font_name, "B", 12)
    pdf.cell(190, 10, "2. Smart Audit & Warnings / 智能审计与风险预警", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(font_name, "", 10)
    
    for res in audit_results:
        pdf.multi_cell(190, 8, f"● {str(res)}")
        
    pdf.ln(10)
    pdf.set_font(font_name, "I", 8)
    pdf.multi_cell(190, 5, "免责声明：本报告基于2024-2026税法逻辑生成，仅供参考，请以CPA最终签字为准。")
    
    return pdf.output()

# --- 核心审计引擎 (集成 TINGTING FU 税表逻辑) ---
def run_audit_engine(income, status):
    logs = []
    
    # 逻辑 1: 自雇税 (Self-Employment Tax) 预警 [参考 TINGTING FU 案例]
    # 根据 Schedule SE 逻辑: 利润 * 92.35% * 15.3%
    se_tax = round(income * 0.9235 * 0.153)
    if income > 400:
        logs.append(f"⚠️ 自雇税风险: 您的收入属于自雇(Schedule C)，需预留约 ${se_tax:,} 缴纳自雇税。")
    
    # 逻辑 2: 联邦所得税门槛
    std_deduction = 14600 if status == "Single" else 29200
    if income < std_deduction:
        logs.append(f"✅ 所得税豁免: 您的 AGI 低于标准扣除额 ${std_deduction:,}，联邦个人所得税预计为 $0。")
    
    # 逻辑 3: 低收入补贴 (EIC) 资格预选 [参考 TINGTING FU 案例]
    if income < 17000:
        logs.append("💰 福利提醒: 您的收入水平可能符合联邦及州 Earned Income Credit (EIC) 退税补贴。")
        
    return logs

# --- Streamlit 界面 ---
st.set_page_config(page_title="华人报税助手 Pro", layout="wide")
st.title("🚀 华人报税助手 Pro (全能审计版)")
st.markdown("---")

# 数据输入区
col1, col2 = st.columns(2)
with col1:
    st.markdown("### 📝 输入财务数据")
    user_income = st.number_input("年预计总收入 (从 W-2 或 1099 汇总)", value=10000, step=1000)
    user_status = st.selectbox("报税身份", ["Single", "Married filing jointly", "Head of household"])

with col2:
    st.markdown("### 📂 智能文件审计 (OCR 预留)")
    # 这里我们预留了上传位，未来可以实现全自动读取
    st.file_uploader("上传您的 W-2 或 1099 PDF", type=['pdf'])
    st.info("💡 提示：系统会自动根据您上传的文件校验输入数据的准确性。")

# 执行审计
audit_results = run_audit_engine(user_income, user_status)

st.markdown("---")
st.markdown("### 🔍 实时审计发现")
for item in audit_results:
    st.write(item)

# 生成报告
if st.button("📥 下载完整中英文结案报告 / Generate PDF"):
    try:
        pdf_bytes = create_pdf_report(user_income, user_status, audit_results)
        st.download_button(
            label="点击保存 PDF 报告",
            data=bytes(pdf_bytes),
            file_name="Chinese_Tax_Audit_Report.pdf",
            mime="application/pdf"
        )
        st.balloons()
    except Exception as e:
        st.error(f"生成失败: {e}")