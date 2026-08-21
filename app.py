"""banksys_kyai5 Streamlit 应用入口:数据分析页(US-5)。"""

import pandas as pd
import streamlit as st

from banksys import APP_NAME, VERSION
from banksys.data import CATEGORICAL_COLS, NUMERIC_COLS, TARGET_COL, load_data, summarize

FILTER_COLS = ["job", "marital", "education", "month"]


@st.cache_data(show_spinner="加载数据...")
def get_train_data() -> pd.DataFrame:
    return load_data("train")


def apply_filters(df: pd.DataFrame, filters: dict[str, str]) -> pd.DataFrame:
    for col, value in filters.items():
        df = df[df[col] == value]
    return df


def main() -> None:
    st.set_page_config(page_title=APP_NAME, layout="wide")
    st.title(APP_NAME)
    st.caption(f"银行营销数据分析 · v{VERSION}")

    df = get_train_data()

    # ---- 1. 数据概览 ----
    st.header("1. 数据概览")
    info = summarize(df)
    subscribe_rate = (df[TARGET_COL] == "yes").mean()
    c1, c2, c3 = st.columns(3)
    c1.metric("客户数", f"{info['rows']:,}")
    c2.metric("特征数", len(df.columns) - 2)  # 去掉 id 与目标列
    c3.metric("认购率", f"{subscribe_rate:.1%}")
    with st.expander("各列类型与缺失情况"):
        dtypes_df = pd.DataFrame(
            {
                "列": list(info["dtypes"]),
                "类型": list(info["dtypes"].values()),
                "缺失数": [int(df[c].isna().sum()) for c in info["dtypes"]],
            }
        )
        st.dataframe(dtypes_df, width="stretch")

    # ---- 2. 目标分布 ----
    st.header("2. 认购目标分布")
    target_counts = df[TARGET_COL].value_counts()
    st.bar_chart(target_counts)
    st.write(f"认购(yes){target_counts.get('yes', 0):,} 人,占比 {subscribe_rate:.1%}")

    # ---- 3. 筛选器 ----
    with st.sidebar:
        st.header("数据筛选")
        filters = {}
        for col in FILTER_COLS:
            choice = st.selectbox(col, ["全部", *sorted(df[col].unique().tolist())])
            if choice != "全部":
                filters[col] = choice
    filtered = apply_filters(df, filters)
    st.caption(f"当前筛选范围:{len(filtered):,} 位客户")

    # ---- 4. 交互式可视化 ----
    st.header("3. 交互式可视化")

    st.subheader("3.1 年龄分布")
    age_bins = pd.cut(filtered["age"], bins=range(17, 102, 5))
    age_dist = age_bins.value_counts().sort_index()
    age_dist.index = age_dist.index.astype(str)  # Interval 索引 altair 不接受
    st.bar_chart(age_dist)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("3.2 类别特征与认购率")
        cat_col = st.selectbox("选择类别特征", CATEGORICAL_COLS, key="cat")
        cat_rate = (
            filtered.groupby(cat_col)[TARGET_COL]
            .apply(lambda s: (s == "yes").mean())
            .sort_values(ascending=False)
        )
        st.bar_chart(cat_rate)

    with col2:
        st.subheader("3.3 数值特征与认购率")
        num_col = st.selectbox("选择数值特征", NUMERIC_COLS, key="num")
        num_bins = pd.cut(filtered[num_col], bins=10)
        num_rate = filtered.groupby(num_bins, observed=True)[TARGET_COL].apply(
            lambda s: (s == "yes").mean()
        )
        num_rate.index = num_rate.index.astype(str)
        st.line_chart(num_rate)

    with st.expander("原始数据预览(前 50 行)"):
        st.dataframe(filtered.head(50), width="stretch")


main()
