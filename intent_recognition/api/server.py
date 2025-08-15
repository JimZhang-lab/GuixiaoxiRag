"""
意图识别独立服务器
"""
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import sys
from pathlib import Path

# 添加父目录到路径
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from core.microservice import IntentRecognitionService
from config.settings import Config
from .models import (
    BaseResponse,
    IntentAnalysisRequest,
    IntentAnalysisResponse,
    HealthResponse,
    ServiceInfo
)

logger = logging.getLogger(__name__)

# 全局服务实例
service_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global service_instance

    # 启动时初始化
    logger.info("正在启动意图识别服务...")
    try:
        # 获取配置
        config = getattr(app.state, 'config', None) or Config.load_from_yaml()

        # 初始化微服务
        service_instance = await IntentRecognitionService.get_instance(config)

        logger.info("意图识别服务初始化完成")

    except Exception as e:
        logger.error(f"意图识别服务初始化失败: {e}")
        raise

    yield

    # 关闭时清理
    logger.info("正在关闭意图识别服务...")
    if service_instance:
        await IntentRecognitionService.shutdown_instance()


def create_intent_app(config: Config = None) -> FastAPI:
    """创建意图识别FastAPI应用"""

    if config is None:
        config = Config.load_from_yaml()

    # API文档配置
    docs_config = config.api.docs
    app = FastAPI(
        title=docs_config.get("title", "意图识别服务 API"),
        description=docs_config.get("description", "提供查询意图识别、安全检查和查询增强功能"),
        version=docs_config.get("version", config.service.version),
        lifespan=lifespan
    )

    # 保存配置到应用状态
    app.state.config = config

    # 添加CORS中间件
    cors_config = config.api.cors
    if cors_config.get("enabled", True):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_config.get("origins", ["*"]),
            allow_credentials=True,
            allow_methods=cors_config.get("methods", ["*"]),
            allow_headers=cors_config.get("headers", ["*"]),
        )

    @app.get("/health", response_model=BaseResponse[HealthResponse])
    async def health_check():
        """健康检查"""
        if not service_instance:
            raise HTTPException(status_code=503, detail="服务未初始化")

        health_data = await service_instance.health_check()
        return BaseResponse(
            data=HealthResponse(
                status=health_data["status"],
                version=health_data["version"],
                timestamp=datetime.now().isoformat(),
                llm_available=health_data["llm_available"]
            )
        )

    @app.get("/info", response_model=BaseResponse[ServiceInfo])
    async def service_info():
        """服务信息"""
        if not service_instance:
            raise HTTPException(status_code=503, detail="服务未初始化")

        info_data = await service_instance.get_service_info()
        return BaseResponse(
            data=ServiceInfo(
                name=info_data["name"],
                version=info_data["version"],
                description=info_data["description"],
                endpoints=info_data["endpoints"],
                features=info_data["features"]
            )
        )

    @app.post("/analyze", response_model=BaseResponse[IntentAnalysisResponse])
    async def analyze_intent(request: IntentAnalysisRequest):
        """分析查询意图"""
        if not service_instance:
            raise HTTPException(status_code=503, detail="服务未初始化")

        try:
            # 执行查询分析
            result_data = await service_instance.analyze_query(
                query=request.query,
                context=request.context
            )

            # 转换为响应格式
            response_data = IntentAnalysisResponse(
                original_query=result_data["original_query"],
                processed_query=result_data["processed_query"],
                intent_type=result_data["intent_type"],
                safety_level=result_data["safety_level"],
                confidence=result_data["confidence"],
                suggestions=result_data["suggestions"],
                risk_factors=result_data["risk_factors"],
                enhanced_query=result_data["enhanced_query"],
                should_reject=result_data["should_reject"],
                rejection_reason=result_data["rejection_reason"],
                safety_tips=result_data["safety_tips"],
                safe_alternatives=result_data["safe_alternatives"]
            )

            # 根据是否拒绝返回不同的消息
            if result_data["should_reject"]:
                return BaseResponse(
                    success=True,
                    message="查询分析完成，内容被安全检查拒绝",
                    data=response_data
                )
            else:
                return BaseResponse(
                    success=True,
                    message="查询分析完成",
                    data=response_data
                )

        except Exception as e:
            logger.error(f"查询分析失败: {e}")
            raise HTTPException(status_code=500, detail=f"查询分析失败: {str(e)}")

    return app


def create_app(config: Config = None) -> FastAPI:
    """创建FastAPI应用（别名）"""
    if config is None:
        config = Config.load_from_yaml()
    return create_intent_app(config)


if __name__ == "__main__":
    import uvicorn

    # 加载配置
    config = Config.load_from_yaml()

    # 配置日志
    logging.basicConfig(
        level=getattr(logging, config.logging.level.upper()),
        format=config.logging.format
    )

    # 创建应用
    app = create_intent_app(config)

    # 启动服务
    uvicorn.run(
        app,
        host=config.service.host,
        port=config.service.port,
        log_level=config.logging.level.lower(),
        workers=config.service.workers if not config.service.debug else 1,
        reload=config.service.reload
    )
