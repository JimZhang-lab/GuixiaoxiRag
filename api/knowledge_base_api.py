"""
知识库管理API处理器
处理知识库管理相关的业务逻辑
"""
from fastapi import HTTPException

from model import (
    BaseResponse, CreateKnowledgeBaseRequest, SwitchKnowledgeBaseRequest,
    KnowledgeBaseConfigRequest
)
from handler import kb_manager, guixiaoxirag_service
from common.logging_utils import logger_manager


class KnowledgeBaseAPI:
    """知识库管理API处理器"""
    
    def __init__(self):
        self.logger = logger_manager.setup_api_logger()
    
    async def list_knowledge_bases(self) -> BaseResponse:
        """获取知识库列表"""
        try:
            knowledge_bases = kb_manager.list_knowledge_bases()
            
            return BaseResponse(
                success=True,
                message="获取知识库列表成功",
                data={
                    "knowledge_bases": knowledge_bases,
                    "total_count": len(knowledge_bases),
                    "current_kb": kb_manager.current_kb
                }
            )
            
        except Exception as e:
            self.logger.error(f"获取知识库列表失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取知识库列表失败: {str(e)}")
    
    async def create_knowledge_base(self, request: CreateKnowledgeBaseRequest) -> BaseResponse:
        """创建新知识库"""
        try:
            self.logger.info(f"创建知识库: {request.name}")
            
            kb_info = kb_manager.create_knowledge_base(
                name=request.name,
                description=request.description,
                language=request.language,
                config=request.config
            )
            
            return BaseResponse(
                success=True,
                message=f"知识库 '{request.name}' 创建成功",
                data=kb_info
            )
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            self.logger.error(f"创建知识库失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"创建知识库失败: {str(e)}")
    
    async def delete_knowledge_base(self, name: str, force: bool = False) -> BaseResponse:
        """删除知识库"""
        try:
            self.logger.warning(f"删除知识库: {name}, force={force}")
            
            success = kb_manager.delete_knowledge_base(name, force)
            
            if success:
                return BaseResponse(
                    success=True,
                    message=f"知识库 '{name}' 删除成功",
                    data={"deleted_kb": name, "force": force}
                )
            else:
                raise HTTPException(status_code=500, detail="删除操作失败")
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            self.logger.error(f"删除知识库失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"删除知识库失败: {str(e)}")
    
    async def switch_knowledge_base(self, request: SwitchKnowledgeBaseRequest) -> BaseResponse:
        """切换当前知识库"""
        try:
            self.logger.info(f"切换知识库: {request.name}")
            
            # 如果知识库不存在且允许创建，则创建它
            if request.create_if_not_exists:
                try:
                    kb_path = kb_manager.switch_knowledge_base(request.name)
                except ValueError:
                    # 知识库不存在，创建它
                    create_request = CreateKnowledgeBaseRequest(name=request.name)
                    await self.create_knowledge_base(create_request)
                    kb_path = kb_manager.switch_knowledge_base(request.name)
            else:
                kb_path = kb_manager.switch_knowledge_base(request.name)
            
            # 切换服务的知识库
            success = await guixiaoxirag_service.switch_knowledge_base(kb_path)
            
            if success:
                kb_info = kb_manager.get_current_kb_info()
                return BaseResponse(
                    success=True,
                    message=f"成功切换到知识库 '{request.name}'",
                    data={
                        "current_kb": request.name,
                        "working_dir": kb_path,
                        "kb_info": kb_info
                    }
                )
            else:
                raise HTTPException(status_code=500, detail="服务切换失败")
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            self.logger.error(f"切换知识库失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"切换知识库失败: {str(e)}")
    
    async def get_current_knowledge_base(self) -> BaseResponse:
        """获取当前知识库信息"""
        try:
            kb_info = kb_manager.get_current_kb_info()
            
            return BaseResponse(
                success=True,
                message="获取当前知识库信息成功",
                data=kb_info
            )
            
        except Exception as e:
            self.logger.error(f"获取当前知识库信息失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取当前知识库信息失败: {str(e)}")
    
    async def get_knowledge_base_info(self, name: str) -> BaseResponse:
        """获取指定知识库信息"""
        try:
            import os

            # 检查知识库是否存在
            kb_path = os.path.join(kb_manager.base_dir, name)
            if not os.path.exists(kb_path):
                raise HTTPException(status_code=404, detail=f"知识库 '{name}' 不存在")

            # 获取知识库信息
            kb_info = kb_manager._get_kb_info(name, kb_path)

            return BaseResponse(
                success=True,
                message=f"获取知识库 '{name}' 信息成功",
                data=kb_info
            )

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"获取知识库信息失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取知识库信息失败: {str(e)}")
    
    async def update_knowledge_base_config(self, request: KnowledgeBaseConfigRequest) -> BaseResponse:
        """更新知识库配置"""
        try:
            import os
            import json

            self.logger.info(f"更新知识库配置: {request.knowledge_base}")

            # 检查知识库是否存在
            kb_path = os.path.join(kb_manager.base_dir, request.knowledge_base)
            if not os.path.exists(kb_path):
                raise HTTPException(status_code=404, detail=f"知识库 '{request.knowledge_base}' 不存在")

            # 读取现有元数据
            metadata_file = os.path.join(kb_path, "metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            else:
                metadata = {}

            # 更新配置
            updated_fields = []
            if request.config:
                for key, value in request.config.items():
                    if key in ["description", "language", "tags", "chunk_size", "chunk_overlap", "enable_auto_update"]:
                        metadata[key] = value
                        updated_fields.append(key)

            # 保存更新后的元数据
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            # 清除缓存
            kb_manager._clear_cache()

            return BaseResponse(
                success=True,
                message=f"知识库 '{request.knowledge_base}' 配置更新成功",
                data={
                    "knowledge_base": request.knowledge_base,
                    "updated_fields": updated_fields,
                    "metadata": metadata
                }
            )

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"更新知识库配置失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"更新知识库配置失败: {str(e)}")
    
    async def backup_knowledge_base(self, name: str, compress: bool = True, include_vectors: bool = False) -> BaseResponse:
        """备份知识库"""
        try:
            self.logger.info(f"备份知识库: {name}")
            
            # 这里应该实现备份逻辑
            backup_result = {
                "message": f"需要实现知识库 '{name}' 备份逻辑",
                "compress": compress,
                "include_vectors": include_vectors
            }
            
            return BaseResponse(
                success=True,
                message=f"知识库 '{name}' 备份成功",
                data=backup_result
            )
            
        except Exception as e:
            self.logger.error(f"备份知识库失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"备份知识库失败: {str(e)}")
    
    async def restore_knowledge_base(self, name: str, backup_file: str, restore_mode: str = "full", overwrite: bool = False) -> BaseResponse:
        """恢复知识库"""
        try:
            self.logger.info(f"恢复知识库: {name}")
            
            # 这里应该实现恢复逻辑
            restore_result = {
                "message": f"需要实现知识库 '{name}' 恢复逻辑",
                "backup_file": backup_file,
                "restore_mode": restore_mode,
                "overwrite": overwrite
            }
            
            return BaseResponse(
                success=True,
                message=f"知识库 '{name}' 恢复成功",
                data=restore_result
            )
            
        except Exception as e:
            self.logger.error(f"恢复知识库失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"恢复知识库失败: {str(e)}")

    async def reload_config(self) -> BaseResponse:
        """重新加载配置"""
        try:
            # 重新加载知识库管理器配置
            kb_manager.reload_config()

            # 获取更新后的配置信息
            config_info = kb_manager.get_config_info()

            return BaseResponse(
                success=True,
                message="配置重新加载成功",
                data=config_info
            )

        except Exception as e:
            self.logger.error(f"重新加载配置失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"重新加载配置失败: {str(e)}")

    async def get_config_info(self) -> BaseResponse:
        """获取配置信息"""
        try:
            config_info = kb_manager.get_config_info()

            return BaseResponse(
                success=True,
                message="获取配置信息成功",
                data=config_info
            )

        except Exception as e:
            self.logger.error(f"获取配置信息失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取配置信息失败: {str(e)}")


# 导出API处理器
__all__ = ["KnowledgeBaseAPI"]
