"""
应用初始化器
负责创建FastAPI应用实例和配置
"""
import signal
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI

from common.config import settings
from common.logging_utils import logger_manager
from initialize.service_initializer import initialize_services, cleanup_services
from initialize.middleware_initializer import setup_middleware

# 设置全局日志
logger = logger_manager.setup_service_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("GuiXiaoXiRag服务启动中...")
    
    try:
        # 初始化核心服务
        await initialize_services()
        logger.info("核心服务初始化完成")

        logger.info(f"GuiXiaoXiRag服务启动成功 - 端口: {settings.port}")

        yield
        
    except Exception as e:
        logger.error(f"服务启动失败: {str(e)}", exc_info=True)
        raise
    finally:
        # 关闭时清理
        logger.info("正在关闭GuiXiaoXiRag服务...")
        await cleanup_services()
        logger.info("GuiXiaoXiRag服务已关闭")


def setup_signal_handlers():
    """设置信号处理器"""
    def signal_handler(signum, frame):
        logger.info(f"收到信号 {signum}，准备关闭服务...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""

    # 设置信号处理器
    setup_signal_handlers()

    # 创建FastAPI应用
    app = FastAPI(
        title=settings.app_name,
        description="""
        GuiXiaoXiRag - 智能知识图谱问答系统

        ## 功能特性
        - 🧠 智能知识图谱构建和查询
        - 📚 多格式文档处理和向量化
        - 🔍 多模式智能检索（本地、全局、混合）
        - 🛡️ 查询安全检查和意图分析
        - 📊 知识图谱可视化
        - 🗂️ 多知识库管理
        - 📈 性能监控和指标统计

        ## API分组
        - **文档管理**: 文档上传、插入、批量处理
        - **查询**: 智能查询、意图分析、批量查询
        - **知识图谱**: 图谱查询、可视化、数据导出
        - **知识库管理**: 知识库创建、切换、配置
        - **系统管理**: 状态监控、配置管理、性能指标
        """,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )

    # 在应用创建后立即设置中间件
    setup_middleware(app)

    return app


def setup_lifespan(app: FastAPI):
    """为现有应用设置生命周期（如果需要）"""
    # 这个函数可以用于为已存在的app实例设置生命周期
    # 目前在create_app中已经设置了lifespan，所以这里暂时为空
    pass
