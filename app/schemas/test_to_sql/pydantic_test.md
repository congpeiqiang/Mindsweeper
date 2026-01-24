# 1. Pydantic

- Config
  - from_attributes = True # 设置使得数据库查询结果可以直接转换为 Pydantic 模型

```python

class DBConnectionInDBBase(DBConnectionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True # 设置使得数据库查询结果可以直接转换为 Pydantic 模型
```

