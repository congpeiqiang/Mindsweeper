"""
统一的 JSON 响应封装工具

提供标准化的 API 响应结构，确保所有端点返回一致的格式
"""

from typing import Any, Optional, Dict, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """
    通用 API 响应模型
    
    提供标准化的响应结构，包含状态码、消息、数据和时间戳
    """
    code: int = Field(..., description="HTTP 状态码")
    message: str = Field(default="success", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": None,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }

def api_response(message: str, data: dict = None, code=200):
    return ApiResponse(
        code=code,
        message=message,
        data=data,
        timestamp=datetime.now()
    )

class ResponseBuilder:
    """
    API 响应构建器
    
    提供便捷的方法来构建标准化的 API 响应
    """
    
    @staticmethod
    async def success(
        data: Any = None
    ) -> JSONResponse:
        """
        构建成功响应
        
        Args:
            :param data: 响应数据
            
        Returns:
            标准化的成功响应字典
            
        Example:
            >>> ResponseBuilder.success(data={"id": 1}, message="创建成功")
            {
                "code": 200,
                "message": "创建成功",
                "data": {"id": 1},
                "timestamp": "2024-01-01T00:00:00Z"
            }
        """
        if data and not isinstance(data, dict):
            data = data.model_dump()
        return JSONResponse(
            status_code=200,
            content=data
        )

    @staticmethod
    async def fail(  # 定义一个名为fail的函数，虽然函数名与功能不太匹配，实际是构建成功响应
            data: Any = None,  # 参数：响应数据，类型为Any，默认值为None
            code: int = 400  # 参数：HTTP状态码，类型为int，默认值为400
    ) -> JSONResponse:  # 函数返回类型为JSONResponse
        """
        构建成功响应
        
        Args:
            :param data: 响应数据
            :param code: 状态码
        Returns:
            标准化的成功响应字典
            
        Example:
            >>> ResponseBuilder.fail(data={"id": 1}, message="创建失败")
            {
                "code": 400,
                "message": "创建失败",
                "data": {"id": 1},
                "timestamp": "2024-01-01T00:00:00Z"
            }
            """
        if data and not isinstance(data, dict):
            data = data.model_dump()
        return JSONResponse(
            status_code=code,
            content=data)
    
    @staticmethod
    def accepted(
        data: Any = None,
        message: str = "accepted"
    ) -> Dict[str, Any]:
        """
        构建接受响应 (202)
        
        用于异步操作，表示请求已被接受但尚未处理
        
        Args:
            data: 响应数据（通常包含任务ID）
            message: 响应消息
            
        Returns:
            标准化的接受响应字典
        """
        return ResponseBuilder.success(data=data, message=message, code=202)
    
    @staticmethod
    def no_content(message: str = "no content") -> Dict[str, Any]:
        """
        构建无内容响应 (204)
        
        用于删除操作成功
        
        Args:
            message: 响应消息
            
        Returns:
            标准化的无内容响应字典
        """
        return {
            "code": 204,
            "message": message,
            "data": None,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def bad_request(
        message: str = "bad request",
        data: Any = None
    ) -> Dict[str, Any]:
        """
        构建请求错误响应 (400)
        
        Args:
            message: 错误消息
            data: 错误详情
            
        Returns:
            标准化的请求错误响应字典
        """
        return {
            "code": 400,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def unauthorized(
        message: str = "unauthorized",
        data: Any = None
    ) -> Dict[str, Any]:
        """
        构建未授权响应 (401)
        
        Args:
            message: 错误消息
            data: 错误详情
            
        Returns:
            标准化的未授权响应字典
        """
        return {
            "code": 401,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def forbidden(
        message: str = "forbidden",
        data: Any = None
    ) -> Dict[str, Any]:
        """
        构建禁止访问响应 (403)
        
        Args:
            message: 错误消息
            data: 错误详情
            
        Returns:
            标准化的禁止访问响应字典
        """
        return {
            "code": 403,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def not_found(
        message: str = "not found",
        data: Any = None
    ) -> Dict[str, Any]:
        """
        构建资源不存在响应 (404)
        
        Args:
            message: 错误消息
            data: 错误详情
            
        Returns:
            标准化的资源不存在响应字典
        """
        return {
            "code": 404,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def conflict(
        message: str = "conflict",
        data: Any = None
    ) -> Dict[str, Any]:
        """
        构建冲突响应 (409)
        
        用于资源冲突，如重复创建
        
        Args:
            message: 错误消息
            data: 错误详情
            
        Returns:
            标准化的冲突响应字典
        """
        return {
            "code": 409,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def unprocessable_entity(
        message: str = "unprocessable entity",
        data: Any = None
    ) -> Dict[str, Any]:
        """
        构建无法处理的实体响应 (422)
        
        用于数据验证失败
        
        Args:
            message: 错误消息
            data: 验证错误详情
            
        Returns:
            标准化的验证错误响应字典
        """
        return {
            "code": 422,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def internal_error(
        message: str = "internal server error",
        data: Any = None
    ) -> Dict[str, Any]:
        """
        构建服务器错误响应 (500)
        
        Args:
            message: 错误消息
            data: 错误详情
            
        Returns:
            标准化的服务器错误响应字典
        """
        return {
            "code": 500,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def service_unavailable(
        message: str = "service unavailable",
        data: Any = None
    ) -> Dict[str, Any]:
        """
        构建服务不可用响应 (503)
        
        Args:
            message: 错误消息
            data: 错误详情
            
        Returns:
            标准化的服务不可用响应字典
        """
        return {
            "code": 503,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

