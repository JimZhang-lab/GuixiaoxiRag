#!/usr/bin/env python3
"""
简化的意图识别服务启动脚本
"""
import sys
import os
import logging
from pathlib import Path

# 添加路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from api.models import (
        BaseResponse,
        IntentAnalysisRequest,
        IntentAnalysisResponse,
        HealthResponse,
        ServiceInfo
    )
    from core.processor import QueryProcessor
    from config.settings import IntentRecognitionConfig
    from datetime import datetime
    
    logger.info("所有模块导入成功")
    
except ImportError as e:
    logger.error(f"模块导入失败: {e}")
    sys.exit(1)

# 全局查询处理器
query_processor = None

def create_app():
    """创建FastAPI应用"""
    global query_processor
    
    app = FastAPI(
        title="意图识别服务",
        description="提供查询意图识别、安全检查和查询增强功能",
        version="1.0.0"
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 初始化查询处理器
    query_processor = QueryProcessor()
    logger.info("查询处理器初始化完成")
    
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "success": True,
            "message": "服务正常",
            "data": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "llm_available": query_processor.llm_func is not None if query_processor else False
            }
        }
    
    @app.get("/info")
    async def service_info():
        """服务信息"""
        return {
            "success": True,
            "message": "服务信息",
            "data": {
                "name": "意图识别服务",
                "version": "1.0.0",
                "description": "提供查询意图识别、安全检查和查询增强功能",
                "endpoints": ["/analyze", "/health", "/info"],
                "features": [
                    "查询意图识别",
                    "内容安全检查", 
                    "查询增强优化",
                    "违规内容拒绝",
                    "安全提示生成",
                    "规则回退机制"
                ]
            }
        }
    
    @app.post("/analyze")
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
            response_data = {
                "original_query": result.original_query,
                "processed_query": result.processed_query,
                "intent_type": result.intent_type.value,
                "safety_level": result.safety_level.value,
                "confidence": result.confidence,
                "suggestions": result.suggestions,
                "risk_factors": result.risk_factors,
                "enhanced_query": result.enhanced_query,
                "should_reject": result.should_reject,
                "rejection_reason": result.rejection_reason,
                "safety_tips": result.safety_tips or [],
                "safe_alternatives": result.safe_alternatives or []
            }
            
            # 根据是否拒绝返回不同的消息
            if result.should_reject:
                return {
                    "success": True,
                    "message": "查询分析完成，内容被安全检查拒绝",
                    "data": response_data
                }
            else:
                return {
                    "success": True,
                    "message": "查询分析完成",
                    "data": response_data
                }
                
        except Exception as e:
            logger.error(f"查询分析失败: {e}")
            raise HTTPException(status_code=500, detail=f"查询分析失败: {str(e)}")
    
    return app

if __name__ == "__main__":
    print("🚀 意图识别服务启动器")
    print("=" * 50)
    
    try:
        app = create_app()
        print("✅ 应用创建成功")
        print("🌟 服务地址: http://0.0.0.0:8003")
        print("📖 API文档: http://0.0.0.0:8003/docs")
        print("🔍 健康检查: http://0.0.0.0:8003/health")
        print("ℹ️ 服务信息: http://0.0.0.0:8003/info")
        print("\n⚡ 按 Ctrl+C 停止服务")
        print("=" * 50)
        
        # 使用内置服务器启动（仅用于测试）
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
        
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        sys.exit(1)
