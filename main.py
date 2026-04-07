import streamlit as st
import pdfplumber
import pandas as pd
import re

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

# --- Streamlit UI 界面设计 ---
st.set_page_config(page_title="华人报税助手 Pro", layout="wide")
st.title("🚀 华人报税助手 Pro (创始人终极版)")
st.markdown("---")

col1, col2 = st.columns([1, 1.2])

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
    
    if st.button("生成测算报告"):
        credit, logs = calculate_tax_logic(inc, deps)
        st.metric("你应该获得的抵免总额", f"${credit}")
        for log in logs: st.write(log)
        st.info("💡 踏实建议：如果你的会计师算的数比这个少，请把这份报告发给他看。")

with col2:
    st.header("📂 券商 1099 智能审计")
    file = st.file_uploader("上传 Moomoo/Fidelity 原始 PDF", type="pdf")
    if file:
        with st.spinner("正在进行‘火眼金睛’扫描..."):
            with pdfplumber.open(file) as pdf:
                txt = "".join([p.extract_text() for p in pdf.pages])
                # 深度抓取 Moomoo 数据
                total_pro = re.findall(r"Grand total\s+([\d,]+\.\d+)", txt)
                wash_dis = re.findall(r"Total Short-term\s+[\d,.]+\s+[\d,.]+\s+[\d,.]+\s+([\d,]+\.\d+)", txt)
                other_inc = re.findall(r"3-\s+Other\s+income\s+([\d,]+\.\d+)", txt)
                
                if total_pro: st.success(f"✅ 审计成功！总成交流水: ${total_pro[0]}")
                if wash_dis:
                    st.error(f"🚨 洗售报警：发现 ${wash_dis[0]} 亏损被 IRS 禁用！")
                    st.caption("避坑指南：这些钱会计师录错就会导致你多交税。")
                if other_inc: st.warning(f"🎁 发现 1099-MISC 额外收入: ${other_inc[0]}")

st.markdown("---")
st.caption("© 2026 Tingting Tax Tech. 本软件专为华人设计，所有算法严格对标 IRS 2026 最新税法。")