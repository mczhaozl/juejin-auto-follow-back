# Python 数据科学完全指南

## 一、NumPy 基础

```python
import numpy as np

# 创建数组
arr = np.array([1, 2, 3, 4, 5])
matrix = np.array([[1, 2], [3, 4]])

# 随机数组
np.random.rand(5)
np.random.randn(5)

# 操作
np.mean(arr)
np.sum(arr)
np.dot(arr, arr)
```

## 二、Pandas 数据处理

```python
import pandas as pd

# DataFrame
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'score': [85, 90, 95]
})

# 筛选
df[df['age'] > 30]

# 聚合
df.groupby('age').mean()

# 读取数据
df = pd.read_csv('data.csv')
df = pd.read_excel('data.xlsx')
```

## 三、Matplotlib 可视化

```python
import matplotlib.pyplot as plt
import seaborn as sns

# 折线图
plt.plot([1, 2, 3], [4, 5, 6])
plt.savefig('plot.png')

# 柱状图
df.plot(kind='bar')

# Seaborn
sns.scatterplot(data=df, x='age', y='score')
```

## 四、数据分析流程

```python
# 1. 数据加载
df = pd.read_csv('data.csv')

# 2. 数据清洗
df = df.dropna()
df = df.fillna(0)

# 3. 探索性分析
df.describe()
df.corr()

# 4. 可视化
sns.histplot(df['score'])
```

## 五、机器学习入门

```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

X = df[['age']]
y = df['score']

X_train, X_test, y_train, y_test = train_test_split(X, y)

model = LinearRegression()
model.fit(X_train, y_train)
model.predict(X_test)
```

## 六、最佳实践

- 使用 Pandas 处理数据
- NumPy 用于数值计算
- Matplotlib/Seaborn 可视化
- Jupyter Notebook 开发
- 注意数据类型和内存优化
