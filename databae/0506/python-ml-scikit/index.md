# Python Scikit-learn 机器学习完全指南

## 一、数据准备

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
import pandas as pd

iris = load_iris()
X = pd.DataFrame(iris.data, columns=iris.feature_names)
y = pd.Series(iris.target)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
```

## 二、数据预处理

```python
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

## 三、分类模型

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

y_pred = model.predict(X_test_scaled)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
```

## 四、回归模型

```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.datasets import load_boston

boston = load_boston()
X, y = boston.data, boston.target

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("MSE:", mean_squared_error(y_test, y_pred))
```

## 五、模型评估

```python
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV

# 交叉验证
scores = cross_val_score(model, X, y, cv=5)
print("Cross-Validation Scores:", scores)

# 网格搜索
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 20]
}
grid = GridSearchCV(model, param_grid, cv=5)
grid.fit(X, y)
print("Best Parameters:", grid.best_params_)
```

## 六、保存和加载模型

```python
import joblib

# 保存
joblib.dump(model, 'model.pkl')

# 加载
model = joblib.load('model.pkl')
```

## 七、最佳实践

- 数据探索和清洗
- 合适的特征工程
- 选择合适的模型
- 交叉验证评估
- 超参数调优
- 模型解释性
- 持续监控和更新
