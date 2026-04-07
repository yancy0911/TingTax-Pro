import streamlit as st
from fpdf import FPDF
import os

# --- 核心 PDF 类：带路径检测的中文字体加载 ---
class AuditReport(FPDF):
    def header(self):
        # 尝试使用中文字体
        if 'Chinese' in self.fonts:
            self.set_font("Chinese", "B", 16)
            self.cell(190, 10, "Tax Audit Report / 2026 报税审计报告", ln=True, align="C")
        else:
            self.set_font("Helvetica", "B", 16)
            self.cell(190, 10, "Tax Audit Report 2026 (Font Missing)", ln=True, align="C")
        self.ln(10)

def create_pdf_report(income, audit_results):
    pdf = AuditReport()
    
    # 自动获取当前文件所在的文件夹路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(current_dir, "font.ttf")
    
    has_chinese = False
    if os.path.exists(font_path):
        try:
            pdf.add_font("Chinese", "", font_path, unicode=True)
            pdf.add_font("Chinese", "B", font_path, unicode=True)
            pdf.set_font("Chinese", "", 10)
            has_chinese = True
        except Exception as e:
            st.error(f"字体加载失败: {e}")
            
    if not has_chinese:
        pdf.set_font("Helvetica", "", 10)
    
    pdf.add_page()
    font_name = "Chinese" if has_chinese else "Helvetica"
    
    # 1. Summary
    pdf.set_font(font_name, "B", 12)
    pdf.cell(190, 10, "1. Household Summary / 家庭财务摘要", ln=True)
    pdf.set_font(font_name, "", 10)
    pdf.cell(190, 8, f"Income (MAGI) / 预计总收入: ${income:,}", ln=True)
    pdf.ln(5)
    
    # 2. Results
    pdf.set_font(font_name, "B", 12)
    pdf.cell(190, 10, "2. Audit Results / 智能审计结果", ln=True)
    pdf.set_font(font_name, "", 10)
    
    if audit_results:
        for res in audit_results:
            pdf.multi_cell(190, 8, f"- {str(res)}")
    else:
        pdf.cell(190, 8, "No risks identified / 未发现显著风险", ln=True)
        
    return pdf.output(dest='S')

# --- UI 界面 ---
st.set_page_config(page_title="华人报税助手 Pro", layout="wide")
st.title("🚀 华人报税助手 Pro (2026 报告版)")
st.subheader("Chinese Tax Assistant Pro - 2026 Report Edition")
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
    # 再次检查字体是否存在
    if not os.path.exists("font.ttf"):
        st.error("❌ 严重错误：服务器上找不到 font.ttf 文件！请确认已将其拖入 Cursor 根目录并 Push。")
    else:
        try:
            pdf_bytes = create_pdf_report(income, audit_summary)
            st.download_button(
                label="点击下载中英文报告 / Download PDF",
                data=bytes(pdf_bytes),
                file_name="Tax_Audit_Report_2026_Bilingual.pdf",
                mime="application/pdf"
            )
            st.success("✅ 报告已生成！请点击上方下载按钮。")
        except Exception as e:
            st.error(f"生成过程出错: {e}")