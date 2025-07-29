# API迁移说明文档

## 当前状态
当前代码已从MongoDB直接存储改为调用本地后端API进行数据存储。

### API配置
API地址通过环境变量 `API_BASE_URL` 配置，默认值为 `http://localhost:8000`。

在 `.env` 文件中设置：
```
API_BASE_URL=http://localhost:8000
```

或在 `env_template.txt` 中查看配置模板。

## API接口说明
根据 [API文档](https://lovetapoversea.xyz:4433/docs#/)，当前使用的接口包括：

1. **创建用户**: `POST /api/v1/UserManagement/create_new_user`
   - 输入: `telegram_user_id`, `telegram_user_name`, `gender`
   - 输出: `user_id`

2. **编辑用户年龄**: `POST /api/v1/UserManagement/edit_user_age`
   - 输入: `user_id`, `age`
   - 输出: `success`

3. **编辑用户目标性别**: `POST /api/v1/UserManagement/edit_target_gender`
   - 输入: `user_id`, `target_gender`
   - 输出: `success`

4. **编辑用户总结**: `POST /api/v1/UserManagement/edit_summary`
   - 输入: `user_id`, `summary`
   - 输出: `success`

## 恢复到MongoDB版本的方法

如果需要恢复到原来的MongoDB直接存储版本，请按以下步骤操作：

### 1. 恢复数据库函数
将注释掉的MongoDB函数取消注释，并注释掉API版本：

```python
# 在 main.py 中找到以下函数，取消注释MongoDB版本，注释掉API版本：

# create_or_update_user
# save_user_gender  
# save_user_age
# save_user_target_gender
# save_user_personality_summary
# save_ai_response
# get_user_from_mongodb
```

### 2. 修改函数调用
将异步调用改回同步调用：

```python
# 在 handle_message 函数中：
# 将 await create_or_update_user(...) 改为 create_or_update_user(...)
# 将 await save_user_gender(...) 改为 save_user_gender(...)
# 将 await save_user_age(...) 改为 save_user_age(...)
# 将 await save_user_target_gender(...) 改为 save_user_target_gender(...)
# 将 await save_user_personality_summary(...) 改为 save_user_personality_summary(...)
```

### 3. 恢复评分存储
取消注释评分存储代码：

```python
# 在评分处理部分取消注释：
users_collection.update_one(
    {'_id': user_id},
    {'$set': {'user_rating': score, 'updated_at': datetime.now(UTC)}}
)
```

### 4. 恢复AI响应存储
取消注释AI响应存储：

```python
# 取消注释：
save_ai_response(user_id, response)
```

### 5. 移除API相关代码
删除或注释掉以下内容：
- API配置：`API_BASE_URL = "http://localhost:8000"`
- API调用函数：`create_new_user_api`, `edit_user_age_api`, `edit_target_gender_api`, `edit_summary_api`
- 用户ID映射：`telegram_to_user_id_map`

### 6. 移除httpx导入
如果不再需要API调用，可以移除：
```python
import httpx  # 新增：用于HTTP请求
```

## 测试API连接
运行测试脚本验证API是否正常工作：
```bash
python test_api_connection.py
```

## 注意事项
1. 确保后端API服务在localhost:8000正常运行
2. API版本和MongoDB版本不能同时使用
3. 切换版本前请备份当前代码
4. 用户ID映射机制仅在API版本中使用，MongoDB版本直接使用telegram_user_id 