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

from core.processor import QueryProcessor
from config.settings import IntentRecognitionConfig
from .models import (
    BaseResponse,
    IntentAnalysisRequest,
    IntentAnalysisResponse,
    HealthResponse,
    ServiceInfo
)

logger = logging.getLogger(__name__)

# 全局查询处理器
query_processor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global query_processor
    
    # 启动时初始化
    logger.info("正在启动意图识别服务...")
    try:
        config = IntentRecognitionConfig()
        
        # 初始化查询处理器
        query_processor = QueryProcessor()
        
        # 如果配置了LLM，尝试设置LLM函数
        if config.llm_enabled:
            try:
                llm_func = await create_llm_func(config)
                query_processor.llm_func = llm_func
                logger.info("LLM功能初始化完成")
            except Exception as e:
                logger.warning(f"LLM功能初始化失败，将使用规则回退: {e}")
        
        logger.info("意图识别服务初始化完成")
        
    except Exception as e:
        logger.error(f"意图识别服务初始化失败: {e}")
        raise
    
    yield
    
    # 关闭时清理
    logger.info("正在关闭意图识别服务...")


async def create_llm_func(config: IntentRecognitionConfig):
    """创建LLM函数（可选）"""
    # 这里可以根据配置创建不同的LLM函数
    # 暂时返回None，使用规则回退
    return None


def create_intent_app(config: IntentRecognitionConfig = None) -> FastAPI:
    """创建意图识别FastAPI应用"""
    
    if config is None:
        config = IntentRecognitionConfig()
    
    app = FastAPI(
        title="意图识别服务",
        description="提供查询意图识别、安全检查和查询增强功能",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health", response_model=BaseResponse[HealthResponse])
    async def health_check():
        """健康检查"""
        return BaseResponse(
            data=HealthResponse(
                status="healthy",
                version="1.0.0",
                timestamp=datetime.now().isoformat(),
                llm_available=query_processor.llm_func is not None if query_processor else False
            )
        )
    
    @app.get("/info", response_model=BaseResponse[ServiceInfo])
    async def service_info():
        """服务信息"""
        return BaseResponse(
            data=ServiceInfo(
                name="意图识别服务",
                version="1.0.0",
                description="提供查询意图识别、安全检查和查询增强功能",
                endpoints=["/analyze", "/health", "/info"],
                features=[
                    "查询意图识别",
                    "内容安全检查", 
                    "查询增强优化",
                    "违规内容拒绝",
                    "安全提示生成",
                    "LLM集成支持",
                    "规则回退机制"
                ]
            )
        )
    
    @app.post("/analyze", response_model=BaseResponse[IntentAnalysisResponse])
    async def analyze_intent(request: IntentAnalysisRequest):
        """分析查询意图"""
        if not query_processor:
            raise HTTPException(status_code=503, detail="服务未初始化")
        
        try:
            # 执行查询分析
            result = await query_processor.process_query(
                query=request.query,
                context=request.context
            )
            
            # 转换为响应格式
            response_data = IntentAnalysisResponse(
                original_query=result.original_query,
                processed_query=result.processed_query,
                intent_type=result.intent_type.value,
                safety_level=result.safety_level.value,
                confidence=result.confidence,
                suggestions=result.suggestions,
                risk_factors=result.risk_factors,
                enhanced_query=result.enhanced_query,
                should_reject=result.should_reject,
                rejection_reason=result.rejection_reason,
                safety_tips=result.safety_tips or [],
                safe_alternatives=result.safe_alternatives or []
            )
            
            # 根据是否拒绝返回不同的消息
            if result.should_reject:
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


if __name__ == "__main__":
    import uvicorn
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建应用
    config = IntentRecognitionConfig()
    app = create_intent_app(config)
    
    # 启动服务
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        log_level=config.log_level.lower()
    )
