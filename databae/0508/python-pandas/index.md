# Python Pandas 数据处理完全指南

## 一、数据读写

```python
import pandas as pd

# 读取 CSV
df = pd.read_csv('data.csv')

# 读取 Excel
df = pd.read_excel('data.xlsx')

# 保存文件
df.to_csv('output.csv', index=False)
df.to_parquet('output.parquet')
```

## 二、数据探索

```python
# 基本信息
df.head()
df.info()
df.describe()

# 缺失值处理
df.isnull().sum()
df.dropna()
df.fillna(df.mean())

# 重复值
df.duplicated().sum()
df.drop_duplicates()
```

## 三、数据选择

```python
# 列选择
df[['col1', 'col2']]

# 条件筛选
df[df['col1'] > 100]
df[(df['col1'] > 100) & (df['col2'] < 200)]

# 使用 iloc 和 loc
df.iloc[0:5, 0:2]
df.loc[df['col1'] > 100, ['col2', 'col3']]
```

## 四、数据操作

```python
# 添加新列
df['new_col'] = df['col1'] * 2

# 分组聚合
df.groupby('category').agg({'value': ['mean', 'sum', 'count']})

# 透视表
pd.pivot_table(df, values='value', index='category', columns='year', aggfunc='sum')

# 合并数据
df1.merge(df2, on='id')
pd.concat([df1, df2])
```

## 五、数据可视化

```python
import matplotlib.pyplot as plt

# 折线图
df.plot(x='date', y='value', kind='line')

# 柱状图
df['category'].value_counts().plot(kind='bar')

# 散点图
df.plot(x='col1', y='col2', kind='scatter')
```

## 六、最佳实践

- 使用向量化操作代替循环
- 合理处理缺失值
- 类型转换优化内存使用
- 管道式操作链式调用
- 内存占用监控
- 测试数据处理逻辑
