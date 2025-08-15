"""
微服务集成模块
"""
import asyncio
import logging
from typing import Optional, Dict, Any
import aiohttp
from config.settings import Config
from core.processor import QueryProcessor
from core.llm_client import create_llm_function

logger = logging.getLogger(__name__)


class IntentRecognitionMicroservice:
    """意图识别微服务"""
    
    def __init__(self, config: Config):
        self.config = config
        self.processor: Optional[QueryProcessor] = None
        self.is_initialized = False
        
    async def initialize(self):
        """初始化微服务"""
        try:
            logger.info("正在初始化意图识别微服务...")
            
            # 创建LLM函数
            llm_func = None
            if self.config.llm.enabled:
                try:
                    llm_func = await create_llm_function(self.config)
                    if llm_func:
                        logger.info("LLM功能初始化成功")
                    else:
                        logger.warning("LLM功能初始化失败，将使用规则回退")
                except Exception as e:
                    logger.warning(f"LLM功能初始化失败: {e}，将使用规则回退")
            
            # 创建查询处理器
            self.processor = QueryProcessor(config=self.config, llm_func=llm_func)
            
            # 注册到主服务（如果启用）
            if self.config.microservice.registry.get("enabled", False):
                await self._register_with_main_service()
            
            self.is_initialized = True
            logger.info("意图识别微服务初始化完成")
            
        except Exception as e:
            logger.error(f"意图识别微服务初始化失败: {e}")
            raise
    
    async def analyze_query(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """分析查询意图"""
        if not self.is_initialized or not self.processor:
            raise RuntimeError("微服务未初始化")
        
        try:
            result = await self.processor.process_query(query, context)
            
            # 转换为字典格式
            return {
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
        except Exception as e:
            logger.error(f"查询分析失败: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "version": self.config.service.version,
            "llm_available": self.processor.llm_func is not None if self.processor else False,
            "config_loaded": True
        }
    
    async def get_service_info(self) -> Dict[str, Any]:
        """获取服务信息"""
        return {
            "name": self.config.service.name,
            "version": self.config.service.version,
            "description": "提供查询意图识别、安全检查和查询增强功能",
            "endpoints": ["/analyze", "/health", "/info"],
            "features": [
                "查询意图识别",
                "内容安全检查",
                "查询增强优化",
                "违规内容拒绝",
                "安全提示生成",
                "LLM集成支持",
                "规则回退机制"
            ],
            "llm_provider": self.config.llm.provider if self.config.llm.enabled else "disabled",
            "microservice_mode": self.config.is_microservice_mode()
        }
    
    async def _register_with_main_service(self):
        """注册到主服务"""
        main_service_url = self.config.integration.microservice.get("main_service_url")
        if not main_service_url:
            logger.warning("主服务URL未配置，跳过注册")
            return
        
        try:
            service_info = {
                "name": "intent_recognition",
                "url": f"http://{self.config.service.host}:{self.config.service.port}",
                "version": self.config.service.version,
                "endpoints": ["/analyze", "/health", "/info"]
            }
            
            register_url = f"{main_service_url}/microservices/register"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(register_url, json=service_info) as response:
                    if response.status == 200:
                        logger.info("成功注册到主服务")
                    else:
                        logger.warning(f"注册到主服务失败: {response.status}")
        except Exception as e:
            logger.warning(f"注册到主服务失败: {e}")
    
    async def shutdown(self):
        """关闭微服务"""
        logger.info("正在关闭意图识别微服务...")
        
        # 从主服务注销（如果需要）
        if self.config.microservice.registry.get("enabled", False):
            await self._unregister_from_main_service()
        
        self.is_initialized = False
        logger.info("意图识别微服务已关闭")

    async def _register_with_main_service(self):
        """注册到主服务"""
        try:
            registry_config = self.config.microservice.registry
            main_service_url = registry_config.get("main_service_url", "http://localhost:8002")
            register_endpoint = registry_config.get("register_endpoint", "/microservices/register")

            register_data = {
                "service_name": "intent_recognition",
                "service_url": f"http://{self.config.service.host}:{self.config.service.port}",
                "health_check_url": f"http://{self.config.service.host}:{self.config.service.port}/health",
                "version": self.config.service.version
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(f"{main_service_url}{register_endpoint}", json=register_data) as response:
                    if response.status == 200:
                        logger.info("成功注册到主服务")
                    else:
                        logger.warning(f"注册到主服务失败: {response.status}")
        except Exception as e:
            logger.warning(f"注册到主服务失败: {e}")

    async def _unregister_from_main_service(self):
        """从主服务注销"""
        try:
            registry_config = self.config.microservice.registry
            main_service_url = registry_config.get("main_service_url", "http://localhost:8002")
            unregister_endpoint = registry_config.get("unregister_endpoint", "/microservices/unregister")

            unregister_data = {
                "service_name": "intent_recognition",
                "service_url": f"http://{self.config.service.host}:{self.config.service.port}"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(f"{main_service_url}{unregister_endpoint}", json=unregister_data) as response:
                    if response.status == 200:
                        logger.info("成功从主服务注销")
                    else:
                        logger.warning(f"从主服务注销失败: {response.status}")
        except Exception as e:
            logger.warning(f"从主服务注销失败: {e}")


class IntentRecognitionService:
    """意图识别服务单例"""
    
    _instance: Optional[IntentRecognitionMicroservice] = None
    _config: Optional[Config] = None
    
    @classmethod
    async def get_instance(cls, config: Config = None) -> IntentRecognitionMicroservice:
        """获取服务实例"""
        if cls._instance is None:
            if config is None:
                config = Config.load_from_yaml()
            cls._config = config
            cls._instance = IntentRecognitionMicroservice(config)
            await cls._instance.initialize()
        return cls._instance
    
    @classmethod
    async def shutdown_instance(cls):
        """关闭服务实例"""
        if cls._instance:
            await cls._instance.shutdown()
            cls._instance = None
            cls._config = None
    
    @classmethod
    def get_config(cls) -> Optional[Config]:
        """获取配置"""
        return cls._config


# 便捷函数
async def analyze_query(query: str, context: Optional[Dict] = None, config: Config = None) -> Dict[str, Any]:
    """分析查询意图（便捷函数）"""
    service = await IntentRecognitionService.get_instance(config)
    return await service.analyze_query(query, context)


async def health_check(config: Config = None) -> Dict[str, Any]:
    """健康检查（便捷函数）"""
    service = await IntentRecognitionService.get_instance(config)
    return await service.health_check()


async def get_service_info(config: Config = None) -> Dict[str, Any]:
    """获取服务信息（便捷函数）"""
    service = await IntentRecognitionService.get_instance(config)
    return await service.get_service_info()
