"""
文档处理器
处理文档上传、解析、分块等功能
"""
import os
import time
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path

from common.config import settings
from common.logging_utils import logger_manager
from common.file_utils import (
    extract_text_from_file,
    process_uploaded_file,
    get_file_contents,
    validate_file_type,
    get_file_info
)
from common.utils import generate_track_id, chunk_list
from .guixiaoxirag_service import guixiaoxirag_service


class DocumentProcessor:
    """文档处理器"""
    
    def __init__(self):
        self.logger = logger_manager.setup_service_logger()
        self.processing_stats = {
            "total_processed": 0,
            "total_failed": 0,
            "avg_processing_time": 0.0,
            "last_activity": None
        }
    
    async def process_single_file(
        self,
        file_path: str,
        knowledge_base: Optional[str] = None,
        language: Optional[str] = None,
        track_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """处理单个文件"""
        start_time = time.time()
        
        if track_id is None:
            track_id = generate_track_id("file_process")
        
        try:
            # 验证文件
            if not os.path.exists(file_path):
                raise ValueError(f"文件不存在: {file_path}")
            
            file_info = get_file_info(file_path)
            if not file_info["is_supported"]:
                raise ValueError(f"不支持的文件类型: {file_info['file_extension']}")
            
            self.logger.info(f"开始处理文件: {file_path}")
            
            # 提取文本内容
            text_content = extract_text_from_file(file_path)
            
            if not text_content.strip():
                raise ValueError("文件内容为空")
            
            # 插入到知识库
            result_track_id = await guixiaoxirag_service.insert_text(
                text=text_content,
                file_path=file_path,
                track_id=track_id,
                working_dir=self._get_kb_working_dir(knowledge_base),
                language=language
            )
            
            processing_time = time.time() - start_time
            self._update_stats(processing_time, success=True)
            
            result = {
                "success": True,
                "track_id": result_track_id,
                "file_path": file_path,
                "file_info": file_info,
                "content_length": len(text_content),
                "processing_time": processing_time,
                "knowledge_base": knowledge_base,
                "language": language
            }
            
            self.logger.info(f"文件处理成功: {file_path}, 耗时: {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_stats(processing_time, success=False)
            
            error_result = {
                "success": False,
                "track_id": track_id,
                "file_path": file_path,
                "error": str(e),
                "processing_time": processing_time
            }
            
            self.logger.error(f"文件处理失败: {file_path}, 错误: {str(e)}")
            return error_result
    
    async def process_directory(
        self,
        directory_path: str,
        knowledge_base: Optional[str] = None,
        language: Optional[str] = None,
        recursive: bool = True,
        file_patterns: Optional[List[str]] = None,
        batch_size: int = 5
    ) -> Dict[str, Any]:
        """处理目录中的所有文件"""
        start_time = time.time()
        track_id = generate_track_id("dir_process")
        
        try:
            if not os.path.exists(directory_path):
                raise ValueError(f"目录不存在: {directory_path}")
            
            if not os.path.isdir(directory_path):
                raise ValueError(f"路径不是目录: {directory_path}")
            
            self.logger.info(f"开始处理目录: {directory_path}")
            
            # 获取所有支持的文件
            files = self._get_supported_files(directory_path, recursive, file_patterns)
            
            if not files:
                return {
                    "success": True,
                    "track_id": track_id,
                    "directory_path": directory_path,
                    "total_files": 0,
                    "processed_files": 0,
                    "failed_files": 0,
                    "results": [],
                    "processing_time": time.time() - start_time
                }
            
            # 分批处理文件
            results = []
            processed_count = 0
            failed_count = 0
            
            file_batches = chunk_list(files, batch_size)
            
            for batch in file_batches:
                batch_tasks = []
                for file_path in batch:
                    task = self.process_single_file(
                        file_path=file_path,
                        knowledge_base=knowledge_base,
                        language=language
                    )
                    batch_tasks.append(task)
                
                # 并行处理当前批次
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, Exception):
                        failed_count += 1
                        results.append({
                            "success": False,
                            "error": str(result),
                            "processing_time": 0
                        })
                    else:
                        if result["success"]:
                            processed_count += 1
                        else:
                            failed_count += 1
                        results.append(result)
            
            processing_time = time.time() - start_time
            
            summary = {
                "success": True,
                "track_id": track_id,
                "directory_path": directory_path,
                "total_files": len(files),
                "processed_files": processed_count,
                "failed_files": failed_count,
                "results": results,
                "processing_time": processing_time,
                "knowledge_base": knowledge_base,
                "language": language
            }
            
            self.logger.info(
                f"目录处理完成: {directory_path}, "
                f"总文件: {len(files)}, 成功: {processed_count}, 失败: {failed_count}, "
                f"耗时: {processing_time:.2f}s"
            )
            
            return summary
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_result = {
                "success": False,
                "track_id": track_id,
                "directory_path": directory_path,
                "error": str(e),
                "processing_time": processing_time
            }
            
            self.logger.error(f"目录处理失败: {directory_path}, 错误: {str(e)}")
            return error_result
    
    async def process_batch_texts(
        self,
        texts: List[str],
        doc_ids: Optional[List[str]] = None,
        knowledge_base: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """批量处理文本"""
        start_time = time.time()
        track_id = generate_track_id("batch_text")
        
        try:
            if not texts:
                raise ValueError("文本列表不能为空")
            
            # 过滤空文本
            valid_texts = [text.strip() for text in texts if text.strip()]
            if not valid_texts:
                raise ValueError("没有有效的文本内容")
            
            self.logger.info(f"开始批量处理文本: {len(valid_texts)}条")
            
            # 调整doc_ids长度
            if doc_ids:
                if len(doc_ids) != len(texts):
                    self.logger.warning("doc_ids长度与texts不匹配，将截断或填充")
                    doc_ids = doc_ids[:len(valid_texts)]
                    while len(doc_ids) < len(valid_texts):
                        doc_ids.append(None)
            
            # 批量插入
            result_track_id = await guixiaoxirag_service.insert_texts(
                texts=valid_texts,
                doc_ids=doc_ids,
                track_id=track_id,
                working_dir=self._get_kb_working_dir(knowledge_base),
                language=language
            )
            
            processing_time = time.time() - start_time
            self._update_stats(processing_time, success=True)
            
            result = {
                "success": True,
                "track_id": result_track_id,
                "total_texts": len(texts),
                "valid_texts": len(valid_texts),
                "processing_time": processing_time,
                "knowledge_base": knowledge_base,
                "language": language
            }
            
            self.logger.info(f"批量文本处理成功: {len(valid_texts)}条, 耗时: {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_stats(processing_time, success=False)
            
            error_result = {
                "success": False,
                "track_id": track_id,
                "error": str(e),
                "processing_time": processing_time
            }
            
            self.logger.error(f"批量文本处理失败: {str(e)}")
            return error_result
    
    def _get_supported_files(
        self, 
        directory_path: str, 
        recursive: bool = True,
        file_patterns: Optional[List[str]] = None
    ) -> List[str]:
        """获取目录中所有支持的文件"""
        supported_files = []
        
        try:
            if recursive:
                for root, dirs, files in os.walk(directory_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if self._should_include_file(file_path, file_patterns):
                            supported_files.append(file_path)
            else:
                for item in os.listdir(directory_path):
                    file_path = os.path.join(directory_path, item)
                    if os.path.isfile(file_path) and self._should_include_file(file_path, file_patterns):
                        supported_files.append(file_path)
        
        except Exception as e:
            self.logger.error(f"获取文件列表失败: {e}")
        
        return supported_files
    
    def _should_include_file(self, file_path: str, file_patterns: Optional[List[str]] = None) -> bool:
        """判断是否应该包含文件"""
        # 检查文件类型
        if not validate_file_type(os.path.basename(file_path)):
            return False
        
        # 检查文件模式（如果指定）
        if file_patterns:
            file_name = os.path.basename(file_path).lower()
            return any(pattern.lower() in file_name for pattern in file_patterns)
        
        return True
    
    def _get_kb_working_dir(self, knowledge_base: Optional[str]) -> Optional[str]:
        """获取知识库工作目录"""
        if knowledge_base:
            return os.path.join("./knowledgeBase", knowledge_base)
        return None
    
    def _update_stats(self, processing_time: float, success: bool = True):
        """更新处理统计"""
        if success:
            self.processing_stats["total_processed"] += 1
        else:
            self.processing_stats["total_failed"] += 1
        
        # 更新平均处理时间
        total_operations = self.processing_stats["total_processed"] + self.processing_stats["total_failed"]
        current_avg = self.processing_stats["avg_processing_time"]
        self.processing_stats["avg_processing_time"] = (
            (current_avg * (total_operations - 1) + processing_time) / total_operations
        )
        
        self.processing_stats["last_activity"] = time.time()
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计"""
        stats = self.processing_stats.copy()
        if stats["last_activity"]:
            stats["idle_time"] = time.time() - stats["last_activity"]
        return stats
    
    def reset_stats(self):
        """重置统计"""
        self.processing_stats = {
            "total_processed": 0,
            "total_failed": 0,
            "avg_processing_time": 0.0,
            "last_activity": None
        }


# 全局文档处理器实例
document_processor = DocumentProcessor()
