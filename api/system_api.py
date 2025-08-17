"""
系统管理API处理器
处理系统管理相关的业务逻辑
"""
import time
from fastapi import HTTPException

from model import (
    BaseResponse, ConfigUpdateRequest, SystemResetRequest,
    HealthResponse, SystemStatus
)
from handler import guixiaoxirag_service
from common.config import settings
from common.logging_utils import logger_manager


class SystemAPI:
    """系统管理API处理器"""
    
    def __init__(self):
        self.logger = logger_manager.setup_api_logger()
        self.start_time = time.time()
    
    async def health_check(self) -> HealthResponse:
        """系统健康检查"""
        try:
            # 获取系统健康状态
            health_info = await guixiaoxirag_service.health_check()
            
            system_status = SystemStatus(
                service_name="GuiXiaoXiRag",
                version="2.0.0",
                status=health_info["status"],
                initialized=health_info["initialized"],
                working_dir=health_info.get("current_working_dir", ""),
                uptime=time.time() - self.start_time
            )
            
            return HealthResponse(
                status=health_info["status"],
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                system=system_status
            )
            
        except Exception as e:
            self.logger.error(f"健康检查失败: {str(e)}")
            # 返回降级的健康状态
            system_status = SystemStatus(
                service_name="GuiXiaoXiRag",
                version="2.0.0",
                status="unhealthy",
                initialized=False,
                working_dir="",
                uptime=time.time() - self.start_time
            )
            
            return HealthResponse(
                status="unhealthy",
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                system=system_status
            )
    
    async def get_system_status(self) -> BaseResponse:
        """获取系统详细状态"""
        try:
            health_info = await guixiaoxirag_service.health_check()
            performance_stats = guixiaoxirag_service.get_performance_stats()
            
            status_data = {
                **health_info,
                "performance_stats": performance_stats,
                "uptime": time.time() - self.start_time
            }
            
            return BaseResponse(
                success=True,
                message="获取系统状态成功",
                data=status_data
            )
            
        except Exception as e:
            self.logger.error(f"获取系统状态失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取系统状态失败: {str(e)}")
    
    async def get_metrics(self) -> BaseResponse:
        """获取系统性能指标"""
        try:
            # 这里应该从中间件获取指标
            from middleware import get_metrics
            
            metrics = get_metrics()
            performance_stats = guixiaoxirag_service.get_performance_stats()
            
            combined_metrics = {
                **metrics,
                "service_stats": performance_stats
            }
            
            return BaseResponse(
                success=True,
                message="获取性能指标成功",
                data=combined_metrics
            )
            
        except Exception as e:
            self.logger.error(f"获取性能指标失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取性能指标失败: {str(e)}")
    
    async def get_logs(self, lines: int = 100) -> BaseResponse:
        """获取系统日志"""
        try:
            import os

            # 限制行数范围
            lines = max(1, min(lines, 1000))

            log_file_path = os.path.join(settings.log_dir, "guixiaoxirag_service.log")
            logs = []

            if os.path.exists(log_file_path):
                try:
                    with open(log_file_path, 'r', encoding='utf-8') as f:
                        all_lines = f.readlines()
                        # 获取最后N行
                        logs = all_lines[-lines:] if len(all_lines) > lines else all_lines
                        # 清理换行符
                        logs = [line.rstrip('\n\r') for line in logs]
                except Exception as e:
                    self.logger.error(f"读取日志文件失败: {e}")
                    logs = [f"读取日志文件失败: {str(e)}"]
            else:
                logs = ["日志文件不存在"]

            logs_data = {
                "logs": logs,
                "total_lines": len(logs),
                "requested_lines": lines,
                "log_file": log_file_path,
                "file_exists": os.path.exists(log_file_path)
            }

            return BaseResponse(
                success=True,
                message="获取日志成功",
                data=logs_data
            )

        except Exception as e:
            self.logger.error(f"获取日志失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取日志失败: {str(e)}")
    
    async def reset_system(self, request: SystemResetRequest) -> BaseResponse:
        """系统重置"""
        try:
            if not request.confirm:
                raise HTTPException(status_code=400, detail="必须确认重置操作")

            self.logger.warning("开始系统重置操作")

            import os
            import shutil
            import time
            from handler import guixiaoxirag_service, kb_manager

            reset_result = {
                "backup_created": False,
                "config_reset": False,
                "cleared_data": [],
                "errors": []
            }

            # 1. 备份数据（如果需要）
            if request.backup_data:
                try:
                    backup_dir = f"./backup_{int(time.time())}"
                    if os.path.exists("./knowledgeBase"):
                        shutil.copytree("./knowledgeBase", f"{backup_dir}/knowledgeBase")
                        reset_result["backup_created"] = True
                        reset_result["backup_path"] = backup_dir
                        self.logger.info(f"数据备份完成: {backup_dir}")
                except Exception as e:
                    reset_result["errors"].append(f"备份失败: {str(e)}")

            # 2. 清理知识库数据
            try:
                if os.path.exists("./knowledgeBase"):
                    shutil.rmtree("./knowledgeBase")
                    reset_result["cleared_data"].append("knowledgeBase")
                    self.logger.info("知识库数据已清理")
            except Exception as e:
                reset_result["errors"].append(f"清理知识库失败: {str(e)}")

            # 3. 清理上传文件
            try:
                if os.path.exists(settings.upload_dir):
                    shutil.rmtree(settings.upload_dir)
                    reset_result["cleared_data"].append("upload_files")
                    self.logger.info("上传文件已清理")
            except Exception as e:
                reset_result["errors"].append(f"清理上传文件失败: {str(e)}")

            # 4. 重置服务状态
            try:
                await guixiaoxirag_service.finalize()
                guixiaoxirag_service.reset_performance_stats()
                reset_result["cleared_data"].append("service_state")
                self.logger.info("服务状态已重置")
            except Exception as e:
                reset_result["errors"].append(f"重置服务状态失败: {str(e)}")

            # 5. 重新初始化默认知识库
            try:
                kb_manager._ensure_base_dir()
                reset_result["cleared_data"].append("default_kb_recreated")
                self.logger.info("默认知识库已重新创建")
            except Exception as e:
                reset_result["errors"].append(f"重新创建默认知识库失败: {str(e)}")

            success = len(reset_result["errors"]) == 0
            message = "系统重置成功" if success else f"系统重置完成，但有 {len(reset_result['errors'])} 个错误"

            return BaseResponse(
                success=success,
                message=message,
                data=reset_result
            )

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"系统重置失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"系统重置失败: {str(e)}")
    
    async def get_service_config(self) -> BaseResponse:
        """获取当前服务配置"""
        try:
            config = guixiaoxirag_service.get_current_config()
            
            return BaseResponse(
                success=True,
                message="获取服务配置成功",
                data=config
            )
            
        except Exception as e:
            self.logger.error(f"获取服务配置失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取服务配置失败: {str(e)}")
    
    async def get_effective_config(self) -> BaseResponse:
        """获取有效配置信息"""
        try:
            config_data = {
                "app_name": settings.app_name,
                "version": settings.version,
                "host": settings.host,
                "port": settings.port,
                "llm": {
                    "api_base": settings.openai_api_base,
                    "model": settings.openai_chat_model,
                    "embedding_model": settings.openai_embedding_model
                },
                "max_file_size_mb": settings.max_file_size / (1024 * 1024),
                "log_level": settings.log_level
            }
            
            return BaseResponse(
                success=True,
                message="获取有效配置成功",
                data=config_data
            )
            
        except Exception as e:
            self.logger.error(f"获取有效配置失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取有效配置失败: {str(e)}")
    
    async def update_service_config(self, request: ConfigUpdateRequest) -> BaseResponse:
        """更新服务配置"""
        try:
            updated_fields = []
            
            # 更新配置字段
            if request.openai_api_base is not None:
                settings.openai_api_base = request.openai_api_base
                updated_fields.append("openai_api_base")
            
            if request.openai_embedding_api_base is not None:
                settings.openai_embedding_api_base = request.openai_embedding_api_base
                updated_fields.append("openai_embedding_api_base")
            
            if request.openai_chat_api_key is not None:
                settings.openai_chat_api_key = request.openai_chat_api_key
                updated_fields.append("openai_chat_api_key")
            
            if request.openai_embedding_api_key is not None:
                settings.openai_embedding_api_key = request.openai_embedding_api_key
                updated_fields.append("openai_embedding_api_key")
            
            if request.openai_chat_model is not None:
                settings.openai_chat_model = request.openai_chat_model
                updated_fields.append("openai_chat_model")
            
            if request.openai_embedding_model is not None:
                settings.openai_embedding_model = request.openai_embedding_model
                updated_fields.append("openai_embedding_model")
            
            if request.embedding_dim is not None:
                settings.embedding_dim = request.embedding_dim
                updated_fields.append("embedding_dim")
            
            if request.max_token_size is not None:
                settings.max_token_size = request.max_token_size
                updated_fields.append("max_token_size")
            
            if request.log_level is not None:
                settings.log_level = request.log_level
                updated_fields.append("log_level")
            
            # 获取更新后的有效配置
            effective_config_response = await self.get_effective_config()
            
            return BaseResponse(
                success=True,
                message=f"配置更新成功，更新了 {len(updated_fields)} 个字段",
                data={
                    "updated_fields": updated_fields,
                    "effective_config": effective_config_response.data,
                    "restart_required": False,
                    "validation_errors": []
                }
            )
            
        except Exception as e:
            self.logger.error(f"更新配置失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


# 导出API处理器
__all__ = ["SystemAPI"]
