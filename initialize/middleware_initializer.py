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
    
    # 2. 安全中间件（从配置注入限流参数）
    app.add_middleware(
        SecurityMiddleware,
        max_request_size=settings.max_request_size,
        rate_limit_requests=settings.rate_limit_requests,
        rate_limit_window=settings.rate_limit_window,
        enable_proxy_headers=settings.enable_proxy_headers,
        trusted_proxy_ips=settings.trusted_proxy_ips,
        user_id_header=settings.user_id_header,
        client_id_header=settings.client_id_header,
        api_key_header=settings.api_key_header,
        authorization_header=settings.authorization_header,
        user_tier_header=settings.user_tier_header,
        rate_limit_tiers=settings.rate_limit_tiers,
        rate_limit_default_tier=settings.rate_limit_default_tier,
        min_interval_per_user=settings.min_interval_per_user,
    )

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
