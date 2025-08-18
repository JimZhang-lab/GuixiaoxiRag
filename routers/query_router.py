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
    基于知识图谱的智能查询，支持多种查询模式和参数优化。

    超时说明：默认大模型请求超时为 240 秒，可通过 .env 配置 LLM_TIMEOUT 调整。

    **查询模式说明：**
    - local: 本地模式 - 专注于上下文相关信息
    - global: 全局模式 - 利用全局知识
    - hybrid: 混合模式 - 结合本地和全局检索方法（推荐）
    - naive: 朴素模式 - 执行基本搜索
    - mix: 混合模式 - 整合知识图谱和向量检索
    - bypass: 绕过模式 - 直接返回结果

    **参数说明：**
    - query: 查询内容（必填）
    - mode: 查询模式（可选，默认hybrid）
    - top_k: 返回结果数量（可选，默认20）
    - stream: 是否流式返回（可选，默认false）
    - only_need_context: 是否只返回上下文（可选）
    - only_need_prompt: 是否只返回提示（可选）
    - response_type: 响应类型（可选）
    - knowledge_base: 知识库名称（可选）
    - language: 回答语言（可选）
    - performance_mode: 性能模式（fast/balanced/quality）

    **使用示例：**
    ```json
    {
        "query": "什么是人工智能？",
        "mode": "hybrid",
        "top_k": 20,
        "knowledge_base": "ai_kb",
        "language": "中文",
        "performance_mode": "balanced"
    }
    ```
    """
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
    批量处理多个查询请求，提高查询效率。

    超时说明：默认单条 LLM 请求超时 240 秒；批量接口可通过 body.timeout 控制聚合等待超时。

    **参数说明：**
    - queries: 查询列表（必填，最多50个）
    - mode: 查询模式（可选，应用于所有查询）
    - top_k: 每个查询返回的结果数量（可选）
    - knowledge_base: 知识库名称（可选）
    - language: 回答语言（可选）
    - parallel: 是否并行处理（可选，默认true）
    - timeout: 超时时间（可选，默认300秒）

    **处理特点：**
    - 支持并行处理以提高效率
    - 单个查询失败不影响其他查询
    - 返回每个查询的详细结果
    - 支持超时控制

    **使用示例：**
    ```json
    {
        "queries": [
            "什么是机器学习？",
            "深度学习的应用领域有哪些？",
            "如何选择合适的算法？"
        ],
        "mode": "hybrid",
        "top_k": 10,
        "parallel": true,
        "timeout": 300
    }
    ```
    """
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
