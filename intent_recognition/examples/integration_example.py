"""
微服务集成示例
展示如何将意图识别服务集成到主服务中
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from config.settings import Config
from core.microservice import IntentRecognitionService

logger = logging.getLogger(__name__)


class MainServiceIntegration:
    """主服务集成类"""
    
    def __init__(self, main_app: FastAPI):
        self.main_app = main_app
        self.intent_service: Optional[IntentRecognitionService] = None
        self.config: Optional[Config] = None
    
    async def initialize_intent_service(self, config_path: str = None):
        """初始化意图识别服务"""
        try:
            # 加载配置
            self.config = Config.load_from_yaml(config_path)
            
            # 启用微服务模式
            self.config.integration.microservice["enabled"] = True
            
            # 初始化服务
            self.intent_service = await IntentRecognitionService.get_instance(self.config)
            
            # 注册路由
            self._register_routes()
            
            logger.info("意图识别服务集成完成")
            
        except Exception as e:
            logger.error(f"意图识别服务集成失败: {e}")
            raise
    
    def _register_routes(self):
        """注册路由到主服务"""
        
        @self.main_app.get("/intent/health")
        async def intent_health():
            """意图识别服务健康检查"""
            if not self.intent_service:
                raise HTTPException(status_code=503, detail="意图识别服务未初始化")
            
            return await self.intent_service.health_check()
        
        @self.main_app.get("/intent/info")
        async def intent_info():
            """意图识别服务信息"""
            if not self.intent_service:
                raise HTTPException(status_code=503, detail="意图识别服务未初始化")
            
            return await self.intent_service.get_service_info()
        
        @self.main_app.post("/intent/analyze")
        async def intent_analyze(request: Dict[str, Any]):
            """意图分析"""
            if not self.intent_service:
                raise HTTPException(status_code=503, detail="意图识别服务未初始化")
            
            query = request.get("query")
            if not query:
                raise HTTPException(status_code=400, detail="查询内容不能为空")
            
            context = request.get("context")
            
            try:
                result = await self.intent_service.analyze_query(query, context)
                return {
                    "success": True,
                    "message": "意图分析完成",
                    "data": result
                }
            except Exception as e:
                logger.error(f"意图分析失败: {e}")
                raise HTTPException(status_code=500, detail=f"意图分析失败: {str(e)}")
    
    async def analyze_query_intent(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """分析查询意图（内部调用）"""
        if not self.intent_service:
            raise RuntimeError("意图识别服务未初始化")
        
        return await self.intent_service.analyze_query(query, context)
    
    async def shutdown(self):
        """关闭服务"""
        if self.intent_service:
            await IntentRecognitionService.shutdown_instance()


# 使用示例
async def example_usage():
    """使用示例"""
    
    # 创建主应用
    main_app = FastAPI(title="主服务", version="1.0.0")
    
    # 创建集成实例
    integration = MainServiceIntegration(main_app)
    
    try:
        # 初始化意图识别服务
        await integration.initialize_intent_service()
        
        # 测试意图分析
        result = await integration.analyze_query_intent("什么是人工智能？")
        print("意图分析结果:", result)
        
        # 测试健康检查
        health = await integration.intent_service.health_check()
        print("健康检查结果:", health)
        
    except Exception as e:
        print(f"集成测试失败: {e}")
    finally:
        # 清理资源
        await integration.shutdown()


# 配置化集成示例
class ConfigurableIntegration:
    """可配置的集成方案"""
    
    @staticmethod
    async def create_integrated_app(config_path: str = None) -> FastAPI:
        """创建集成了意图识别的应用"""
        
        # 加载配置
        config = Config.load_from_yaml(config_path)
        
        # 创建主应用
        app = FastAPI(
            title="集成应用",
            description="集成了意图识别功能的主服务",
            version="1.0.0"
        )
        
        # 创建集成实例
        integration = MainServiceIntegration(app)
        
        # 应用启动事件
        @app.on_event("startup")
        async def startup_event():
            await integration.initialize_intent_service(config_path)
        
        # 应用关闭事件
        @app.on_event("shutdown")
        async def shutdown_event():
            await integration.shutdown()
        
        # 添加主服务路由
        @app.get("/")
        async def root():
            return {"message": "集成应用运行中", "services": ["main", "intent_recognition"]}
        
        @app.get("/health")
        async def health():
            """整体健康检查"""
            intent_health = await integration.intent_service.health_check() if integration.intent_service else {"status": "disabled"}
            
            return {
                "main_service": {"status": "healthy"},
                "intent_service": intent_health,
                "overall": "healthy" if intent_health.get("status") == "healthy" else "degraded"
            }
        
        return app


# 独立运行示例
async def run_integrated_service():
    """运行集成服务"""
    import uvicorn
    
    # 创建集成应用
    app = await ConfigurableIntegration.create_integrated_app()
    
    # 启动服务
    config = uvicorn.Config(app, host="0.0.0.0", port=8004, log_level="info")
    server = uvicorn.Server(config)
    
    print("🚀 启动集成服务...")
    print("   • 主服务: http://localhost:8004")
    print("   • 意图分析: http://localhost:8004/intent/analyze")
    print("   • 健康检查: http://localhost:8004/health")
    
    await server.serve()


if __name__ == "__main__":
    # 运行示例
    print("选择运行模式:")
    print("1. 基本集成测试")
    print("2. 启动集成服务")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == "1":
        asyncio.run(example_usage())
    elif choice == "2":
        asyncio.run(run_integrated_service())
    else:
        print("无效选择")
