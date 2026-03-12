# MyBatis-Plus 踩坑血泪史：我们踩过的那些坑

> 从入门到放弃再到精通，MyBatis-Plus 的坑我都踩过。这篇文章帮你避开它们，少走弯路。

---

## 一、从「真香」到「真坑」

去年项目引入 MyBatis-Plus，团队一片欢呼：「终于不用写 XML 了！」「CRUD 自动生成，太爽了！」

三个月后，生产环境频繁出问题：
- 慢查询导致数据库 CPU 飙升
- 逻辑删除导致数据不一致
- 分页查询内存溢出
- 批量操作性能极差

这才发现，MyBatis-Plus 虽然方便，但坑也不少。今天就来聊聊我们踩过的那些坑。

## 二、坑 1：N+1 查询问题

### 2.1 问题重现

```java
// 用户实体
@TableName("user")
public class User {
    private Long id;
    private String name;
    
    // 一对多关系
    @TableField(exist = false)
    private List<Order> orders;
}

// 查询用户及其订单
List<User> users = userMapper.selectList(null);
for (User user : users) {
    // 每个用户都查一次订单，N+1 问题
    user.setOrders(orderMapper.selectList(
        new QueryWrapper<Order>().eq("user_id", user.getId())
    ));
}
```

**问题**：
- 查询 100 个用户，执行 101 次 SQL（1 次查用户 + 100 次查订单）
- 数据库压力大，性能差

**SQL 日志**：

```sql
SELECT * FROM user;  -- 1 次
SELECT * FROM order WHERE user_id = 1;  -- 100 次
SELECT * FROM order WHERE user_id = 2;
...
SELECT * FROM order WHERE user_id = 100;
```

### 2.2 解决方案

**方案 1：手动 JOIN**

```java
// 自定义 SQL
@Select("SELECT u.*, o.* FROM user u LEFT JOIN `order` o ON u.id = o.user_id")
@Results({
    @Result(property = "id", column = "id"),
    @Result(property = "orders", column = "id",
            many = @Many(select = "com.example.mapper.OrderMapper.selectByUserId"))
})
List<User> selectUsersWithOrders();
```

**方案 2：分两次查询 + 内存组装**

```java
// 1. 查询所有用户
List<User> users = userMapper.selectList(null);
List<Long> userIds = users.stream()
    .map(User::getId)
    .collect(Collectors.toList());

// 2. 一次性查询所有订单
List<Order> orders = orderMapper.selectList(
    new QueryWrapper<Order>().in("user_id", userIds)
);

// 3. 内存组装
Map<Long, List<Order>> orderMap = orders.stream()
    .collect(Collectors.groupBy(Order::getUserId));

users.forEach(user -> 
    user.setOrders(orderMap.getOrDefault(user.getId(), Collections.emptyList()))
);
```

**方案 3：使用 MyBatis-Plus 的关联查询插件**

```xml
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-join</artifactId>
    <version>1.4.6</version>
</dependency>
```

```java
List<User> users = userMapper.selectJoinList(User.class,
    new MPJLambdaWrapper<User>()
        .selectAll(User.class)
        .selectCollection(Order.class, User::getOrders)
        .leftJoin(Order.class, Order::getUserId, User::getId)
);
```

## 三、坑 2：逻辑删除的陷阱

### 3.1 问题重现

```java
@TableName("user")
public class User {
    private Long id;
    private String name;
    
    @TableLogic  // 逻辑删除字段
    private Integer deleted;  // 0=未删除, 1=已删除
}

// 删除用户
userMapper.deleteById(1L);  // UPDATE user SET deleted=1 WHERE id=1

// 查询用户
User user = userMapper.selectById(1L);  // null（被逻辑删除了）

// 但是！唯一索引冲突
User newUser = new User();
newUser.setName("Alice");
newUser.setEmail("alice@example.com");  // 邮箱有唯一索引
userMapper.insert(newUser);  // 报错：Duplicate entry 'alice@example.com'
```

**问题**：
- 逻辑删除的数据仍然占用唯一索引
- 无法插入相同邮箱的新用户

### 3.2 解决方案

**方案 1：唯一索引包含 deleted 字段**

```sql
-- 修改唯一索引
ALTER TABLE user DROP INDEX uk_email;
ALTER TABLE user ADD UNIQUE INDEX uk_email_deleted (email, deleted);
```

但这样会导致：
- 同一个邮箱可以有多条已删除记录
- 索引变大，性能下降

**方案 2：删除时修改唯一字段**

```java
@Override
public boolean removeById(Serializable id) {
    User user = getById(id);
    if (user != null) {
        // 删除时修改邮箱，避免唯一索引冲突
        user.setEmail(user.getEmail() + "_deleted_" + System.currentTimeMillis());
        updateById(user);
    }
    return super.removeById(id);
}
```

**方案 3：不用逻辑删除，用状态字段**

```java
@TableName("user")
public class User {
    private Long id;
    private String name;
    private Integer status;  // 0=正常, 1=禁用, 2=删除
}

// 查询时过滤
List<User> users = userMapper.selectList(
    new QueryWrapper<User>().ne("status", 2)
);
```

### 3.3 逻辑删除的其他坑

**坑 1：关联查询失效**

```java
// 逻辑删除后，JOIN 查询可能查不到数据
@Select("SELECT u.*, o.* FROM user u LEFT JOIN `order` o ON u.id = o.user_id WHERE u.id = #{id}")
User selectUserWithOrders(Long id);  // 如果 user 被逻辑删除，查不到
```

**坑 2：统计不准确**

```java
// COUNT 不包含逻辑删除的数据
Long count = userMapper.selectCount(null);  // 不包含 deleted=1 的数据

// 如果需要包含，要手动指定
Long totalCount = userMapper.selectCount(
    new QueryWrapper<User>().in("deleted", 0, 1)
);
```

**坑 3：批量操作性能差**

```java
// 逻辑删除的批量删除
userMapper.deleteBatchIds(Arrays.asList(1L, 2L, 3L));

// 生成的 SQL
UPDATE user SET deleted=1 WHERE id=1;
UPDATE user SET deleted=1 WHERE id=2;
UPDATE user SET deleted=1 WHERE id=3;

// 而不是
UPDATE user SET deleted=1 WHERE id IN (1, 2, 3);
```

## 四、坑 3：分页查询的性能问题

### 4.1 深分页问题

```java
// 查询第 10000 页，每页 20 条
Page<User> page = new Page<>(10000, 20);
IPage<User> result = userMapper.selectPage(page, null);

// 生成的 SQL
SELECT * FROM user LIMIT 200000, 20;
```

**问题**：
- MySQL 需要扫描 200020 行数据，然后丢弃前 200000 行
- 页数越大，性能越差

**性能测试**：

| 页数 | 耗时 |
|------|------|
| 第 1 页 | 10ms |
| 第 100 页 | 50ms |
| 第 1000 页 | 500ms |
| 第 10000 页 | 5s |

### 4.2 解决方案

**方案 1：使用游标分页**

```java
// 记录上一页的最后一条数据的 ID
Long lastId = 0L;

// 查询下一页
List<User> users = userMapper.selectList(
    new QueryWrapper<User>()
        .gt("id", lastId)
        .orderByAsc("id")
        .last("LIMIT 20")
);

// 更新 lastId
if (!users.isEmpty()) {
    lastId = users.get(users.size() - 1).getId();
}
```

**方案 2：延迟关联**

```java
// 先查 ID
Page<Long> idPage = new Page<>(10000, 20);
IPage<Long> idResult = userMapper.selectPage(idPage,
    new QueryWrapper<User>().select("id")
);

// 再根据 ID 查数据
List<User> users = userMapper.selectBatchIds(idResult.getRecords());
```

**方案 3：使用搜索引擎**

```java
// 对于大数据量的分页，使用 Elasticsearch
SearchRequest request = new SearchRequest("user");
SearchSourceBuilder builder = new SearchSourceBuilder();
builder.from(10000 * 20);
builder.size(20);
request.source(builder);

SearchResponse response = client.search(request, RequestOptions.DEFAULT);
```

### 4.3 COUNT 查询优化

```java
// MyBatis-Plus 的分页会自动执行 COUNT
Page<User> page = new Page<>(1, 20);
IPage<User> result = userMapper.selectPage(page, wrapper);

// 生成两条 SQL
SELECT COUNT(*) FROM user WHERE ...;  // COUNT 查询
SELECT * FROM user WHERE ... LIMIT 0, 20;  // 数据查询
```

**问题**：
- COUNT 查询很慢（特别是大表）
- 每次分页都执行 COUNT

**优化**：

```java
// 方案 1：禁用 COUNT
Page<User> page = new Page<>(1, 20, false);  // 第三个参数：是否查询总数

// 方案 2：缓存 COUNT 结果
@Cacheable(value = "userCount", key = "#wrapper.toString()")
public Long getUserCount(QueryWrapper<User> wrapper) {
    return userMapper.selectCount(wrapper);
}

// 方案 3：使用近似值
// 对于大表，使用 EXPLAIN 获取近似行数
EXPLAIN SELECT * FROM user;  // rows 列是近似值
```


## 五、坑 4：批量操作的性能陷阱

### 5.1 saveBatch 的问题

```java
// 批量插入 10000 条数据
List<User> users = new ArrayList<>();
for (int i = 0; i < 10000; i++) {
    users.add(new User("User" + i, "user" + i + "@example.com"));
}

userService.saveBatch(users);  // 耗时 30 秒
```

**问题**：MyBatis-Plus 的 `saveBatch` 实际上是循环插入

```java
// saveBatch 的源码
for (User user : users) {
    mapper.insert(user);  // 执行 10000 次 INSERT
}
```

### 5.2 解决方案

**方案 1：使用真正的批量插入**

```xml
<!-- UserMapper.xml -->
<insert id="insertBatch">
    INSERT INTO user (name, email) VALUES
    <foreach collection="list" item="item" separator=",">
        (#{item.name}, #{item.email})
    </foreach>
</insert>
```

```java
userMapper.insertBatch(users);  // 耗时 2 秒
```

**方案 2：使用 JDBC 批处理**

```java
@Autowired
private JdbcTemplate jdbcTemplate;

public void batchInsert(List<User> users) {
    String sql = "INSERT INTO user (name, email) VALUES (?, ?)";
    
    jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
        @Override
        public void setValues(PreparedStatement ps, int i) throws SQLException {
            User user = users.get(i);
            ps.setString(1, user.getName());
            ps.setString(2, user.getEmail());
        }
        
        @Override
        public int getBatchSize() {
            return users.size();
        }
    });
}
```

**方案 3：分批插入**

```java
// 每次插入 1000 条
int batchSize = 1000;
for (int i = 0; i < users.size(); i += batchSize) {
    int end = Math.min(i + batchSize, users.size());
    List<User> batch = users.subList(i, end);
    userMapper.insertBatch(batch);
}
```

## 六、坑 5：自动填充的坑

### 6.1 问题重现

```java
@TableName("user")
public class User {
    private Long id;
    private String name;
    
    @TableField(fill = FieldFill.INSERT)
    private Date createTime;
    
    @TableField(fill = FieldFill.UPDATE)
    private Date updateTime;
}

// 自动填充处理器
@Component
public class MyMetaObjectHandler implements MetaObjectHandler {
    @Override
    public void insertFill(MetaObject metaObject) {
        this.strictInsertFill(metaObject, "createTime", Date.class, new Date());
    }
    
    @Override
    public void updateFill(MetaObject metaObject) {
        this.strictUpdateFill(metaObject, "updateTime", Date.class, new Date());
    }
}

// 批量插入时，自动填充不生效
userMapper.insertBatch(users);  // createTime 为 null
```

**原因**：自定义的 `insertBatch` 不会触发 MyBatis-Plus 的拦截器

### 6.2 解决方案

```java
// 手动填充
public void batchInsert(List<User> users) {
    Date now = new Date();
    users.forEach(user -> {
        user.setCreateTime(now);
        user.setUpdateTime(now);
    });
    userMapper.insertBatch(users);
}
```

## 七、坑 6：Wrapper 的性能问题

### 7.1 问题重现

```java
// 复杂查询
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq("status", 1)
    .like("name", "张")
    .between("age", 18, 60)
    .orderByDesc("create_time")
    .last("LIMIT 1000");

List<User> users = userMapper.selectList(wrapper);
```

**问题**：
- `like` 查询无法使用索引
- `orderBy` 可能导致文件排序
- `LIMIT` 太大导致内存占用高

### 7.2 优化建议

```java
// 1. 避免 like 前缀模糊查询
wrapper.like("name", "张%");  // ❌ 无法使用索引
wrapper.likeRight("name", "张");  // ✅ 可以使用索引

// 2. 使用覆盖索引
wrapper.select("id", "name", "age");  // 只查询需要的字段

// 3. 限制返回数量
wrapper.last("LIMIT 100");  // 不要一次查太多

// 4. 使用索引排序
wrapper.orderByDesc("id");  // 主键排序，使用索引
```

## 八、坑 7：乐观锁的坑

### 8.1 问题重现

```java
@TableName("user")
public class User {
    private Long id;
    private String name;
    
    @Version  // 乐观锁字段
    private Integer version;
}

// 并发更新
User user1 = userMapper.selectById(1L);  // version = 1
User user2 = userMapper.selectById(1L);  // version = 1

user1.setName("Alice");
userMapper.updateById(user1);  // 成功，version = 2

user2.setName("Bob");
userMapper.updateById(user2);  // 失败，version 不匹配
```

**问题**：
- 第二次更新失败，但没有异常
- 返回值是 0，容易被忽略

### 8.2 解决方案

```java
// 检查更新结果
int rows = userMapper.updateById(user);
if (rows == 0) {
    throw new OptimisticLockException("数据已被修改，请刷新后重试");
}

// 或者重试
int maxRetry = 3;
for (int i = 0; i < maxRetry; i++) {
    User user = userMapper.selectById(id);
    user.setName("Alice");
    int rows = userMapper.updateById(user);
    if (rows > 0) {
        break;
    }
    if (i == maxRetry - 1) {
        throw new OptimisticLockException("更新失败");
    }
}
```

## 九、最佳实践总结

### 9.1 性能优化

1. **避免 N+1 查询**：使用 JOIN 或分两次查询
2. **深分页优化**：使用游标分页或延迟关联
3. **批量操作**：使用真正的批量 SQL
4. **索引优化**：避免 like 前缀模糊查询
5. **字段筛选**：只查询需要的字段

### 9.2 功能使用

1. **逻辑删除**：慎用，考虑唯一索引冲突
2. **自动填充**：注意批量操作时不生效
3. **乐观锁**：检查更新结果，必要时重试
4. **分页查询**：考虑禁用 COUNT 或缓存结果

### 9.3 代码规范

1. **Wrapper 复用**：避免重复创建
2. **SQL 日志**：开发环境开启，生产环境关闭
3. **异常处理**：捕获并处理 MyBatis-Plus 异常
4. **单元测试**：测试边界情况和并发场景

## 十、总结

MyBatis-Plus 的常见坑：

1. **N+1 查询**：关联查询要小心
2. **逻辑删除**：唯一索引冲突
3. **深分页**：性能急剧下降
4. **批量操作**：不是真正的批量
5. **自动填充**：批量操作不生效
6. **Wrapper**：like 查询无法使用索引
7. **乐观锁**：更新失败无异常

避坑指南：
- 理解 MyBatis-Plus 的实现原理
- 关注生成的 SQL
- 做好性能测试
- 合理使用功能，不要过度依赖

MyBatis-Plus 是个好工具，但不是银弹。用好它需要理解底层原理，避开常见陷阱。

如果这篇文章对你有帮助，欢迎点赞收藏。有问题欢迎评论区讨论。
