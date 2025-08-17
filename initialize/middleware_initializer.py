"""
中间件初始化器
负责设置和配置所有中间件
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from middleware import (
    LoggingMiddleware, MetricsMiddleware, SecurityMiddleware
)
from common.config import settings
from common.logging_utils import logger_manager

logger = logger_manager.setup_service_logger()


def setup_middleware(app: FastAPI):
    """设置所有中间件"""
    
    # 1. CORS中间件（最外层）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 在生产环境中应该限制具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 2. 安全中间件
    app.add_middleware(SecurityMiddleware)
    
    # 3. 性能监控中间件
    app.add_middleware(MetricsMiddleware)
    
    # 4. 日志中间件（最内层，最后执行）
    app.add_middleware(LoggingMiddleware)
    
    logger.info("中间件设置完成")


def setup_cors_middleware(app: FastAPI, 
                         allowed_origins: list = None,
                         allow_credentials: bool = True):
    """单独设置CORS中间件"""
    if allowed_origins is None:
        allowed_origins = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )


def setup_security_middleware(app: FastAPI):
    """单独设置安全中间件"""
    app.add_middleware(SecurityMiddleware)


def setup_monitoring_middleware(app: FastAPI):
    """单独设置监控中间件"""
    app.add_middleware(MetricsMiddleware)


def setup_logging_middleware(app: FastAPI):
    """单独设置日志中间件"""
    app.add_middleware(LoggingMiddleware)
