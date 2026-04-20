# Python Seaborn 数据可视化完全指南

## 一、基础图表

```python
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme()
tips = sns.load_dataset("tips")

# 散点图
sns.relplot(x="total_bill", y="tip", hue="day", data=tips)
plt.show()

# 直方图
sns.displot(x="total_bill", hue="time", data=tips)
plt.show()
```

## 二、分类数据

```python
# 箱线图
sns.boxplot(x="day", y="total_bill", data=tips)

# 小提琴图
sns.violinplot(x="day", y="total_bill", hue="sex", split=True, data=tips)
```

## 三、关系图

```python
# 配对图
sns.pairplot(tips, hue="sex")

# 热力图
flights = sns.load_dataset("flights")
flights = flights.pivot("month", "year", "passengers")
sns.heatmap(flights, annot=True, fmt="d")
```

## 四、主题和颜色

```python
# 主题
sns.set_theme(style="whitegrid")

# 颜色
sns.color_palette("husl", 8)
sns.pairplot(tips, hue="sex", palette="husl")
```

## 五、最佳实践

- 选择合适的图表类型展示数据
- 使用默认主题提高美观度
- 合理配色
- 标记和注释关键数据
- 保存高分辨率图片
