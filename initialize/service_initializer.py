"""
服务初始化器
负责初始化和清理各种服务
"""
import asyncio
from handler import guixiaoxirag_service, kb_manager
from common.config import settings
from common.logging_utils import logger_manager
from common.utils import ensure_directory

logger = logger_manager.setup_service_logger()


async def initialize_services():
    """初始化所有核心服务"""
    try:
        # 1. 确保必要的目录存在
        ensure_directory(settings.log_dir)
        ensure_directory(settings.upload_dir)
        ensure_directory("./knowledgeBase")
        
        # 2. 初始化知识库管理器
        await initialize_knowledge_base_manager()
        
        # 3. 初始化GuiXiaoXiRag服务
        await initialize_guixiaoxirag_service()
        
        logger.info("所有核心服务初始化完成")
        
    except Exception as e:
        logger.error(f"服务初始化失败: {str(e)}", exc_info=True)
        raise


async def initialize_knowledge_base_manager():
    """初始化知识库管理器"""
    try:
        # 知识库管理器通常不需要异步初始化
        # 但我们可以在这里做一些检查
        kb_manager._ensure_base_dir()
        logger.info("知识库管理器初始化完成")
    except Exception as e:
        logger.error(f"知识库管理器初始化失败: {str(e)}")
        raise


async def initialize_guixiaoxirag_service():
    """初始化GuiXiaoXiRag服务"""
    try:
        # 使用默认配置初始化
        await guixiaoxirag_service.initialize(
            working_dir=settings.working_dir,
            language="中文"
        )
        logger.info("GuiXiaoXiRag服务初始化完成")
    except Exception as e:
        logger.error(f"GuiXiaoXiRag服务初始化失败: {str(e)}")
        raise


async def cleanup_services():
    """清理所有服务"""
    try:
        # 清理GuiXiaoXiRag服务
        await cleanup_guixiaoxirag_service()
        
        # 清理知识库管理器
        await cleanup_knowledge_base_manager()
        
        logger.info("所有服务清理完成")
        
    except Exception as e:
        logger.error(f"服务清理失败: {str(e)}", exc_info=True)


async def cleanup_guixiaoxirag_service():
    """清理GuiXiaoXiRag服务"""
    try:
        await guixiaoxirag_service.finalize()
        logger.info("GuiXiaoXiRag服务清理完成")
    except Exception as e:
        logger.error(f"GuiXiaoXiRag服务清理失败: {str(e)}")


async def cleanup_knowledge_base_manager():
    """清理知识库管理器"""
    try:
        # 知识库管理器通常不需要特殊清理
        # 但可以在这里做一些清理工作
        logger.info("知识库管理器清理完成")
    except Exception as e:
        logger.error(f"知识库管理器清理失败: {str(e)}")


async def health_check_services():
    """检查所有服务的健康状态"""
    health_status = {
        "guixiaoxirag_service": False,
        "knowledge_base_manager": False
    }
    
    try:
        # 检查GuiXiaoXiRag服务
        health_info = await guixiaoxirag_service.health_check()
        health_status["guixiaoxirag_service"] = health_info.get("status") == "healthy"
        
        # 检查知识库管理器
        health_status["knowledge_base_manager"] = True  # 简单检查
        
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
    
    return health_status


async def restart_service(service_name: str):
    """重启指定服务"""
    try:
        if service_name == "guixiaoxirag":
            await cleanup_guixiaoxirag_service()
            await initialize_guixiaoxirag_service()
            logger.info(f"服务 {service_name} 重启完成")
        else:
            logger.warning(f"未知的服务名称: {service_name}")
    except Exception as e:
        logger.error(f"服务 {service_name} 重启失败: {str(e)}")
        raise
