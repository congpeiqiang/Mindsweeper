# 自定义异常

import logging
from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


logger = logging.getLogger(__name__)


# ==================== 自定义异常类 ====================

class AppException(Exception):
    """
    应用基础异常类

    所有自定义异常的基类
    """

    def __init__(
        self,
        code: int = 500,
        message: str = "服务器内部错误",
        detail: Optional[str] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        """
        初始化异常

        Args:
            code: 错误代码
            message: 错误消息
            detail: 错误详情
            status_code: HTTP状态码
        """
        self.code = code
        self.message = message
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "code": self.code,
            "message": self.message,
            "detail": self.detail,
        }


class ValidationException(AppException):
    """数据验证异常"""

    def __init__(self, message: str = "数据验证失败", detail: Optional[str] = None):
        super().__init__(
            code=422,
            message=message,
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class NotFoundException(AppException):
    """资源未找到异常"""

    def __init__(self, message: str = "资源未找到", detail: Optional[str] = None):
        super().__init__(
            code=404,
            message=message,
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UnauthorizedException(AppException):
    """未授权异常"""

    def __init__(self, message: str = "未授权", detail: Optional[str] = None):
        super().__init__(
            code=401,
            message=message,
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenException(AppException):
    """禁止访问异常"""

    def __init__(self, message: str = "禁止访问", detail: Optional[str] = None):
        super().__init__(
            code=403,
            message=message,
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ConflictException(AppException):
    """冲突异常"""

    def __init__(self, message: str = "资源冲突", detail: Optional[str] = None):
        super().__init__(
            code=409,
            message=message,
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
        )


class FileException(AppException):
    """文件处理异常"""

    def __init__(self, message: str = "文件处理失败", detail: Optional[str] = None):
        super().__init__(
            code=400,
            message=message,
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class DatabaseException(AppException):
    """数据库异常"""

    def __init__(self, message: str = "数据库操作失败", detail: Optional[str] = None):
        super().__init__(
            code=500,
            message=message,
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class ServiceException(AppException):
    """服务异常"""

    def __init__(self, message: str = "服务异常", detail: Optional[str] = None):
        super().__init__(
            code=500,
            message=message,
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ==================== 异常处理器 ====================

class ExceptionHandlers:
    """
    异常处理器集合

    提供统一的异常处理接口
    """

    @staticmethod
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
        处理请求验证错误

        Args:
            request: 请求对象
            exc: 异常对象

        Returns:
            JSON响应
        """
        logger.warning(f"请求验证失败: {request.url}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": 422,
                "message": "请求验证失败",
                "errors": exc.errors(),
            },
        )

    @staticmethod
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        """
        处理应用异常

        Args:
            request: 请求对象
            exc: 异常对象

        Returns:
            JSON响应
        """
        logger.warning(f"应用异常: {exc.message} - {request.url}")
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
        )

    @staticmethod
    async def general_exception_handler(
        request: Request, exc: Exception, debug: bool = False
    ) -> JSONResponse:
        """
        处理通用异常

        Args:
            request: 请求对象
            exc: 异常对象
            debug: 是否为调试模式

        Returns:
            JSON响应
        """
        logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 500,
                "message": "服务器内部错误",
                "detail": str(exc) if debug else "Internal Server Error",
            },
        )
