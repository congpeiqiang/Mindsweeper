# API 响应结构统一封装指南

## 📋 概述

本指南介绍如何使用 `ResponseBuilder` 工具类来统一封装所有 API 响应，确保整个系统的响应格式一致。

---

## 🏗️ 响应结构

所有 API 响应都遵循以下统一结构：

```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | int | HTTP 状态码 (200, 201, 400, 404, 500 等) |
| `message` | string | 响应消息 (success, error message 等) |
| `data` | any | 响应数据 (可选，根据端点返回) |
| `timestamp` | string | 响应时间戳 (ISO 8601 格式) |

---

## 🔧 ResponseBuilder 使用方法

### 1. 成功响应 (200)

```python
from app.schema.response import ResponseBuilder

# 基础成功响应
return ResponseBuilder.success(
    data={"id": 1, "name": "example"},
    message="操作成功"
)

# 响应示例
{
    "code": 200,
    "message": "操作成功",
    "data": {"id": 1, "name": "example"},
    "timestamp": "2024-01-01T00:00:00Z"
}
```

### 2. 创建成功响应 (201)

```python
# 用于 POST 请求创建资源
return ResponseBuilder.created(
    data={"id": 1, "name": "new resource"},
    message="资源创建成功"
)

# 响应示例
{
  "code": 201,
  "message": "资源创建成功",
  "data": {"id": 1, "name": "new resource"},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 3. 接受响应 (202)

```python
# 用于异步操作，表示请求已被接受但尚未处理
return ResponseBuilder.accepted(
    data={"task_id": "abc123"},
    message="任务已接受，正在处理"
)

# 响应示例
{
  "code": 202,
  "message": "任务已接受，正在处理",
  "data": {"task_id": "abc123"},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 4. 无内容响应 (204)

```python
# 用于删除操作成功
return ResponseBuilder.no_content(message="资源删除成功")

# 响应示例
{
  "code": 204,
  "message": "资源删除成功",
  "data": null,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 5. 请求错误响应 (400)

```python
# 用于请求参数错误
return ResponseBuilder.bad_request(
    message="请求参数错误",
    data={"field": "email", "error": "格式不正确"}
)

# 响应示例
{
  "code": 400,
  "message": "请求参数错误",
  "data": {"field": "email", "error": "格式不正确"},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 6. 未授权响应 (401)

```python
# 用于认证失败
return ResponseBuilder.unauthorized(message="请提供有效的认证凭证")

# 响应示例
{
  "code": 401,
  "message": "请提供有效的认证凭证",
  "data": null,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 7. 禁止访问响应 (403)

```python
# 用于权限不足
return ResponseBuilder.forbidden(message="您没有权限访问此资源")

# 响应示例
{
  "code": 403,
  "message": "您没有权限访问此资源",
  "data": null,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 8. 资源不存在响应 (404)

```python
# 用于资源不存在
return ResponseBuilder.not_found(message="请求的资源不存在")

# 响应示例
{
  "code": 404,
  "message": "请求的资源不存在",
  "data": null,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 9. 冲突响应 (409)

```python
# 用于资源冲突，如重复创建
return ResponseBuilder.conflict(
    message="资源已存在",
    data={"existing_id": "123"}
)

# 响应示例
{
  "code": 409,
  "message": "资源已存在",
  "data": {"existing_id": "123"},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 10. 无法处理的实体响应 (422)

```python
# 用于数据验证失败
return ResponseBuilder.unprocessable_entity(
    message="数据验证失败",
    data={"errors": [{"field": "age", "message": "必须是正整数"}]}
)

# 响应示例
{
  "code": 422,
  "message": "数据验证失败",
  "data": {"errors": [{"field": "age", "message": "必须是正整数"}]},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 11. 服务器错误响应 (500)

```python
# 用于服务器内部错误
return ResponseBuilder.internal_error(
    message="服务器内部错误",
    data={"error_id": "err_123"}
)

# 响应示例
{
  "code": 500,
  "message": "服务器内部错误",
  "data": {"error_id": "err_123"},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 12. 服务不可用响应 (503)

```python
# 用于服务不可用
return ResponseBuilder.service_unavailable(message="服务暂时不可用，请稍后重试")

# 响应示例
{
  "code": 503,
  "message": "服务暂时不可用，请稍后重试",
  "data": null,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## 📝 实际应用示例

### 文件上传端点

```python
from app.schema.response import ResponseBuilder
from app.models.schemas import FileUploadResponse


@router.post("/upload", response_model=ApiResponse)
async def upload_file(file: UploadFile = File(...)):
    try:
        # 验证文件
        if not is_valid_file(file):
            return ResponseBuilder.bad_request(message="文件格式不支持")

        # 保存文件
        file_record = save_file(file)

        # 构建响应
        upload_response = FileUploadResponse(
            file_id=file_record.id,
            filename=file_record.filename,
            file_size=file_record.file_size,
            file_type=file_record.file_type,
            status=file_record.status,
            created_at=file_record.created_at
        )

        return ResponseBuilder.created(
            data=upload_response.dict(),
            message="文件上传成功"
        )

    except Exception as e:
        return ResponseBuilder.internal_error(
            message=f"文件上传失败: {str(e)}"
        )
```

### 获取资源端点

```python
@router.get("/{resource_id}")
async def get_resource(resource_id: int):
    try:
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        
        if not resource:
            return ResponseBuilder.not_found(message="资源不存在")
        
        return ResponseBuilder.success(
            data=resource.to_dict(),
            message="success"
        )
    
    except Exception as e:
        return ResponseBuilder.internal_error(
            message=f"获取资源失败: {str(e)}"
        )
```

### 删除资源端点

```python
@router.delete("/{resource_id}")
async def delete_resource(resource_id: int):
    try:
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        
        if not resource:
            return ResponseBuilder.not_found(message="资源不存在")
        
        db.delete(resource)
        db.commit()
        
        return ResponseBuilder.no_content(message="资源删除成功")
    
    except Exception as e:
        return ResponseBuilder.internal_error(
            message=f"删除资源失败: {str(e)}"
        )
```

---

## 🎯 最佳实践

### 1. 始终使用 ResponseBuilder

```python
# ✅ 推荐
return ResponseBuilder.success(data=result)

# ❌ 不推荐
return {"code": 200, "message": "success", "data": result}
```

### 2. 选择正确的状态码

```python
# ✅ 创建资源使用 201
return ResponseBuilder.created(data=new_resource)

# ❌ 不要用 200
return ResponseBuilder.success(data=new_resource)
```

### 3. 提供有意义的错误消息

```python
# ✅ 清晰的错误信息
return ResponseBuilder.bad_request(
    message="邮箱格式不正确",
    data={"field": "email"}
)

# ❌ 模糊的错误信息
return ResponseBuilder.bad_request(message="参数错误")
```

### 4. 包含错误详情

```python
# ✅ 包含详细的错误信息
return ResponseBuilder.unprocessable_entity(
    message="数据验证失败",
    data={
        "errors": [
            {"field": "age", "message": "必须是正整数"},
            {"field": "email", "message": "格式不正确"}
        ]
    }
)

# ❌ 只返回错误消息
return ResponseBuilder.unprocessable_entity(message="验证失败")
```

---

## 📊 HTTP 状态码对应表

| 状态码 | 方法 | 用途 |
|--------|------|------|
| 200 | `success()` | 成功的 GET、PUT、PATCH 请求 |
| 201 | `created()` | 成功的 POST 请求（创建资源） |
| 202 | `accepted()` | 异步操作已接受 |
| 204 | `no_content()` | 成功的 DELETE 请求 |
| 400 | `bad_request()` | 请求参数错误 |
| 401 | `unauthorized()` | 认证失败 |
| 403 | `forbidden()` | 权限不足 |
| 404 | `not_found()` | 资源不存在 |
| 409 | `conflict()` | 资源冲突 |
| 422 | `unprocessable_entity()` | 数据验证失败 |
| 500 | `internal_error()` | 服务器内部错误 |
| 503 | `service_unavailable()` | 服务不可用 |

---

## 🔄 迁移指南

### 从旧格式迁移到新格式

**旧格式**:
```python
return {
    "code": 200,
    "message": "success",
    "data": result
}
```

**新格式**:
```python
return ResponseBuilder.success(data=result)
```

### 批量迁移步骤

1. 导入 ResponseBuilder
2. 替换所有手动构建的响应字典
3. 使用正确的状态码方法
4. 测试所有端点

---

## 📚 相关文件

- `app/models/response.py` - ResponseBuilder 实现和 ApiResponse 模型定义
- `app/models/schemas.py` - Pydantic 数据模型定义
- `app/api/v1/files.py` - 使用示例


