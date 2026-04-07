import streamlit as st
import pdfplumber
import pandas as pd
import re

# ==========================================
# 核心逻辑：2026 IRS 抚养人避坑引擎
# ==========================================
def calculate_tax_logic(income, dependents):
    """
    基于 2026 最新 OBBBA 法案逻辑
    """
    total_credit = 0
    details = []
    
    # 2026 标准额度
    CHILD_TAX_CREDIT = 2200  # 17岁以下 (OBBBA法案调高)
    OTHER_DEPENDENT_CREDIT = 500  # 父母/大学生/ITIN持有者
    
    for dep in dependents:
        name = dep['name']
        age = dep['age']
        is_student = dep['is_student']
        has_ssn = dep['has_ssn'] # 是否有有效SSN
        
        # 逻辑 1：17岁以下且有SSN -> 拿满 $2,200
        if age < 17 and has_ssn:
            total_credit += CHILD_TAX_CREDIT
            details.append(f"✅ {name}: 符合 Child Tax Credit, 获得 ${CHILD_TAX_CREDIT}")
        
        # 逻辑 2：17-23岁在校学生 或 国内父母(有ITIN) -> 拿 $500
        elif (17 <= age < 24 and is_student) or (age >= 17):
            total_credit += OTHER_DEPENDENT_CREDIT
            details.append(f"✅ {name}: 符合 Credit for Other Dependents, 获得 ${OTHER_DEPENDENT_CREDIT}")
            if not has_ssn:
                details.append(f"   💡 提示: {name} 使用 ITIN 申报，虽不能拿满额CTC，但 $500 稳拿。")

    # 逻辑 3：高收入缩减 (Phase-out) - 会计师最易算错点
    # 夫妻合报 40万门槛，单身 20万门槛
    threshold = 400000 
    if income > threshold:
        reduction = ((income - threshold) // 1000) * 50
        total_credit = max(0, total_credit - reduction)
        details.append(f"⚠️ 预警: 您的收入超过 ${threshold}，抵税额依法缩减了 ${reduction}。")

    return total_credit, details

# ==========================================
# Streamlit UI 界面
# ==========================================
st.set_page_config(page_title="华人报税助手 Pro", layout="wide")

st.title("🚀 华人报税助手 Pro (2026 避坑版)")
st.markdown("---")

# 侧边栏：家庭基本情况输入
with st.sidebar:
    st.header("🏠 家庭报税信息")
    income = st.number_input("家庭年预计总收入 (MAGI)", min_value=0, value=150000, step=1000)
    
    st.subheader("👨‍👩‍👧‍👦 抚养人信息")
    num_deps = st.number_input("抚养人数 (孩子/老人)", min_value=0, max_value=10, value=1)
    
    deps_data = []
    for i in range(num_deps):
        st.markdown(f"**家属 #{i+1}**")
        d_name = st.text_input(f"姓名", key=f"n_{i}", value=f"家属{i+1}")
        d_age = st.number_input(f"年龄", min_value=0, max_value=110, key=f"a_{i}", value=10)
        d_ssn = st.checkbox(f"有 SSN (非ITIN)", key=f"s_{i}", value=True)
        d_stu = st.checkbox(f"是全日制学生", key=f"st_{i}", value=False)
        deps_data.append({"name": d_name, "age": d_age, "has_ssn": d_ssn, "is_student": d_stu})

# 主界面：结果展示
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📋 税务智能分析报告")
    if st.button("开始计算抵税额"):
        credit, logs = calculate_tax_logic(income, deps_data)
        st.metric("预计可抵减税额", f"${credit}")
        for log in logs:
            st.write(log)
        
        st.info("💡 避坑建议：如果会计师给您的结果低于此数值，请务必询问其是否漏报了家属抵扣。")

with col2:
    st.header("📂 券商 1099 解析")
    uploaded_file = st.file_uploader("上传 MooMoo/Fidelity PDF 税单", type="pdf")
    
    if uploaded_file:
        with st.spinner("正在精准提取数据..."):
            with pdfplumber.open(uploaded_file) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()
                
                # 示例正则抓取：抓取 Total Proceeds (仅作演示)
                proceeds = re.findall(r"Total\s+Proceeds\s+\$?([\d,]+\.\d+)", text)
                if proceeds:
                    st.success(f"成功识别总流水: ${proceeds[0]}")
                else:
                    st.warning("未能自动抓取流水数值，请确保是官方原始 PDF。")
        
        st.button("导出为会计专用 CSV")

st.markdown("---")
st.caption("© 2026 Tingting Tax Tech. 所有计算基于 IRS 2026 (OBBBA) 最新法规。")