"""
文档管理API处理器
处理文档相关的业务逻辑
"""
import time
from typing import List, Optional
from fastapi import HTTPException, UploadFile

from model import (
    BaseResponse, InsertTextRequest, InsertTextsRequest,
    DirectoryInsertRequest, FileUploadRequest, InsertResponse
)
from handler import document_processor, guixiaoxirag_service
from common.logging_utils import logger_manager
from common.utils import generate_track_id


class DocumentAPI:
    """文档管理API处理器"""
    
    def __init__(self):
        self.logger = logger_manager.setup_api_logger()
    
    async def insert_text(self, request: InsertTextRequest) -> BaseResponse:
        """插入单个文本文档"""
        try:
            self.logger.info(f"开始插入文本，长度: {len(request.text)}")
            
            # 验证输入
            if not request.text.strip():
                raise HTTPException(status_code=400, detail="文本内容不能为空")
            
            # 调用服务层
            track_id = await guixiaoxirag_service.insert_text(
                text=request.text,
                doc_id=request.doc_id,
                file_path=request.file_path,
                track_id=request.track_id,
                working_dir=self._get_working_dir(request.working_dir, request.knowledge_base),
                language=request.language
            )
            
            return BaseResponse(
                success=True,
                message="文本插入成功",
                data=InsertResponse(
                    track_id=track_id,
                    message="文本插入成功"
                )
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"插入文本失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"插入文本失败: {str(e)}")
    
    async def insert_texts(self, request: InsertTextsRequest) -> BaseResponse:
        """批量插入文本文档"""
        try:
            self.logger.info(f"开始批量插入文本，数量: {len(request.texts)}")
            
            # 验证输入
            if not request.texts:
                raise HTTPException(status_code=400, detail="文本列表不能为空")
            
            valid_texts = [text for text in request.texts if text.strip()]
            if not valid_texts:
                raise HTTPException(status_code=400, detail="没有有效的文本内容")
            
            # 调用服务层
            track_id = await guixiaoxirag_service.insert_texts(
                texts=valid_texts,
                doc_ids=request.doc_ids,
                file_paths=request.file_paths,
                track_id=request.track_id,
                working_dir=self._get_working_dir(None, request.knowledge_base),
                language=request.language
            )
            
            return BaseResponse(
                success=True,
                message=f"批量插入成功，处理了 {len(valid_texts)} 条文本",
                data=InsertResponse(
                    track_id=track_id,
                    message=f"批量插入成功，处理了 {len(valid_texts)} 条文本",
                    processed_count=len(valid_texts)
                )
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"批量插入文本失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"批量插入文本失败: {str(e)}")
    
    async def insert_file(self, file: UploadFile, request: FileUploadRequest) -> BaseResponse:
        """上传并插入单个文件"""
        try:
            self.logger.info(f"开始处理文件: {file.filename}")

            # 使用文件工具处理上传
            from common.file_utils import process_uploaded_file

            # 处理文件上传
            file_result = await process_uploaded_file(file)

            # 插入文本到知识库
            track_id = await guixiaoxirag_service.insert_text(
                text=file_result["content"],
                file_path=file_result["file_path"],
                track_id=request.track_id,
                working_dir=self._get_working_dir(None, request.knowledge_base),
                language=request.language
            )

            result = {
                "success": True,
                "track_id": track_id,
                "file_info": file_result,
                "knowledge_base": request.knowledge_base,
                "language": request.language
            }

            return BaseResponse(
                success=True,
                message="文件上传并插入成功",
                data=result
            )

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"文件处理失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")
    
    async def insert_files(
        self, 
        files: List[UploadFile], 
        knowledge_base: Optional[str] = None,
        language: Optional[str] = None,
        extract_metadata: bool = True
    ) -> BaseResponse:
        """批量上传并插入文件"""
        try:
            self.logger.info(f"开始批量处理文件，数量: {len(files)}")
            
            if not files:
                raise HTTPException(status_code=400, detail="文件列表不能为空")
            
            # 批量处理文件
            results = []
            for file in files:
                try:
                    request = FileUploadRequest(
                        knowledge_base=knowledge_base,
                        language=language,
                        extract_metadata=extract_metadata
                    )
                    result = await self.insert_file(file, request)
                    results.append(result.data)
                except Exception as e:
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": str(e)
                    })
            
            successful_count = sum(1 for r in results if r.get("success", False))
            
            return BaseResponse(
                success=True,
                message=f"批量文件处理完成，成功: {successful_count}/{len(files)}",
                data={
                    "total_files": len(files),
                    "successful_files": successful_count,
                    "failed_files": len(files) - successful_count,
                    "results": results
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"批量文件处理失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"批量文件处理失败: {str(e)}")
    
    async def insert_directory(self, request: DirectoryInsertRequest) -> BaseResponse:
        """从目录插入文件"""
        try:
            self.logger.info(f"开始处理目录: {request.directory_path}")
            
            # 调用文档处理器
            result = await document_processor.process_directory(
                directory_path=request.directory_path,
                knowledge_base=request.knowledge_base,
                language=request.language,
                recursive=request.recursive,
                file_patterns=request.file_patterns
            )
            
            if result["success"]:
                return BaseResponse(
                    success=True,
                    message=f"目录处理完成，成功: {result['processed_files']}/{result['total_files']}",
                    data=result
                )
            else:
                raise HTTPException(status_code=500, detail=result.get("error", "目录处理失败"))
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"目录处理失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"目录处理失败: {str(e)}")
    
    def _get_working_dir(self, working_dir: Optional[str], knowledge_base: Optional[str]) -> Optional[str]:
        """获取工作目录"""
        if working_dir:
            return working_dir
        if knowledge_base:
            from pathlib import Path
            from common.config import settings
            # 使用配置文件中的knowledgeBase目录
            kb_base_dir = str(Path(settings.working_dir).parent)
            return f"{kb_base_dir}/{knowledge_base}"
        return None


# 导出API处理器
__all__ = ["DocumentAPI"]
