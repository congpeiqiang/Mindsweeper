# FastAPI应用入口

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError

from app.api.v1.api import api_router
from app.config.settings import get_settings
from app.utils.logger import setup_logging
from app.utils.exceptions import ExceptionHandlers, AppException

# ==================== 获取配置 ====================

settings = get_settings()
logger = setup_logging(settings)

# ==================== 应用生命周期事件 ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    处理应用启动和关闭事件
    """
    # 启动事件
    logger.info("=" * 60)
    logger.info(f"🚀 {app.title} v{app.version} 启动中...")
    logger.info("=" * 60)

    try:
        # 其他启动逻辑
        logger.info("✅ 应用启动完成")
        logger.info(f"📍 访问地址: http://{settings.HOST}:{settings.PORT}")
        logger.info(f"📚 API文档: http://{settings.HOST}:{settings.PORT}/docs")
        logger.info(f"📚 API文档: http://{settings.HOST}:{settings.PORT}/redoc")
        logger.info(f"📚 API文档: http://{settings.HOST}:{settings.PORT}/openapi")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ 应用启动失败: {str(e)}")
    yield
    # 关闭事件
    logger.info("=" * 60)
    logger.info("🛑 应用关闭中...")
    logger.info("=" * 60)

    try:
        # 清理资源
        logger.info("✅ 应用关闭完成")
    except Exception as e:
        logger.error(f"❌ 应用关闭失败: {str(e)}")



# ==================== 创建FastAPI应用 ====================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Mindsweeper - 知识库管理系统",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ==================== 中间件配置 ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 异常处理 ====================
# 注册异常处理器
app.add_exception_handler(
    RequestValidationError,
    ExceptionHandlers.validation_exception_handler,
)

app.add_exception_handler(
    AppException,
    ExceptionHandlers.app_exception_handler,
)

app.add_exception_handler(
    Exception,
    lambda request, exc: ExceptionHandlers.general_exception_handler(
        request, exc, debug=settings.DEBUG
    ),
)

# ==================== API路由注册 ====================

# 注册v1 API路由
api_v1_prefix = "/api/v1"
app.include_router(api_router, prefix=api_v1_prefix)

logger.info(f"✅ 已注册API路由: {api_v1_prefix}")


# ==================== 应用启动 ====================

if __name__ == "__main__":
    import uvicorn

    logger.info(f"启动服务器: {settings.HOST}:{settings.PORT}")
    logger.info(f"调试模式: {settings.DEBUG}")
    logger.info(f"自动重载: {settings.RELOAD}")

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        timeout_keep_alive = 120
    )
