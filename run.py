import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# 防止中文乱码
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 读取数据
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'douban_books.xlsx')
df = pd.read_excel(file_path)
print("✅ 数据文件读取成功！")
print("列名：", list(df.columns))

# 2. 数据清洗
df["书籍价格"] = df["书籍价格"].astype(str).str.split().str[0]
df["书籍价格"] = df["书籍价格"].str.replace("元", "").str.replace("CNY", "").str.replace(",", "")
df["书籍价格"] = pd.to_numeric(df["书籍价格"], errors="coerce")

df["评分人数"] = df["评分人数"].astype(str).str.replace("人评价", "").str.replace(",", "")
df["评分人数"] = pd.to_numeric(df["评分人数"], errors="coerce")

df["出版年份"] = df["书籍年份"].astype(str).str.extract(r'(\d{4})').astype(float)

df = df.dropna(subset=["书籍评分", "评分人数", "书籍价格", "出版年份"])
print(f"清洗后剩余 {len(df)} 条数据")

# =============================================
# 图1：评分分布直方图
# =============================================
plt.figure(figsize=(8,5))
sns.histplot(df["书籍评分"], bins=10, color="skyblue", edgecolor="black")
plt.title("图1 豆瓣Top250评分分布", fontsize=14)
plt.xlabel("评分")
plt.ylabel("书籍数量")
plt.tight_layout()
plt.savefig("图1_评分分布.png", dpi=300)
plt.show()
print("✅ 图1已保存")

# =============================================
# 图2：出版社TOP10柱状图
# =============================================
top_publishers = df["书籍出版社"].value_counts().head(10)
plt.figure(figsize=(10,5))
colors = ["#FF6B6B", "#FFA07A", "#FFD700", "#98FB98", "#87CEEB", "#DDA0DD", "#F0E68C", "#E6E6FA", "#FFB6C1", "#B0E0E6"]
bars = plt.bar(range(len(top_publishers)), top_publishers.values, color=colors[:len(top_publishers)])
plt.title("图2 出版社上榜数量TOP10", fontsize=14)
plt.xlabel("出版社")
plt.ylabel("上榜数量")
plt.xticks(range(len(top_publishers)), top_publishers.index, rotation=45, ha="right")
for bar, val in zip(bars, top_publishers.values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, str(val), ha='center', va='bottom')
plt.tight_layout()
plt.savefig("图2_出版社TOP10.png", dpi=300)
plt.show()
print("✅ 图2已保存")

# =============================================
# 图3：年份趋势折线图
# =============================================
year_cnt = df.groupby("出版年份").size()
plt.figure(figsize=(12,5))
plt.plot(year_cnt.index, year_cnt.values, marker="o", color="#2E86AB", linewidth=2, markersize=6)
plt.title("图3 上榜书籍出版年份趋势", fontsize=14)
plt.xlabel("出版年份")
plt.ylabel("上榜数量")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("图3_年份趋势.png", dpi=300)
plt.show()
print("✅ 图3已保存")

# =============================================
# 图4：评分 vs 评分人数散点图
# =============================================
plt.figure(figsize=(8,6))
scatter = plt.scatter(df["书籍评分"], df["评分人数"], alpha=0.5, c=df["出版年份"], cmap="viridis", s=30)
plt.colorbar(scatter, label="出版年份")
plt.title("图4 评分与评分人数关系散点图", fontsize=14)
plt.xlabel("评分")
plt.ylabel("评分人数")
plt.tight_layout()
plt.savefig("图4_评分vs评分人数.png", dpi=300)
plt.show()
print("✅ 图4已保存")

# =============================================
# 图5：价格分布箱线图
# =============================================
plt.figure(figsize=(8,5))
bp = plt.boxplot(df["书籍价格"].dropna(), vert=True, patch_artist=True,
                  boxprops=dict(facecolor="#87CEEB", alpha=0.7),
                  medianprops=dict(color="red", linewidth=2))
plt.title("图5 上榜书籍价格分布箱线图", fontsize=14)
plt.ylabel("价格（元）")
plt.xticks([1], ["全部书籍"])
plt.tight_layout()
plt.savefig("图5_价格分布.png", dpi=300)
plt.show()
print("✅ 图5已保存")

# =============================================
# 图6：作者上榜次数TOP10柱状图
# =============================================
author_count = df["书籍作者"].value_counts().head(10)
plt.figure(figsize=(10,5))
colors2 = plt.cm.Set3(np.linspace(0, 1, len(author_count)))
bars2 = plt.bar(range(len(author_count)), author_count.values, color=colors2)
plt.title("图6 作者上榜次数TOP10", fontsize=14)
plt.xlabel("作者")
plt.ylabel("上榜次数")
plt.xticks(range(len(author_count)), author_count.index, rotation=45, ha="right")
for bar, val in zip(bars2, author_count.values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, str(val), ha='center', va='bottom')
plt.tight_layout()
plt.savefig("图6_作者TOP10.png", dpi=300)
plt.show()
print("✅ 图6已保存")

# =============================================
# 图7：出版社平均评分对比图
# =============================================
pub_stats = df.groupby("书籍出版社")["书籍评分"].agg(["count", "mean"]).sort_values("count", ascending=False).head(10)
pub_stats["mean"] = pub_stats["mean"].round(2)
plt.figure(figsize=(10,5))
bars3 = plt.bar(range(len(pub_stats)), pub_stats["mean"], color="#98D8C8")
plt.title("图7 头部出版社平均评分对比", fontsize=14)
plt.xlabel("出版社")
plt.ylabel("平均评分")
plt.xticks(range(len(pub_stats)), pub_stats.index, rotation=45, ha="right")
plt.ylim(8.5, 9.5)
for bar, val in zip(bars3, pub_stats["mean"]):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, str(val), ha='center', va='bottom')
plt.tight_layout()
plt.savefig("图7_出版社平均评分.png", dpi=300)
plt.show()
print("✅ 图7已保存")

# =============================================
# 表格数据：出版社竞争力指标
# =============================================
print("\n" + "="*60)
print("📊 出版社竞争力指标表")
print("="*60)
pub_table = df.groupby("书籍出版社").agg(
    上榜数量=("书籍评分", "count"),
    平均评分=("书籍评分", "mean"),
    平均评分人数=("评分人数", "mean")
).sort_values("上榜数量", ascending=False).head(10)
pub_table["平均评分"] = pub_table["平均评分"].round(2)
pub_table["平均评分人数"] = pub_table["平均评分人数"].round(0).astype(int)
print(pub_table)
print("="*60)

print("\n🎉 全部图表已生成完毕！请查看桌面 douban 文件夹下的图片文件。")