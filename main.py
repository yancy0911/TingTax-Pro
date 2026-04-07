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
        
        # A. 抓取姓名并深度去重
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

        # B. 抓取业务类型 (从 Schedule C 识别)
        biz_match = re.search(r"Principal business or profession.*?\n(.*?)\n", text, re.IGNORECASE)
        business_type = biz_match.group(1).strip() if biz_match else "通用劳务"

        # C. 抓取 AGI (调整后总收入)
        agi_match = re.search(r"adjusted gross income.*?(\d+[,.]\d+)", text, re.IGNORECASE)
        agi = float(agi_match.group(1).replace(',', '')) if agi_match else 0.0
        
        # D. 识别报税年份
        year_match = re.search(r"Form 1040 \((\d{4})\)", text)
        tax_year = year_match.group(1) if year_match else "2024"
        
        return full_name, agi, business_type, tax_year
    except Exception as e:
        return "识别失败", 0.0, "未知", "2024"

# --- 2. 全能审计引擎：场景化分析 ---
def run_audit_engine(income, status, biz_type):
    logs = []
    # 自雇税核心预警
    se_tax = round(income * 0.9235 * 0.153)
    if income > 400:
        logs.append(f"⚠️ 自雇税核算: 您在【{biz_type}】领域的收入需缴纳约 ${se_tax:,} 的社保医保税。")
    
    # 联邦所得税门槛
    std_deduction = 14600 if status == "Single" else 29200
    if income < std_deduction:
        logs.append(f"✅ 所得税豁免: 收入低于门槛 ${std_deduction:,}，联邦所得税预计为 $0。")
    
    # 低收入补贴 (EIC) 与 QBI 扣除提醒
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
    pdf.cell(190, 10, f"{year} Tax Comprehensive Report / 综合报税审计报告", new_x="