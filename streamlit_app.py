import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# 设置中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 页面配置
st.set_page_config(page_title="豆瓣Top250数据看板", layout="wide")
st.title("📚 豆瓣Top250背后的出版力量：头部出版社竞争力分析")
st.markdown("---")

# 加载数据
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'douban_books.xlsx')
    df = pd.read_excel(file_path)
    
    # 清洗
    df["书籍价格"] = df["书籍价格"].astype(str).str.split().str[0]
    df["书籍价格"] = df["书籍价格"].str.replace("元", "").str.replace("CNY", "").str.replace(",", "")
    df["书籍价格"] = pd.to_numeric(df["书籍价格"], errors="coerce")
    
    df["评分人数"] = df["评分人数"].astype(str).str.replace("人评价", "").str.replace(",", "")
    df["评分人数"] = pd.to_numeric(df["评分人数"], errors="coerce")
    
    df["出版年份"] = df["书籍年份"].astype(str).str.extract(r'(\d{4})').astype(float)
    
    df = df.dropna(subset=["书籍评分", "评分人数", "书籍价格", "出版年份"])
    return df

df = load_data()

# ========== 侧边栏筛选器 ==========
st.sidebar.header("🔍 数据筛选")

# 出版社筛选
all_publishers = sorted(df["书籍出版社"].unique().tolist())
selected_publishers = st.sidebar.multiselect(
    "选择出版社",
    options=all_publishers,
    default=all_publishers[:5]
)

# 评分范围筛选
min_score, max_score = float(df["书籍评分"].min()), float(df["书籍评分"].max())
score_range = st.sidebar.slider(
    "评分范围",
    min_value=min_score,
    max_value=max_score,
    value=(8.5, 9.5),
    step=0.1
)

# 年份范围筛选
min_year, max_year = int(df["出版年份"].min()), int(df["出版年份"].max())
year_range = st.sidebar.slider(
    "出版年份范围",
    min_value=min_year,
    max_value=max_year,
    value=(1980, 2020)
)

# 价格范围筛选
min_price, max_price = float(df["书籍价格"].min()), float(df["书籍价格"].max())
price_range = st.sidebar.slider(
    "价格范围（元）",
    min_value=0.0,
    max_value=float(max_price),
    value=(0.0, 100.0)
)

# 应用筛选
filtered_df = df[
    (df["书籍出版社"].isin(selected_publishers)) &
    (df["书籍评分"].between(score_range[0], score_range[1])) &
    (df["出版年份"].between(year_range[0], year_range[1])) &
    (df["书籍价格"].between(price_range[0], price_range[1]))
]

st.sidebar.markdown(f"**当前筛选结果：{len(filtered_df)} 本书**")

# ========== 主面板 ==========

# 第一行：概览指标
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📊 总书籍数", len(filtered_df))
with col2:
    st.metric("⭐ 平均评分", round(filtered_df["书籍评分"].mean(), 2) if len(filtered_df) > 0 else "-")
with col3:
    st.metric("🏢 涉及出版社", filtered_df["书籍出版社"].nunique())
with col4:
    st.metric("💰 平均价格", f"{round(filtered_df['书籍价格'].mean(), 1)} 元" if len(filtered_df) > 0 else "-")

st.markdown("---")

# 第二行：两个图表并排
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("📈 评分分布")
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    sns.histplot(filtered_df["书籍评分"], bins=10, color="skyblue", edgecolor="black", ax=ax1)
    ax1.set_xlabel("评分")
    ax1.set_ylabel("书籍数量")
    ax1.set_title("豆瓣Top250评分分布")
    st.pyplot(fig1)

with right_col:
    st.subheader("🏆 出版社TOP10")
    top_pubs = filtered_df["书籍出版社"].value_counts().head(10)
    if len(top_pubs) > 0:
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        colors = ["#FF6B6B", "#FFA07A", "#FFD700", "#98FB98", "#87CEEB", "#DDA0DD", "#F0E68C", "#E6E6FA", "#FFB6C1", "#B0E0E6"]
        bars = ax2.barh(range(len(top_pubs)), top_pubs.values[::-1], color=colors[:len(top_pubs)][::-1])
        ax2.set_yticks(range(len(top_pubs)))
        ax2.set_yticklabels(top_pubs.index[::-1])
        ax2.set_xlabel("上榜数量")
        ax2.set_title("出版社上榜数量TOP10")
        for bar, val in zip(bars, top_pubs.values[::-1]):
            ax2.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2, str(val), va='center')
        st.pyplot(fig2)

st.markdown("---")

# 第三行：年份趋势 + 价格分布
left_col2, right_col2 = st.columns(2)

with left_col2:
    st.subheader("📅 出版年份趋势")
    year_cnt = filtered_df.groupby("出版年份").size()
    if len(year_cnt) > 0:
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        ax3.plot(year_cnt.index, year_cnt.values, marker="o", color="#2E86AB", linewidth=2, markersize=5)
        ax3.set_xlabel("出版年份")
        ax3.set_ylabel("上榜数量")
        ax3.set_title("上榜书籍出版年份趋势")
        ax3.grid(True, alpha=0.3)
        st.pyplot(fig3)

with right_col2:
    st.subheader("💰 价格分布")
    if len(filtered_df) > 0:
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        bp = ax4.boxplot(filtered_df["书籍价格"].dropna(), vert=True, patch_artist=True,
                         boxprops=dict(facecolor="#87CEEB", alpha=0.7),
                         medianprops=dict(color="red", linewidth=2))
        ax4.set_ylabel("价格（元）")
        ax4.set_title("上榜书籍价格分布箱线图")
        ax4.set_xticklabels(["全部书籍"])
        st.pyplot(fig4)

st.markdown("---")

# 第四行：数据表格
st.subheader("📋 详细数据表")
st.dataframe(
    filtered_df[["书籍名称", "书籍作者", "书籍出版社", "出版年份", "书籍价格", "书籍评分", "评分人数"]]
    .sort_values("书籍评分", ascending=False)
    .reset_index(drop=True),
    use_container_width=True,
    height=400
)

st.markdown("---")
st.caption("数据来源：豆瓣读书Top250榜单 | 分析工具：Python + Streamlit")