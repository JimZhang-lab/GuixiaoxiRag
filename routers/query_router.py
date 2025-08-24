"""
查询路由
处理智能查询、意图分析、批量查询等功能
"""
from fastapi import APIRouter, HTTPException

from model import (
    BaseResponse, QueryRequest, BatchQueryRequest, 
    QueryIntentAnalysisRequest, SafeQueryRequest,
    QueryResponse, BatchQueryResponse, QueryIntentAnalysisResponse,
    SafeQueryResponse
)
from api.query_api import QueryAPI

# 创建路由器
router = APIRouter(prefix="/api/v1", tags=["查询"])

# 创建API处理器实例
query_api = QueryAPI()


@router.post(
    "/query",
    response_model=BaseResponse,
    summary="智能知识查询",
    description="""
    基于知识图谱和向量检索的智能查询系统，支持多种查询模式和参数优化。

    **🚀 核心特性：**
    - 多模态检索（向量+知识图谱）
    - 智能查询理解和扩展
    - 上下文感知的答案生成
    - 实时流式响应支持
    - 多语言查询支持

    **⏱️ 超时配置：**
    - 默认LLM请求超时：240秒
    - 可通过.env的LLM_TIMEOUT配置调整
    - 支持查询级别的超时控制

    **🎯 查询模式详解：**
    - **local**: 本地模式 - 专注于上下文相关信息，适合精确查询
    - **global**: 全局模式 - 利用全局知识图谱，适合广泛主题查询
    - **hybrid**: 混合模式 - 结合本地和全局检索（🌟推荐）
    - **naive**: 朴素模式 - 执行基本向量搜索，速度最快
    - **mix**: 混合模式 - 整合知识图谱和向量检索，适合复杂查询
    - **bypass**: 绕过模式 - 直接返回检索结果，用于调试

    **📊 性能模式：**
    - **fast**: 快速模式 - 优先响应速度，适合实时交互
    - **balanced**: 平衡模式 - 兼顾速度和质量（默认）
    - **quality**: 质量模式 - 优先结果质量，适合深度分析

    **🔧 参数说明：**
    - query: 查询内容（必填，1-2000字符）
    - mode: 查询模式（可选，默认hybrid）
    - top_k: 返回结果数量（可选，1-50，默认20）
    - stream: 是否流式返回（可选，默认false）
    - only_need_context: 仅返回上下文（可选，用于调试）
    - only_need_prompt: 仅返回提示词（可选，用于调试）
    - response_type: 响应类型（可选，text/json/markdown）
    - knowledge_base: 知识库名称（可选，默认使用当前知识库）
    - language: 回答语言（可选，中文/English等）
    - performance_mode: 性能模式（可选，默认balanced）

    **💡 使用建议：**
    - 日常查询推荐使用hybrid模式
    - 需要快速响应时使用fast性能模式
    - 复杂分析查询使用quality性能模式
    - 调试时可使用only_need_context查看检索结果
    """,
    responses={
        200: {
            "description": "查询成功",
            "content": {
                "application/json": {
                    "examples": {
                        "normal_query": {
                            "summary": "普通查询成功",
                            "value": {
                                "success": True,
                                "message": "查询完成",
                                "data": {
                                    "answer": "人工智能（AI）是计算机科学的一个分支...",
                                    "context": ["相关文档片段1", "相关文档片段2"],
                                    "sources": ["doc1.pdf", "doc2.txt"],
                                    "confidence": 0.95,
                                    "response_time": 1.25,
                                    "mode_used": "hybrid",
                                    "tokens_used": 1024
                                }
                            }
                        },
                        "context_only": {
                            "summary": "仅返回上下文",
                            "value": {
                                "success": True,
                                "message": "上下文检索完成",
                                "data": {
                                    "context": ["检索到的相关文档片段"],
                                    "sources": ["source1.pdf"],
                                    "similarity_scores": [0.95, 0.87, 0.82]
                                }
                            }
                        }
                    }
                }
            }
        },
        422: {
            "description": "参数验证失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "query"],
                                "msg": "查询内容不能为空",
                                "type": "value_error"
                            }
                        ]
                    }
                }
            }
        },
        408: {
            "description": "查询超时",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "查询超时，请尝试简化查询或调整超时设置"
                    }
                }
            }
        },
        500: {
            "description": "服务器内部错误",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "查询处理失败: 知识库连接错误"
                    }
                }
            }
        }
    }
)
async def query(request: QueryRequest):
    """智能知识查询"""
    return await query_api.query(request)


# @router.post(
#     "/query/safe",
#     response_model=BaseResponse,
#     summary="安全智能查询",
#     description="""
#     结合意图分析和安全检查的智能查询，确保查询内容的安全性。
    
#     **处理流程：**
#     1. 查询意图分析
#     2. 安全级别评估
#     3. 查询增强（如果安全）
#     4. 执行查询（如果通过安全检查）
    
#     **安全特性：**
#     - 自动识别和拒绝不当查询
#     - 提供安全替代建议
#     - 记录可疑查询行为
#     - 支持查询增强和优化
    
#     **参数说明：**
#     - query: 查询内容（必填）
#     - mode: 查询模式（可选）
#     - knowledge_base: 知识库名称（可选）
#     - language: 查询语言（可选）
#     - enable_intent_analysis: 是否启用意图分析（可选）
#     - enable_query_enhancement: 是否启用查询增强（可选）
#     - safety_check: 是否进行安全检查（可选）
    
#     **使用示例：**
#     ```json
#     {
#         "query": "人工智能的发展历史",
#         "mode": "hybrid",
#         "knowledge_base": "ai_kb",
#         "enable_intent_analysis": true,
#         "enable_query_enhancement": true,
#         "safety_check": true
#     }
#     ```
#     """
# )
# async def safe_query(request: SafeQueryRequest):
#     """安全智能查询"""
#     return await query_api.safe_query(request)


@router.get(
    "/query/modes",
    response_model=BaseResponse,
    summary="获取查询模式列表",
    description="""
    获取所有支持的查询模式及其详细说明。
    
    **返回信息：**
    - 查询模式列表
    - 每种模式的详细描述
    - 推荐使用场景
    - 性能特点
    
    **查询模式对比：**
    - local: 适合上下文相关的精确查询
    - global: 适合需要全局知识的广泛查询
    - hybrid: 平衡精确性和覆盖面，适合大多数场景
    - naive: 简单快速，适合基础查询
    - mix: 综合多种检索方法，适合复杂查询
    - bypass: 直接模式，适合测试和调试
    """
)
async def get_query_modes():
    """获取查询模式列表"""
    return await query_api.get_query_modes()


@router.post(
    "/query/batch",
    response_model=BaseResponse,
    summary="批量查询处理",
    description="""
    高效批量处理多个查询请求，支持并行处理和智能调度。

    **🚀 批量处理优势：**
    - 并行处理提升整体效率
    - 智能负载均衡
    - 资源复用减少开销
    - 统一的错误处理和重试机制

    **⏱️ 超时控制：**
    - 单条LLM请求超时：240秒（可通过.env配置）
    - 批量聚合超时：通过body.timeout控制（默认300秒）
    - 支持查询级别的独立超时

    **📊 处理策略：**
    - **并行模式**：同时处理多个查询（默认）
    - **串行模式**：按顺序处理，适合资源受限环境
    - **混合模式**：根据查询复杂度动态调整

    **🔧 参数说明：**
    - queries: 查询列表（必填，1-50个查询）
    - mode: 查询模式（可选，应用于所有查询，默认hybrid）
    - top_k: 每个查询返回结果数量（可选，1-20，默认10）
    - knowledge_base: 知识库名称（可选）
    - language: 回答语言（可选，统一应用）
    - parallel: 是否并行处理（可选，默认true）
    - timeout: 批量处理超时时间（可选，默认300秒）
    - max_concurrent: 最大并发数（可选，默认5）
    - retry_failed: 是否重试失败的查询（可选，默认false）

    **📈 性能优化：**
    - 智能批次分组
    - 缓存复用机制
    - 动态资源分配
    - 实时进度反馈

    **🛡️ 容错机制：**
    - 单个查询失败不影响其他查询
    - 自动重试机制（可配置）
    - 详细的错误分类和报告
    - 部分成功结果返回

    **💡 使用建议：**
    - 相似查询建议分组处理
    - 复杂查询适当降低并发数
    - 生产环境建议启用重试机制
    """,
    responses={
        200: {
            "description": "批量查询完成",
            "content": {
                "application/json": {
                    "examples": {
                        "all_success": {
                            "summary": "全部成功",
                            "value": {
                                "success": True,
                                "message": "批量查询完成：3个成功，0个失败",
                                "data": {
                                    "total_queries": 3,
                                    "successful_queries": 3,
                                    "failed_queries": 0,
                                    "total_time": 5.2,
                                    "results": [
                                        {
                                            "query": "什么是机器学习？",
                                            "success": True,
                                            "answer": "机器学习是人工智能的一个分支...",
                                            "response_time": 1.8
                                        }
                                    ]
                                }
                            }
                        },
                        "partial_success": {
                            "summary": "部分成功",
                            "value": {
                                "success": True,
                                "message": "批量查询完成：2个成功，1个失败",
                                "data": {
                                    "total_queries": 3,
                                    "successful_queries": 2,
                                    "failed_queries": 1,
                                    "total_time": 8.5,
                                    "results": [
                                        {
                                            "query": "正常查询",
                                            "success": True,
                                            "answer": "查询结果..."
                                        },
                                        {
                                            "query": "失败查询",
                                            "success": False,
                                            "error": "查询超时"
                                        }
                                    ],
                                    "failed_queries_details": [
                                        {
                                            "query": "失败查询",
                                            "error": "查询超时",
                                            "error_code": "TIMEOUT"
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        },
        422: {
            "description": "参数验证失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "queries"],
                                "msg": "查询列表不能为空",
                                "type": "value_error"
                            }
                        ]
                    }
                }
            }
        },
        413: {
            "description": "查询数量超限",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "查询数量超过限制（最多50个）"
                    }
                }
            }
        }
    }
)
async def batch_query(request: BatchQueryRequest):
    """批量查询处理"""
    return await query_api.batch_query(request)


@router.post(
    "/query/optimized",
    response_model=BaseResponse,
    summary="优化参数查询",
    description="""
    使用性能优化参数的查询，根据查询模式和性能要求自动调整参数。

    超时说明：默认大模型请求超时为 240 秒，可通过 .env 的 LLM_TIMEOUT 配置调整。

    **优化特性：**
    - 根据查询模式自动优化参数
    - 支持不同性能级别（fast/balanced/quality）
    - 动态调整token限制和检索参数
    - 提供性能监控和建议

    **性能模式：**
    - fast: 快速模式，优先响应速度
    - balanced: 平衡模式，兼顾速度和质量
    - quality: 质量模式，优先结果质量

    **参数说明：**
    - query: 查询内容（必填）
    - mode: 查询模式（可选）
    - performance_mode: 性能模式（可选）
    - custom_params: 自定义参数（可选）
    """
)
async def optimized_query(request: dict):
    """使用优化参数的查询"""
    return await query_api.optimized_query(request)


# 导出路由器
__all__ = ["router"]
