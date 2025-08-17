"""
查询相关数据模型定义
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .base_models import (
    SupportedLanguage, SupportedQueryMode, SafetyLevel,
    IntentType, ResponseType, PerformanceMode
)
from core.intent_recognition import QueryIntentType, ContentSafetyLevel


class QueryContext(BaseModel):
    """查询上下文模型"""
    user_id: Optional[str] = Field(None, description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    conversation_history: List[Dict[str, str]] = Field(default_factory=list, description="对话历史")
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="用户偏好")
    domain: Optional[str] = Field(None, description="查询领域")
    context_variables: Dict[str, Any] = Field(default_factory=dict, description="上下文变量")


class QueryAnalysisResult(BaseModel):
    """查询分析结果模型"""
    original_query: str = Field(..., description="原始查询")
    processed_query: str = Field(..., description="处理后的查询")
    intent_type: IntentType = Field(..., description="意图类型")
    safety_level: SafetyLevel = Field(..., description="安全级别")
    confidence: float = Field(..., description="置信度")
    keywords: List[str] = Field(default_factory=list, description="关键词")
    entities: List[Dict[str, Any]] = Field(default_factory=list, description="实体")
    sentiment: Optional[str] = Field(None, description="情感倾向")
    complexity: Optional[str] = Field(None, description="查询复杂度")
    language: Optional[SupportedLanguage] = Field(None, description="查询语言")
    suggestions: List[str] = Field(default_factory=list, description="改进建议")
    risk_factors: List[str] = Field(default_factory=list, description="风险因素")
    enhanced_query: Optional[str] = Field(None, description="增强后的查询")
    should_reject: bool = Field(default=False, description="是否应该拒绝")
    rejection_reason: Optional[str] = Field(None, description="拒绝原因")
    safety_tips: List[str] = Field(default_factory=list, description="安全提示")
    safe_alternatives: List[str] = Field(default_factory=list, description="安全替代建议")


class QueryExecutionPlan(BaseModel):
    """查询执行计划模型"""
    plan_id: str = Field(..., description="计划ID")
    query: str = Field(..., description="查询内容")
    mode: SupportedQueryMode = Field(..., description="查询模式")
    steps: List[Dict[str, Any]] = Field(..., description="执行步骤")
    estimated_time: float = Field(..., description="预估执行时间")
    resource_requirements: Dict[str, Any] = Field(..., description="资源需求")
    optimization_hints: List[str] = Field(default_factory=list, description="优化提示")


class QueryResult(BaseModel):
    """查询结果模型"""
    query_id: str = Field(..., description="查询ID")
    query: str = Field(..., description="原始查询")
    result: str = Field(..., description="查询结果")
    mode: SupportedQueryMode = Field(..., description="查询模式")
    knowledge_base: str = Field(..., description="知识库")
    language: SupportedLanguage = Field(..., description="语言")
    confidence: float = Field(..., description="结果置信度")
    relevance_score: float = Field(..., description="相关性分数")
    context_sources: List[str] = Field(default_factory=list, description="上下文来源")
    retrieved_chunks: List[Dict[str, Any]] = Field(default_factory=list, description="检索到的块")
    entities_used: List[str] = Field(default_factory=list, description="使用的实体")
    relations_used: List[str] = Field(default_factory=list, description="使用的关系")
    response_time: float = Field(..., description="响应时间")
    token_usage: Dict[str, int] = Field(default_factory=dict, description="token使用情况")
    metadata: Optional[Dict[str, Any]] = Field(None, description="结果元数据")


class QueryPerformanceMetrics(BaseModel):
    """查询性能指标模型"""
    query_id: str = Field(..., description="查询ID")
    total_time: float = Field(..., description="总时间")
    retrieval_time: float = Field(..., description="检索时间")
    generation_time: float = Field(..., description="生成时间")
    preprocessing_time: float = Field(..., description="预处理时间")
    postprocessing_time: float = Field(..., description="后处理时间")
    memory_usage: float = Field(..., description="内存使用量")
    cpu_usage: float = Field(..., description="CPU使用率")
    cache_hit_rate: float = Field(..., description="缓存命中率")
    tokens_processed: int = Field(..., description="处理的token数")
    chunks_retrieved: int = Field(..., description="检索的块数")
    entities_processed: int = Field(..., description="处理的实体数")


class QueryFeedback(BaseModel):
    """查询反馈模型"""
    feedback_id: str = Field(..., description="反馈ID")
    query_id: str = Field(..., description="查询ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    rating: int = Field(..., ge=1, le=5, description="评分(1-5)")
    relevance: Optional[int] = Field(None, ge=1, le=5, description="相关性评分")
    accuracy: Optional[int] = Field(None, ge=1, le=5, description="准确性评分")
    completeness: Optional[int] = Field(None, ge=1, le=5, description="完整性评分")
    helpfulness: Optional[int] = Field(None, ge=1, le=5, description="有用性评分")
    comments: Optional[str] = Field(None, description="评论")
    suggestions: Optional[str] = Field(None, description="改进建议")
    created_at: str = Field(..., description="反馈时间")


class QueryTemplate(BaseModel):
    """查询模板模型"""
    template_id: str = Field(..., description="模板ID")
    name: str = Field(..., description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    query_template: str = Field(..., description="查询模板")
    parameters: List[Dict[str, Any]] = Field(default_factory=list, description="参数定义")
    default_mode: SupportedQueryMode = Field(default="hybrid", description="默认查询模式")
    category: Optional[str] = Field(None, description="模板分类")
    tags: List[str] = Field(default_factory=list, description="模板标签")
    usage_count: int = Field(default=0, description="使用次数")
    is_active: bool = Field(default=True, description="是否激活")


class QueryHistory(BaseModel):
    """查询历史模型"""
    history_id: str = Field(..., description="历史ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    query: str = Field(..., description="查询内容")
    result: str = Field(..., description="查询结果")
    mode: SupportedQueryMode = Field(..., description="查询模式")
    knowledge_base: str = Field(..., description="知识库")
    response_time: float = Field(..., description="响应时间")
    success: bool = Field(..., description="是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")
    created_at: str = Field(..., description="查询时间")
    feedback_rating: Optional[int] = Field(None, description="反馈评分")


class QueryStatistics(BaseModel):
    """查询统计模型"""
    total_queries: int = Field(..., description="查询总数")
    successful_queries: int = Field(..., description="成功查询数")
    failed_queries: int = Field(..., description="失败查询数")
    average_response_time: float = Field(..., description="平均响应时间")
    mode_distribution: Dict[str, int] = Field(..., description="模式分布")
    language_distribution: Dict[str, int] = Field(..., description="语言分布")
    knowledge_base_distribution: Dict[str, int] = Field(..., description="知识库分布")
    intent_distribution: Dict[str, int] = Field(..., description="意图分布")
    peak_hours: List[int] = Field(..., description="高峰时段")
    average_rating: Optional[float] = Field(None, description="平均评分")


class QueryOptimization(BaseModel):
    """查询优化模型"""
    optimization_id: str = Field(..., description="优化ID")
    original_query: str = Field(..., description="原始查询")
    optimized_query: str = Field(..., description="优化后查询")
    optimization_type: str = Field(..., description="优化类型")
    improvements: List[str] = Field(..., description="改进点")
    performance_gain: Optional[float] = Field(None, description="性能提升")
    accuracy_gain: Optional[float] = Field(None, description="准确性提升")
    applied_at: str = Field(..., description="应用时间")


class QueryCache(BaseModel):
    """查询缓存模型"""
    cache_key: str = Field(..., description="缓存键")
    query: str = Field(..., description="查询内容")
    result: str = Field(..., description="缓存结果")
    mode: SupportedQueryMode = Field(..., description="查询模式")
    knowledge_base: str = Field(..., description="知识库")
    created_at: str = Field(..., description="创建时间")
    last_accessed: str = Field(..., description="最后访问时间")
    access_count: int = Field(default=1, description="访问次数")
    ttl: int = Field(..., description="生存时间（秒）")
    size: int = Field(..., description="缓存大小（字节）")


class QueryBatch(BaseModel):
    """批量查询模型"""
    batch_id: str = Field(..., description="批次ID")
    queries: List[str] = Field(..., description="查询列表")
    mode: SupportedQueryMode = Field(..., description="查询模式")
    knowledge_base: str = Field(..., description="知识库")
    status: str = Field(..., description="批次状态")
    total_queries: int = Field(..., description="查询总数")
    completed_queries: int = Field(default=0, description="已完成查询数")
    failed_queries: int = Field(default=0, description="失败查询数")
    start_time: str = Field(..., description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
    results: List[QueryResult] = Field(default_factory=list, description="查询结果")





# 导出所有查询相关模型
__all__ = [
    "QueryContext",
    "QueryAnalysisResult",
    "QueryExecutionPlan",
    "QueryResult",
    "QueryPerformanceMetrics",
    "QueryFeedback",
    "QueryTemplate",
    "QueryHistory",
    "QueryStatistics",
    "QueryOptimization",
    "QueryCache",
    "QueryBatch"
]
