"""banksys_kyai5 Streamlit 应用入口:数据分析页(功能迭代中)。"""

import streamlit as st

from banksys import APP_NAME, VERSION

st.set_page_config(page_title=APP_NAME, layout="wide")

st.title(APP_NAME)
st.caption(f"银行营销数据分析 + 在线认购预测 · v{VERSION}")
st.info("功能开发中:数据分析页与在线预测页将在后续迭代上线。")
