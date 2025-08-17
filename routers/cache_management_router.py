"""
缓存管理路由
处理缓存清理、统计等功能
"""
from fastapi import APIRouter

from model import BaseResponse
from api.cache_management_api import CacheManagementAPI

# 创建路由器
router = APIRouter(prefix="/api/v1", tags=["缓存管理"])

# 创建API处理器实例
cache_api = CacheManagementAPI()


@router.delete(
    "/cache/clear",
    response_model=BaseResponse,
    summary="清理所有缓存",
    description="""
    清理系统中的所有缓存数据，包括LLM响应缓存、向量缓存等。

    **清理内容：**
    - LLM响应缓存
    - 向量计算缓存
    - 知识图谱缓存
    - 文档处理缓存
    - 查询结果缓存

    **使用场景：**
    - 系统维护和清理
    - 释放内存空间
    - 强制重新计算
    - 故障排除

    **注意事项：**
    - 清理后首次查询可能较慢
    - 建议在低峰期执行
    - 操作不可逆，请谨慎使用
    """,
    responses={
        200: {
            "description": "缓存清理成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "缓存清理成功",
                        "data": {
                            "cleared_caches": ["llm_response", "vector", "knowledge_graph"],
                            "freed_memory_mb": 256.5,
                            "cache_stats": {
                                "before": {"total_size_mb": 512.3, "item_count": 1024},
                                "after": {"total_size_mb": 0, "item_count": 0}
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "缓存清理失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "缓存清理失败: 权限不足"
                    }
                }
            }
        }
    }
)
async def clear_all_cache():
    """清理所有缓存"""
    return await cache_api.clear_all_cache()


@router.delete(
    "/cache/clear/{cache_type}",
    response_model=BaseResponse,
    summary="清理指定类型缓存",
    description="""
    清理指定类型的缓存数据。

    **支持的缓存类型：**
    - `llm`: LLM响应缓存
    - `vector`: 向量计算缓存
    - `knowledge_graph`: 知识图谱缓存
    - `documents`: 文档处理缓存
    - `queries`: 查询结果缓存

    **使用场景：**
    - 选择性清理特定缓存
    - 精确控制缓存管理
    - 性能优化和调试

    **优势：**
    - 避免清理所有缓存的性能影响
    - 保留有用的缓存数据
    - 更精细的缓存控制
    """,
    responses={
        200: {
            "description": "指定缓存清理成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "LLM缓存清理成功",
                        "data": {
                            "cache_type": "llm",
                            "cleared_items": 128,
                            "freed_memory_mb": 64.2
                        }
                    }
                }
            }
        },
        400: {
            "description": "不支持的缓存类型",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "不支持的缓存类型: invalid_type"
                    }
                }
            }
        }
    }
)
async def clear_specific_cache(cache_type: str):
    """清理指定类型的缓存"""
    return await cache_api.clear_specific_cache(cache_type)


@router.get(
    "/cache/stats",
    response_model=BaseResponse,
    summary="获取缓存统计信息",
    description="""
    获取系统中各种缓存的统计信息。

    **统计信息包括：**
    - 各类缓存的大小和项目数量
    - 内存使用情况
    - 缓存命中率
    - 缓存性能指标

    **使用场景：**
    - 监控缓存使用情况
    - 性能分析和优化
    - 容量规划
    - 故障诊断

    **返回数据：**
    - 实时缓存统计
    - 内存使用详情
    - 性能指标
    """,
    responses={
        200: {
            "description": "缓存统计信息获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "操作成功",
                        "data": {
                            "total_memory_mb": 512.3,
                            "caches": {
                                "llm_response": {
                                    "size_mb": 128.5,
                                    "item_count": 256,
                                    "hit_rate": 0.85
                                },
                                "vector": {
                                    "size_mb": 256.8,
                                    "item_count": 1024,
                                    "hit_rate": 0.92
                                }
                            },
                            "system_memory": {
                                "total_mb": 8192,
                                "available_mb": 4096,
                                "used_percent": 50.0
                            }
                        }
                    }
                }
            }
        }
    }
)
async def get_cache_stats():
    """获取缓存统计信息"""
    return await cache_api.get_cache_stats()
