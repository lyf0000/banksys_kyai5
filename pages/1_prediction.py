"""在线认购预测页(US-6):点选表单输入客户特征,预测是否认购。"""

import streamlit as st

from banksys import APP_NAME
from banksys.data import CATEGORICAL_COLS, NUMERIC_COLS, load_data
from banksys.model import load_pipeline, predict
from banksys.preprocess import InputValidationError

# 整数特征用整数步长,小数特征用 0.1 步长
INTEGER_COLS = {"age", "duration", "campaign", "pdays", "previous"}


@st.cache_data(show_spinner="加载选项...")
def category_options() -> dict[str, list[str]]:
    """类别控件选项与训练数据一致(含 unknown)。"""
    df = load_data("train")
    return {col: sorted(df[col].unique().tolist()) for col in CATEGORICAL_COLS}


@st.cache_data(show_spinner="加载默认值...")
def numeric_defaults() -> dict[str, float]:
    """数值控件默认值取训练数据中位数。"""
    df = load_data("train")
    return {col: float(df[col].median()) for col in NUMERIC_COLS}


def main() -> None:
    st.set_page_config(page_title=f"{APP_NAME} · 在线预测", layout="wide")
    st.title("在线认购预测")
    st.caption("填写客户特征,预测其是否会认购定期存款")

    try:
        model, preprocessor = load_pipeline()
    except FileNotFoundError as exc:
        st.error(f"模型未就绪:{exc}")
        st.stop()

    options = category_options()
    defaults = numeric_defaults()
    features: dict = {}

    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        for i, col in enumerate(CATEGORICAL_COLS):
            target = col1 if i % 2 == 0 else col2
            features[col] = target.selectbox(col, options[col], key=f"cat_{col}")
        for i, col in enumerate(NUMERIC_COLS):
            target = col1 if i % 2 == 0 else col2
            step = 1.0 if col in INTEGER_COLS else 0.1
            features[col] = target.number_input(
                col, value=defaults[col], step=step, key=f"num_{col}"
            )
        submitted = st.form_submit_button("预测认购结果")

    if submitted:
        try:
            result = predict(model, preprocessor, features)
        except InputValidationError as exc:
            st.error(f"输入不合法:{exc}")
        else:
            proba = result["probability"]
            if result["subscribe"]:
                st.success(f"预测结果:会认购(yes),置信度 {proba:.1%}")
            else:
                st.warning(f"预测结果:不认购(no),置信度 {proba:.1%}")
            st.progress(min(max(proba, 0.0), 1.0))


main()
