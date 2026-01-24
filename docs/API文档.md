# 知识库管理系统 - API文档

## 基础信息

- **基础URL**: `http://localhost:8000/api/v1`
- **认证**: Bearer Token (JWT)
- **响应格式**: JSON

## 通用响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "错误描述",
  "error": "ERROR_CODE"
}
```

## API端点

### 1. 文件管理

#### 1.1 上传文件
```
POST /files/upload
Content-Type: multipart/form-data

参数:
- file: 文件 (必需)
- knowledge_base_id: 知识库ID (必需)
- description: 文件描述 (可选)

响应:
{
  "code": 200,
  "data": {
    "file_id": "uuid",
    "filename": "document.pdf",
    "file_size": 1024000,
    "status": "processing",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### 1.2 获取文件列表
```
GET /files?knowledge_base_id=uuid&page=1&page_size=10

响应:
{
  "code": 200,
  "data": {
    "total": 100,
    "items": [
      {
        "file_id": "uuid",
        "filename": "document.pdf",
        "file_size": 1024000,
        "status": "completed",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ]
  }
}
```

#### 1.3 获取文件详情
```
GET /files/{file_id}

响应:
{
  "code": 200,
  "data": {
    "file_id": "uuid",
    "filename": "document.pdf",
    "file_size": 1024000,
    "status": "completed",
    "chunks_count": 50,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### 1.4 删除文件
```
DELETE /files/{file_id}

响应:
{
  "code": 200,
  "message": "文件删除成功"
}
```

### 2. 文档管理

#### 2.1 获取文档列表
```
GET /documents?file_id=uuid&page=1&page_size=10

响应:
{
  "code": 200,
  "data": {
    "total": 50,
    "items": [
      {
        "doc_id": "uuid",
        "file_id": "uuid",
        "content": "文档内容...",
        "chunk_index": 1,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ]
  }
}
```

#### 2.2 获取文档详情
```
GET /documents/{doc_id}

响应:
{
  "code": 200,
  "data": {
    "doc_id": "uuid",
    "file_id": "uuid",
    "content": "文档内容...",
    "chunk_index": 1,
    "metadata": {},
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### 3. 搜索

#### 3.1 向量搜索
```
POST /search

请求体:
{
  "query": "搜索关键词",
  "knowledge_base_id": "uuid",
  "top_k": 10,
  "threshold": 0.5
}

响应:
{
  "code": 200,
  "data": {
    "query": "搜索关键词",
    "results": [
      {
        "doc_id": "uuid",
        "file_id": "uuid",
        "filename": "document.pdf",
        "content": "相关内容...",
        "score": 0.95,
        "chunk_index": 1
      }
    ],
    "total": 10
  }
}
```

#### 3.2 混合搜索
```
POST /search/hybrid

请求体:
{
  "query": "搜索关键词",
  "knowledge_base_id": "uuid",
  "top_k": 10,
  "vector_weight": 0.7,
  "keyword_weight": 0.3
}

响应:
{
  "code": 200,
  "data": {
    "results": [...]
  }
}
```

### 4. 知识库管理

#### 4.1 创建知识库
```
POST /knowledge-bases

请求体:
{
  "name": "知识库名称",
  "description": "知识库描述",
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
}

响应:
{
  "code": 200,
  "data": {
    "kb_id": "uuid",
    "name": "知识库名称",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### 4.2 获取知识库列表
```
GET /knowledge-bases?page=1&page_size=10

响应:
{
  "code": 200,
  "data": {
    "total": 5,
    "items": [
      {
        "kb_id": "uuid",
        "name": "知识库名称",
        "description": "知识库描述",
        "files_count": 10,
        "documents_count": 500,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ]
  }
}
```

#### 4.3 获取知识库详情
```
GET /knowledge-bases/{kb_id}

响应:
{
  "code": 200,
  "data": {
    "kb_id": "uuid",
    "name": "知识库名称",
    "description": "知识库描述",
    "files_count": 10,
    "documents_count": 500,
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### 4.4 更新知识库
```
PUT /knowledge-bases/{kb_id}

请求体:
{
  "name": "新名称",
  "description": "新描述"
}

响应:
{
  "code": 200,
  "message": "知识库更新成功"
}
```

#### 4.5 删除知识库
```
DELETE /knowledge-bases/{kb_id}

响应:
{
  "code": 200,
  "message": "知识库删除成功"
}
```

#### 4.6 获取知识库统计
```
GET /knowledge-bases/{kb_id}/stats

响应:
{
  "code": 200,
  "data": {
    "kb_id": "uuid",
    "files_count": 10,
    "documents_count": 500,
    "total_size": 10485760,
    "last_updated": "2024-01-01T00:00:00Z"
  }
}
```

### 5. 健康检查

#### 5.1 系统健康检查
```
GET /health

响应:
{
  "code": 200,
  "data": {
    "status": "healthy",
    "milvus": "connected",
    "postgres": "connected",
    "redis": "connected"
  }
}
```

## 错误码

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 413 | 文件过大 |
| 415 | 不支持的文件类型 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

## 文件类型支持

| 类型 | 扩展名 | 最大大小 |
|------|--------|---------|
| PDF | .pdf | 100MB |
| CSV | .csv | 50MB |
| 图片 | .jpg, .png, .jpeg | 20MB |
| 文本 | .txt | 50MB |

## 分页参数

所有列表接口支持以下分页参数:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认10，最大100）

## 排序参数

支持的排序字段:
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `name`: 名称

排序方式: `asc` (升序) 或 `desc` (降序)

示例: `GET /files?sort_by=created_at&sort_order=desc`

