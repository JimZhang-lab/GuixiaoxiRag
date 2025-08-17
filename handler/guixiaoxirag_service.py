"""
GuiXiaoXiRag服务核心管理类
优化版本 - 更好的错误处理、性能监控和配置管理
"""
import os
import asyncio
import time
from typing import List, Dict, Any, Optional
import numpy as np
from pathlib import Path

from core.rag import GuiXiaoXiRag, QueryParam
from core.rag.llm.openai import openai_embed, openai_complete_if_cache
from core.rag.kg.shared_storage import initialize_pipeline_status
from core.rag.utils import setup_logger, EmbeddingFunc
from core.rag.types import KnowledgeGraph

from common.config import settings
from common.utils import create_or_update_knowledge_graph_json, generate_track_id
from common.logging_utils import logger_manager
from common.performance_config import get_optimized_query_params


class GuiXiaoXiRagService:
    """GuiXiaoXiRag服务管理类"""

    def __init__(self):
        self.rag: Optional[GuiXiaoXiRag] = None
        self.logger = logger_manager.setup_service_logger()
        self._initialized = False
        self._current_working_dir = None
        self._current_language = "中文"  # 默认语言
        self._rag_instances = {}  # 缓存不同知识库的实例
        self._initialization_lock = asyncio.Lock()
        self._performance_stats = {
            "total_queries": 0,
            "total_inserts": 0,
            "avg_query_time": 0.0,
            "avg_insert_time": 0.0,
            "last_activity": None
        }
        
    async def initialize(
        self, 
        working_dir: str = None, 
        language: str = None,
        force_reinit: bool = False
    ) -> None:
        """初始化GuiXiaoXiRag实例"""
        async with self._initialization_lock:
            if working_dir is None:
                working_dir = settings.working_dir
            if language is None:
                language = self._current_language

            # 检查是否已经初始化了相同配置的实例
            instance_key = f"{working_dir}_{language}"
            if not force_reinit and instance_key in self._rag_instances:
                self.rag = self._rag_instances[instance_key]
                self._current_working_dir = working_dir
                self._current_language = language
                self._initialized = True
                self.logger.info(f"使用缓存的RAG实例: {instance_key}")
                return

            # 设置日志
            setup_logger("guixiaoxiRag", level=settings.log_level)

            # 确保工作目录存在
            os.makedirs(working_dir, exist_ok=True)

            try:
                start_time = time.time()
                
                # 创建GuiXiaoXiRag实例，避免导入有问题的模块
                import sys
                original_argv = sys.argv.copy()
                sys.argv = ['guixiaoxirag_service']  # 临时修改argv避免参数解析冲突

                rag_instance = GuiXiaoXiRag(
                    working_dir=working_dir,
                    llm_model_func=lambda *args, **kwargs: self._llm_model_func(*args, language=language, **kwargs),
                    embedding_func=EmbeddingFunc(
                        embedding_dim=settings.embedding_dim,
                        max_token_size=settings.max_token_size,
                        func=self._embedding_func
                    ),
                    addon_params={
                        "language": language
                    }
                )

                # 恢复原始argv
                sys.argv = original_argv

                # 初始化存储
                await rag_instance.initialize_storages()
                await initialize_pipeline_status()

                # 缓存实例
                self._rag_instances[instance_key] = rag_instance
                self.rag = rag_instance
                self._current_working_dir = working_dir
                self._current_language = language
                self._initialized = True

                init_time = time.time() - start_time
                self.logger.info(
                    f"GuiXiaoXiRag服务初始化成功 - "
                    f"工作目录: {working_dir}, 语言: {language}, "
                    f"初始化时间: {init_time:.2f}s"
                )

            except Exception as e:
                self.logger.error(f"GuiXiaoXiRag服务初始化失败: {str(e)}", exc_info=True)
                raise
    
    async def _llm_model_func(
        self,
        prompt: str,
        system_prompt: str = None,
        history_messages: List = None,
        language: str = None,
        **kwargs
    ) -> str:
        """大语言模型函数"""
        if history_messages is None:
            history_messages = []
        if language is None:
            language = self._current_language

        # 根据语言调整系统提示
        if system_prompt and language:
            language_instruction = self._get_language_instruction(language)
            system_prompt = f"{system_prompt}\n\n{language_instruction}"

        try:
            return await openai_complete_if_cache(
                model=settings.openai_chat_model,
                prompt=prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                api_key=settings.openai_chat_api_key,
                base_url=settings.openai_api_base,
                **kwargs
            )
        except Exception as e:
            self.logger.error(f"LLM调用失败: {str(e)}")
            raise

    def _get_language_instruction(self, language: str) -> str:
        """获取语言指令"""
        language_instructions = {
            "中文": "请用中文回答。",
            "英文": "Please answer in English.",
            "English": "Please answer in English.",
            "Chinese": "请用中文回答。",
            "zh": "请用中文回答。",
            "en": "Please answer in English.",
            "zh-CN": "请用中文回答。",
            "en-US": "Please answer in English."
        }
        return language_instructions.get(language, "请用中文回答。")
    
    async def _embedding_func(self, texts: List[str]) -> np.ndarray:
        """嵌入函数"""
        try:
            return await openai_embed(
                texts,
                model=settings.openai_embedding_model,
                api_key=settings.openai_embedding_api_key,
                base_url=settings.openai_embedding_api_base
            )
        except Exception as e:
            self.logger.error(f"Embedding调用失败: {str(e)}")
            raise
    
    async def insert_text(
        self,
        text: str,
        doc_id: str = None,
        file_path: str = None,
        track_id: str = None,
        working_dir: str = None,
        language: str = None
    ) -> str:
        """插入文本"""
        start_time = time.time()
        
        # 如果指定了不同的知识库或语言，重新初始化
        if working_dir or language:
            await self.initialize(working_dir=working_dir, language=language)
        elif not self._initialized:
            await self.initialize()

        if track_id is None:
            track_id = generate_track_id("insert")

        try:
            result = await self.rag.ainsert(
                input=text,
                ids=doc_id,
                file_paths=file_path,
                track_id=track_id
            )
            
            kb_name = Path(self._current_working_dir).name if self._current_working_dir else "default"
            insert_time = time.time() - start_time
            
            # 更新性能统计
            self._update_insert_stats(insert_time)
            
            self.logger.info(
                f"文本插入成功 - 知识库: {kb_name}, 语言: {self._current_language}, "
                f"track_id: {result}, 耗时: {insert_time:.2f}s"
            )

            # 插入成功后，自动创建或更新知识图谱JSON文件
            try:
                success = create_or_update_knowledge_graph_json(self._current_working_dir)
                if success:
                    self.logger.debug(f"知识图谱JSON文件已更新，知识库: {kb_name}")
                else:
                    self.logger.warning(f"知识图谱JSON文件更新失败，知识库: {kb_name}")
            except Exception as kg_error:
                self.logger.error(f"更新知识图谱JSON文件时发生错误: {str(kg_error)}")

            return result
            
        except Exception as e:
            self.logger.error(f"文本插入失败: {str(e)}", exc_info=True)
            raise
    
    async def insert_texts(
        self,
        texts: List[str],
        doc_ids: List[str] = None,
        file_paths: List[str] = None,
        track_id: str = None,
        working_dir: str = None,
        language: str = None
    ) -> str:
        """批量插入文本"""
        start_time = time.time()
        
        # 如果指定了不同的知识库或语言，重新初始化
        if working_dir or language:
            await self.initialize(working_dir=working_dir, language=language)
        elif not self._initialized:
            await self.initialize()

        if track_id is None:
            track_id = generate_track_id("batch_insert")

        try:
            result = await self.rag.ainsert(
                input=texts,
                ids=doc_ids,
                file_paths=file_paths,
                track_id=track_id
            )
            
            kb_name = Path(self._current_working_dir).name if self._current_working_dir else "default"
            insert_time = time.time() - start_time
            
            # 更新性能统计
            self._update_insert_stats(insert_time)
            
            self.logger.info(
                f"批量文本插入成功 - 知识库: {kb_name}, 语言: {self._current_language}, "
                f"数量: {len(texts)}, track_id: {result}, 耗时: {insert_time:.2f}s"
            )

            # 插入成功后，自动创建或更新知识图谱JSON文件
            try:
                success = create_or_update_knowledge_graph_json(self._current_working_dir)
                if success:
                    self.logger.debug(f"知识图谱JSON文件已更新，知识库: {kb_name}")
                else:
                    self.logger.warning(f"知识图谱JSON文件更新失败，知识库: {kb_name}")
            except Exception as kg_error:
                self.logger.error(f"更新知识图谱JSON文件时发生错误: {str(kg_error)}")

            return result

        except Exception as e:
            self.logger.error(f"批量文本插入失败: {str(e)}", exc_info=True)
            raise

    async def query(
        self,
        query: str,
        mode: str = "hybrid",
        top_k: int = 20,
        stream: bool = False,
        working_dir: str = None,
        language: str = None,
        performance_mode: str = "balanced",
        **kwargs
    ) -> str:
        """查询"""
        start_time = time.time()

        # 如果指定了不同的知识库或语言，重新初始化
        if working_dir or language:
            await self.initialize(working_dir=working_dir, language=language)
        elif not self._initialized:
            await self.initialize()

        try:
            # 获取优化的查询参数
            optimized_params = get_optimized_query_params(mode, performance_mode)

            # 合并用户参数和优化参数
            final_params = {**optimized_params, **kwargs}
            if 'top_k' not in kwargs:
                final_params['top_k'] = min(top_k, optimized_params.get('top_k', top_k))

            # 过滤掉QueryParam不支持的参数
            supported_params = {}
            for key, value in final_params.items():
                if key not in ['timeout', 'enable_rerank']:  # 过滤掉不支持的参数
                    supported_params[key] = value



            param = QueryParam(
                mode=mode,
                stream=stream,
                **supported_params
            )

            result = await self.rag.aquery(query, param)

            kb_name = Path(self._current_working_dir).name if self._current_working_dir else "default"
            query_time = time.time() - start_time

            # 更新性能统计
            self._update_query_stats(query_time)

            self.logger.info(
                f"查询成功 - 知识库: {kb_name}, 语言: {self._current_language}, "
                f"模式: {mode}, 耗时: {query_time:.2f}s"
            )

            return result

        except Exception as e:
            self.logger.error(f"查询失败: {str(e)}", exc_info=True)
            raise

    async def get_knowledge_graph(
        self,
        node_label: str,
        max_depth: int = 3,
        max_nodes: int = None
    ) -> KnowledgeGraph:
        """获取知识图谱"""
        if not self._initialized:
            await self.initialize()

        try:
            result = await self.rag.get_knowledge_graph(
                node_label=node_label,
                max_depth=max_depth,
                max_nodes=max_nodes
            )
            self.logger.info(f"获取知识图谱成功，节点标签: {node_label}")
            return result
        except Exception as e:
            self.logger.error(f"获取知识图谱失败: {str(e)}", exc_info=True)
            raise

    async def switch_knowledge_base(self, working_dir: str, language: str = None) -> bool:
        """切换知识库"""
        try:
            if language is None:
                language = self._current_language
            await self.initialize(working_dir=working_dir, language=language)
            return True
        except Exception as e:
            self.logger.error(f"切换知识库失败: {str(e)}")
            return False

    def set_language(self, language: str) -> bool:
        """设置回答语言"""
        try:
            self._current_language = language
            self.logger.info(f"语言设置为: {language}")
            return True
        except Exception as e:
            self.logger.error(f"设置语言失败: {str(e)}")
            return False

    def get_current_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return {
            "working_dir": self._current_working_dir,
            "language": self._current_language,
            "initialized": self._initialized,
            "cached_instances": len(self._rag_instances),
            "performance_stats": self._performance_stats.copy()
        }

    def get_supported_languages(self) -> List[str]:
        """获取支持的语言列表"""
        return ["中文", "英文", "English", "Chinese", "zh", "en", "zh-CN", "en-US"]

    def _update_query_stats(self, query_time: float):
        """更新查询统计"""
        self._performance_stats["total_queries"] += 1
        total_queries = self._performance_stats["total_queries"]
        current_avg = self._performance_stats["avg_query_time"]

        # 计算新的平均时间
        self._performance_stats["avg_query_time"] = (
            (current_avg * (total_queries - 1) + query_time) / total_queries
        )
        self._performance_stats["last_activity"] = time.time()

    def _update_insert_stats(self, insert_time: float):
        """更新插入统计"""
        self._performance_stats["total_inserts"] += 1
        total_inserts = self._performance_stats["total_inserts"]
        current_avg = self._performance_stats["avg_insert_time"]

        # 计算新的平均时间
        self._performance_stats["avg_insert_time"] = (
            (current_avg * (total_inserts - 1) + insert_time) / total_inserts
        )
        self._performance_stats["last_activity"] = time.time()

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        stats = self._performance_stats.copy()
        if stats["last_activity"]:
            stats["idle_time"] = time.time() - stats["last_activity"]
        return stats

    def reset_performance_stats(self):
        """重置性能统计"""
        self._performance_stats = {
            "total_queries": 0,
            "total_inserts": 0,
            "avg_query_time": 0.0,
            "avg_insert_time": 0.0,
            "last_activity": None
        }
        self.logger.info("性能统计已重置")

    async def finalize(self):
        """清理资源"""
        try:
            # 清理所有缓存的实例
            for instance in self._rag_instances.values():
                await instance.finalize_storages()
            self._rag_instances.clear()
            self.logger.info("GuiXiaoXiRag服务资源清理完成")
        except Exception as e:
            self.logger.error(f"资源清理失败: {str(e)}")
        self._initialized = False
        self.rag = None
        self._current_working_dir = None

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health_info = {
            "status": "healthy" if self._initialized else "not_initialized",
            "initialized": self._initialized,
            "current_working_dir": self._current_working_dir,
            "current_language": self._current_language,
            "cached_instances": len(self._rag_instances),
            "performance_stats": self.get_performance_stats()
        }

        # 检查RAG实例状态
        if self.rag:
            try:
                # 这里可以添加更详细的健康检查
                health_info["rag_status"] = "active"
            except Exception as e:
                health_info["rag_status"] = f"error: {str(e)}"
                health_info["status"] = "degraded"

        return health_info


# 全局服务实例
guixiaoxirag_service = GuiXiaoXiRagService()
