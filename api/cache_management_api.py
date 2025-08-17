"""
缓存管理API
处理缓存清理、统计等业务逻辑
"""
from fastapi import HTTPException
from common.logging_utils import logger_manager
from handler.guixiaoxirag_service import guixiaoxirag_service
from model import BaseResponse

logger = logger_manager.get_logger("cache_management_api")


class CacheManagementAPI:
    """缓存管理API处理器"""

    async def clear_all_cache(self) -> BaseResponse:
        """清理所有缓存"""
        try:
            import gc
            import psutil
            import os

            # 获取清理前的内存使用情况
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB

            cleared_caches = []

            # 清理GuiXiaoXiRag服务缓存
            if hasattr(guixiaoxirag_service, 'rag') and guixiaoxirag_service.rag:
                # 清理LLM响应缓存
                if hasattr(guixiaoxirag_service.rag, 'llm_response_cache'):
                    try:
                        await guixiaoxirag_service.rag.llm_response_cache.clear()
                        cleared_caches.append("llm_response")
                    except Exception as e:
                        logger.warning(f"清理LLM响应缓存失败: {e}")

                # 清理向量数据库缓存
                for vdb_name in ['entities_vdb', 'relationships_vdb', 'chunks_vdb']:
                    if hasattr(guixiaoxirag_service.rag, vdb_name):
                        try:
                            vdb = getattr(guixiaoxirag_service.rag, vdb_name)
                            if hasattr(vdb, 'clear_cache'):
                                await vdb.clear_cache()
                            cleared_caches.append(f"vector_{vdb_name}")
                        except Exception as e:
                            logger.warning(f"清理{vdb_name}缓存失败: {e}")

            # 清理Python垃圾回收
            collected = gc.collect()
            cleared_caches.append("python_gc")

            # 获取清理后的内存使用情况
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            freed_memory = max(0, memory_before - memory_after)

            return BaseResponse(
                message="缓存清理成功",
                data={
                    "cleared_caches": cleared_caches,
                    "freed_memory_mb": round(freed_memory, 2),
                    "gc_collected_objects": collected,
                    "cache_stats": {
                        "before": {"memory_mb": round(memory_before, 2)},
                        "after": {"memory_mb": round(memory_after, 2)}
                    }
                }
            )
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def clear_specific_cache(self, cache_type: str) -> BaseResponse:
        """清理指定类型的缓存"""
        try:
            import gc

            supported_types = ["llm", "vector", "knowledge_graph", "documents", "queries"]

            if cache_type not in supported_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的缓存类型: {cache_type}。支持的类型: {', '.join(supported_types)}"
                )

            cleared_items = 0
            freed_memory = 0

            if cache_type == "llm":
                # 清理LLM响应缓存
                if hasattr(guixiaoxirag_service, 'rag') and guixiaoxirag_service.rag:
                    if hasattr(guixiaoxirag_service.rag, 'llm_response_cache'):
                        cache = guixiaoxirag_service.rag.llm_response_cache
                        if hasattr(cache, 'size'):
                            cleared_items = await cache.size()
                        await cache.clear()

            elif cache_type == "vector":
                # 清理向量缓存
                if hasattr(guixiaoxirag_service, 'rag') and guixiaoxirag_service.rag:
                    for vdb_name in ['entities_vdb', 'relationships_vdb', 'chunks_vdb']:
                        if hasattr(guixiaoxirag_service.rag, vdb_name):
                            vdb = getattr(guixiaoxirag_service.rag, vdb_name)
                            if hasattr(vdb, 'clear_cache'):
                                await vdb.clear_cache()
                                cleared_items += 1

            elif cache_type == "knowledge_graph":
                # 清理知识图谱缓存
                if hasattr(guixiaoxirag_service, 'rag') and guixiaoxirag_service.rag:
                    if hasattr(guixiaoxirag_service.rag, 'chunk_entity_relation_graph'):
                        graph = guixiaoxirag_service.rag.chunk_entity_relation_graph
                        if hasattr(graph, 'clear_cache'):
                            await graph.clear_cache()
                            cleared_items = 1

            # 执行垃圾回收
            collected = gc.collect()

            return BaseResponse(
                message=f"{cache_type.upper()}缓存清理成功",
                data={
                    "cache_type": cache_type,
                    "cleared_items": cleared_items,
                    "gc_collected_objects": collected,
                    "freed_memory_mb": round(freed_memory, 2)
                }
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"清理{cache_type}缓存失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_cache_stats(self) -> BaseResponse:
        """获取缓存统计信息"""
        try:
            import psutil
            import os

            # 获取系统内存信息
            memory = psutil.virtual_memory()
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info().rss / 1024 / 1024  # MB

            cache_stats = {
                "total_memory_mb": round(process_memory, 2),
                "caches": {},
                "system_memory": {
                    "total_mb": round(memory.total / 1024 / 1024, 2),
                    "available_mb": round(memory.available / 1024 / 1024, 2),
                    "used_percent": round(memory.percent, 1)
                }
            }

            # 获取各种缓存的统计信息
            if hasattr(guixiaoxirag_service, 'rag') and guixiaoxirag_service.rag:
                # LLM响应缓存统计
                if hasattr(guixiaoxirag_service.rag, 'llm_response_cache'):
                    cache = guixiaoxirag_service.rag.llm_response_cache
                    try:
                        size = await cache.size() if hasattr(cache, 'size') else 0
                        cache_stats["caches"]["llm_response"] = {
                            "item_count": size,
                            "size_mb": round(size * 0.1, 2),  # 估算
                            "hit_rate": 0.0  # 需要实际实现
                        }
                    except:
                        cache_stats["caches"]["llm_response"] = {
                            "item_count": 0,
                            "size_mb": 0,
                            "hit_rate": 0.0
                        }

                # 向量数据库统计
                vector_total_size = 0
                vector_total_items = 0
                for vdb_name in ['entities_vdb', 'relationships_vdb', 'chunks_vdb']:
                    if hasattr(guixiaoxirag_service.rag, vdb_name):
                        try:
                            vdb = getattr(guixiaoxirag_service.rag, vdb_name)
                            if hasattr(vdb, 'size'):
                                size = await vdb.size()
                                vector_total_items += size
                                vector_total_size += size * 0.5  # 估算每个向量0.5KB
                        except:
                            pass

                cache_stats["caches"]["vector"] = {
                    "item_count": vector_total_items,
                    "size_mb": round(vector_total_size / 1024, 2),
                    "hit_rate": 0.0
                }

            return BaseResponse(data=cache_stats)
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))
