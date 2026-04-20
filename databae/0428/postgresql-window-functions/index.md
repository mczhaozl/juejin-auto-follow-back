# PostgreSQL 窗口函数完全指南：从 RANK() 到高级分析

## 一、窗口函数概述

窗口函数允许在不分组的情况下计算一组相关行的值，是 SQL 分析能力的核心。

### 1.1 窗口函数 vs 聚合函数

| 特性 | 聚合函数 | 窗口函数 |
|------|---------|--------|
| 返回行数 | 分组后行数 | 与原表相同 |
| 分组 | GROUP BY | OVER() 子句 |
| 用途 | 汇总数据 | 分析、排序、计算 |

### 1.2 语法基础

```sql
SELECT
  column1,
  column2,
  window_function() OVER (
    [PARTITION BY partition_column]
    [ORDER BY sort_column]
    [frame_clause]
  ) AS result
FROM table;
```

---

## 二、排序窗口函数

### 2.1 RANK()、DENSE_RANK()、ROW_NUMBER()

```sql
SELECT
  name,
  department,
  salary,
  ROW_NUMBER() OVER (ORDER BY salary DESC) AS rn,
  RANK() OVER (ORDER BY salary DESC) AS rk,
  DENSE_RANK() OVER (ORDER BY salary DESC) AS drk
FROM employees;

/*
name    | department | salary | rn | rk | drk
--------|------------|--------|----|----|----
Alice   | Sales      | 90000  | 1  | 1  | 1
Bob     | Marketing  | 85000  | 2  | 2  | 2
Charlie | Sales      | 85000  | 3  | 2  | 2
David   | IT         | 80000  | 4  | 4  | 3
*/
```

### 2.2 部门内排名

```sql
SELECT
  name,
  department,
  salary,
  RANK() OVER (
    PARTITION BY department
    ORDER BY salary DESC
  ) AS dept_rank
FROM employees;
```

---

## 三、分布函数

### 3.1 PERCENT_RANK()、CUME_DIST()

```sql
SELECT
  name,
  salary,
  PERCENT_RANK() OVER (ORDER BY salary) AS pct_rank,
  CUME_DIST() OVER (ORDER BY salary) AS cum_dist
FROM employees;

/* PERCENT_RANK = (rank - 1) / (total rows - 1)
   CUME_DIST = (number of rows ≤ current) / total rows
*/
```

### 3.2 NTILE()

```sql
-- 分成 4 组
SELECT
  name,
  salary,
  NTILE(4) OVER (ORDER BY salary DESC) AS quartile
FROM employees;
```

---

## 四、偏移函数

### 4.1 LAG()、LEAD()

```sql
-- 查看前一行和后一行
SELECT
  date,
  revenue,
  LAG(revenue) OVER (ORDER BY date) AS prev_day,
  LEAD(revenue) OVER (ORDER BY date) AS next_day,
  revenue - LAG(revenue) OVER (ORDER BY date) AS diff
FROM daily_revenue;

-- 指定偏移量
SELECT
  date,
  revenue,
  LAG(revenue, 7) OVER (ORDER BY date) AS last_week
FROM daily_revenue;
```

### 4.2 FIRST_VALUE()、LAST_VALUE()

```sql
SELECT
  department,
  name,
  salary,
  FIRST_VALUE(name) OVER (
    PARTITION BY department ORDER BY salary DESC
  ) AS top_dept_earner,
  LAST_VALUE(salary) OVER (
    PARTITION BY department ORDER BY salary
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
  ) AS dept_lowest_salary
FROM employees;
```

---

## 五、聚合窗口函数

### 5.1 SUM()、AVG()、COUNT()

```sql
SELECT
  date,
  revenue,
  SUM(revenue) OVER (ORDER BY date) AS running_total,
  AVG(revenue) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS 7d_ma
FROM daily_revenue;

-- 按部门分区
SELECT
  department,
  name,
  salary,
  AVG(salary) OVER (PARTITION BY department) AS dept_avg,
  salary - AVG(salary) OVER (PARTITION BY department) AS salary_diff
FROM employees;
```

### 5.2 滑动窗口

```sql
SELECT
  date,
  revenue,
  SUM(revenue) OVER (
    ORDER BY date
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
  ) AS last_3_days
FROM daily_revenue;

-- RANGE 窗口（按值）
SELECT
  amount,
  SUM(amount) OVER (
    ORDER BY amount
    RANGE BETWEEN 10 PRECEDING AND 10 FOLLOWING
  ) AS range_sum
FROM transactions;
```

---

## 六、实战场景

### 6.1 计算移动平均线

```sql
-- 7 天移动平均
SELECT
  date,
  revenue,
  AVG(revenue) OVER (
    ORDER BY date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS moving_avg_7d
FROM daily_revenue
ORDER BY date;
```

### 6.2 找出每个部门的前三名

```sql
WITH ranked AS (
  SELECT
    name,
    department,
    salary,
    ROW_NUMBER() OVER (
      PARTITION BY department
      ORDER BY salary DESC
    ) AS rn
  FROM employees
)
SELECT name, department, salary
FROM ranked
WHERE rn <= 3
ORDER BY department, rn;
```

### 6.3 计算同比增长

```sql
SELECT
  EXTRACT(YEAR FROM date) AS year,
  EXTRACT(MONTH FROM date) AS month,
  revenue,
  LAG(revenue) OVER (PARTITION BY EXTRACT(MONTH FROM date) ORDER BY date) AS last_year_same_month,
  ROUND(
    (revenue - LAG(revenue) OVER (PARTITION BY EXTRACT(MONTH FROM date) ORDER BY date))
     / LAG(revenue) OVER (PARTITION BY EXTRACT(MONTH FROM date) ORDER BY date) * 100, 2
  ) AS YoY_pct
FROM monthly_revenue;
```

### 6.4 累计分布与分位数

```sql
-- 计算薪资分位数
SELECT
  name,
  salary,
  NTILE(4) OVER (ORDER BY salary) AS quartile,
  NTILE(10) OVER (ORDER BY salary) AS decile,
  NTILE(100) OVER (ORDER BY salary) AS percentile
FROM employees;
```

---

## 七、窗口函数优化

### 7.1 性能考虑

```sql
-- 避免不必要的排序
SELECT
  name,
  ROW_NUMBER() OVER (ORDER BY id)  -- 用主键排序更快
FROM users;

-- 合适的索引
CREATE INDEX idx_emp_dept_salary ON employees (department, salary DESC);
```

### 7.2 复用窗口

```sql
SELECT
  name,
  department,
  salary,
  ROW_NUMBER() OVER w AS rn,
  RANK() OVER w AS rk,
  FIRST_VALUE(name) OVER w AS top_earner
FROM employees
WINDOW w AS (
  PARTITION BY department
  ORDER BY salary DESC
);
```

---

## 八、最佳实践

1. **理解 PARTITION BY 的作用**：控制窗口范围
2. **注意 ORDER BY 对聚合的影响**
3. **选择合适的窗口帧**（ROWS vs RANGE）
4. **适当建立索引**
5. **复用窗口定义**（WINDOW 子句）

---

## 九、总结

窗口函数是 PostgreSQL 数据分析的利器，掌握它们能写出简洁高效的分析查询。
