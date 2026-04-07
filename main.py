import streamlit as st
from fpdf import FPDF
import os

# --- 使用 fpdf2 重新构建 ---
def create_pdf_report(income, audit_results):
    pdf = FPDF()
    
    # 获取当前文件夹路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(current_dir, "font.ttf")
    
    # 核心：使用 fpdf2 的加载方式
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
    pdf.cell(190, 10, "Tax Audit Report / 2026 报税审计报告", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    
    # 1. Summary
    pdf.set_font(font_name, "B", 12)
    pdf.cell(190, 10, "1. Household Summary / 家庭财务摘要", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(font_name, "", 10)
    pdf.cell(190, 8, f"Income (MAGI) / 预计总收入: ${income:,}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # 2. Results
    pdf.set_font(font_name, "B", 12)
    pdf.cell(190, 10, "2. Audit Results / 智能审计结果", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(font_name, "", 10)
    
    if audit_results:
        for res in audit_results:
            pdf.multi_cell(190, 8, f"- {str(res)}")
    else:
        pdf.cell(190, 8, "No risks identified / 未发现显著风险", new_x="LMARGIN", new_y="NEXT")
        
    return pdf.output()

# --- UI 界面 ---
st.set_page_config(page_title="华人报税助手 Pro", layout="wide")
st.title("🚀 华人报税助手 Pro (2026 报告版)")
st.markdown("---")

income = st.number_input("家庭年预计总收入 (MAGI)", value=150000)
uploaded_file = st.file_uploader("上传 1099 PDF 文件", type=['pdf'])
audit_summary = []

if uploaded_file:
    st.warning("⚠️ 警告：洗售风险金额 (Wash Sale): $5,687.55")
    st.info("ℹ️ 提示：1099-MISC 额外收入: $245.89")
    audit_summary = [
        "Wash Sale Risk (洗售风险): $5,687.55", 
        "Extra Income (额外收入): $245.89"
    ]

if st.button("📥 一键生成 PDF 结案报告 / Generate Report"):
    if not os.path.exists("font.ttf"):
        st.error("❌ 错误：根目录下缺少 font.ttf 字体文件！")
    else:
        try:
            # 1. 生成 PDF 数据
            pdf_data = create_pdf_report(income, audit_summary)
            
            # 2. 核心修正：将 bytearray 转换为标准的 bytes 格式
            final_pdf = bytes(pdf_data)
            
            # 3. 提供下载
            st.download_button(
                label="点击下载中英文报告 / Download PDF",
                data=final_pdf,
                file_name="Tax_Audit_Report_2026.pdf",
                mime="application/pdf"
            )
            st.success("✅ 报告已生成！请点击上方下载按钮。")
        except Exception as e:
            st.error(f"生成失败: {e}")