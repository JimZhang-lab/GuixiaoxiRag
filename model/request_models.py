"""
请求数据模型定义
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .base_models import (
    SupportedLanguage, SupportedQueryMode, SupportedFileFormat,
    ResponseType, PerformanceMode
)


# 文档管理相关请求模型
class InsertTextRequest(BaseModel):
    """插入文本请求"""
    text: str = Field(..., description="要插入的文本内容")
    doc_id: Optional[str] = Field(None, description="文档ID")
    file_path: Optional[str] = Field(None, description="文件路径")
    track_id: Optional[str] = Field(None, description="跟踪ID")
    working_dir: Optional[str] = Field(None, description="自定义知识库路径")
    knowledge_base: Optional[str] = Field(None, description="知识库名称")
    language: Optional[SupportedLanguage] = Field(None, description="处理语言")


class InsertTextsRequest(BaseModel):
    """批量插入文本请求"""
    texts: List[str] = Field(..., description="要插入的文本列表")
    doc_ids: Optional[List[str]] = Field(None, description="文档ID列表")
    file_paths: Optional[List[str]] = Field(None, description="文件路径列表")
    track_id: Optional[str] = Field(None, description="跟踪ID")
    knowledge_base: Optional[str] = Field(None, description="知识库名称")
    language: Optional[SupportedLanguage] = Field(None, description="处理语言")


class DirectoryInsertRequest(BaseModel):
    """目录插入请求"""
    directory_path: str = Field(..., description="目录路径")
    knowledge_base: Optional[str] = Field(None, description="知识库名称")
    language: Optional[SupportedLanguage] = Field(None, description="处理语言")
    recursive: bool = Field(default=True, description="是否递归处理子目录")
    file_patterns: Optional[List[str]] = Field(None, description="文件匹配模式")


class FileUploadRequest(BaseModel):
    """文件上传请求"""
    knowledge_base: Optional[str] = Field(None, description="目标知识库名称")
    language: Optional[SupportedLanguage] = Field(None, description="处理语言")
    track_id: Optional[str] = Field(None, description="跟踪ID")
    extract_metadata: bool = Field(default=True, description="是否提取元数据")


# 查询相关请求模型
class QueryRequest(BaseModel):
    """查询请求"""
    query: str = Field(..., description="查询内容")
    mode: SupportedQueryMode = Field(default="hybrid", description="查询模式")
    top_k: int = Field(default=20, ge=1, le=100, description="返回结果数量")
    stream: bool = Field(default=False, description="是否流式返回")
    only_need_context: bool = Field(default=False, description="是否只返回上下文")
    only_need_prompt: bool = Field(default=False, description="是否只返回提示")
    response_type: ResponseType = Field(default="Multiple Paragraphs", description="响应类型")
    max_entity_tokens: Optional[int] = Field(None, ge=100, le=10000, description="最大实体token数")
    max_relation_tokens: Optional[int] = Field(None, ge=100, le=10000, description="最大关系token数")
    max_total_tokens: Optional[int] = Field(None, ge=500, le=20000, description="最大总token数")
    hl_keywords: List[str] = Field(default_factory=list, description="高级关键词")
    ll_keywords: List[str] = Field(default_factory=list, description="低级关键词")
    conversation_history: List[Dict[str, str]] = Field(default_factory=list, description="对话历史")
    user_prompt: Optional[str] = Field(None, description="用户自定义提示")
    enable_rerank: bool = Field(default=True, description="是否启用重排序")
    knowledge_base: Optional[str] = Field(None, description="知识库名称")
    language: Optional[SupportedLanguage] = Field(None, description="回答语言")
    performance_mode: PerformanceMode = Field(default="balanced", description="性能模式")


class BatchQueryRequest(BaseModel):
    """批量查询请求"""
    queries: List[str] = Field(..., min_items=1, max_items=50, description="查询列表")
    mode: SupportedQueryMode = Field(default="hybrid", description="查询模式")
    top_k: int = Field(default=20, ge=1, le=100, description="每个查询返回的结果数量")
    knowledge_base: Optional[str] = Field(None, description="知识库名称")
    language: Optional[SupportedLanguage] = Field(None, description="回答语言")
    parallel: bool = Field(default=True, description="是否并行处理")
    timeout: int = Field(default=300, ge=30, le=600, description="超时时间（秒）")


class QueryIntentAnalysisRequest(BaseModel):
    """查询意图分析请求"""
    query: str = Field(..., description="查询内容")
    context: Optional[Dict[str, Any]] = Field(None, description="查询上下文")
    enable_enhancement: bool = Field(default=True, description="是否启用查询增强")
    safety_check: bool = Field(default=True, description="是否进行安全检查")


class SafeQueryRequest(BaseModel):
    """安全查询请求"""
    query: str = Field(..., description="查询内容")
    mode: Optional[str] = Field(default="hybrid", description="查询模式")
    knowledge_base: Optional[str] = Field(None, description="知识库名称")
    language: Optional[SupportedLanguage] = Field(None, description="查询语言")
    enable_intent_analysis: bool = Field(default=True, description="是否启用意图分析")
    enable_query_enhancement: bool = Field(default=True, description="是否启用查询增强")
    safety_check: bool = Field(default=True, description="是否进行安全检查")


# 知识图谱相关请求模型
class KnowledgeGraphRequest(BaseModel):
    """知识图谱请求"""
    node_label: str = Field(..., description="节点标签")
    max_depth: int = Field(default=3, ge=1, le=10, description="最大深度")
    max_nodes: Optional[int] = Field(None, ge=10, le=5000, description="最大节点数")
    include_metadata: bool = Field(default=True, description="是否包含元数据")


class GraphVisualizationRequest(BaseModel):
    """知识图谱可视化请求"""
    knowledge_base: Optional[str] = Field(None, description="知识库名称")
    max_nodes: int = Field(default=100, ge=10, le=1000, description="最大显示节点数")
    layout: str = Field(default="spring", description="布局算法")
    node_size_field: str = Field(default="degree", description="节点大小字段")
    edge_width_field: str = Field(default="weight", description="边宽度字段")
    filter_nodes: Optional[List[str]] = Field(None, description="节点过滤条件")
    filter_edges: Optional[List[str]] = Field(None, description="边过滤条件")


class GraphDataRequest(BaseModel):
    """图谱数据请求"""
    knowledge_base: Optional[str] = Field(None, description="知识库名称")
    format: SupportedFileFormat = Field(default="json", description="数据格式")
    include_metadata: bool = Field(default=True, description="是否包含元数据")
    compress: bool = Field(default=False, description="是否压缩数据")


# 知识库管理相关请求模型
class CreateKnowledgeBaseRequest(BaseModel):
    """创建知识库请求"""
    name: str = Field(..., min_length=1, max_length=100, description="知识库名称")
    description: Optional[str] = Field(None, max_length=500, description="知识库描述")
    language: SupportedLanguage = Field(default="中文", description="默认语言")
    config: Optional[Dict[str, Any]] = Field(None, description="自定义配置")


class SwitchKnowledgeBaseRequest(BaseModel):
    """切换知识库请求"""
    name: str = Field(..., description="要切换到的知识库名称")
    create_if_not_exists: bool = Field(default=False, description="如果不存在是否创建")


class KnowledgeBaseConfigRequest(BaseModel):
    """知识库配置请求"""
    knowledge_base: str = Field(..., description="知识库名称")
    config: Dict[str, Any] = Field(..., description="配置参数")


# 系统管理相关请求模型
class ConfigUpdateRequest(BaseModel):
    """配置更新请求"""
    openai_api_base: Optional[str] = Field(None, description="LLM API基础URL")
    openai_embedding_api_base: Optional[str] = Field(None, description="Embedding API基础URL")
    openai_chat_api_key: Optional[str] = Field(None, description="LLM API密钥")
    openai_embedding_api_key: Optional[str] = Field(None, description="Embedding API密钥")
    openai_chat_model: Optional[str] = Field(None, description="LLM模型名称")
    openai_embedding_model: Optional[str] = Field(None, description="Embedding模型名称")
    embedding_dim: Optional[int] = Field(None, ge=128, le=4096, description="Embedding维度")
    max_token_size: Optional[int] = Field(None, ge=1024, le=32768, description="最大Token数")
    log_level: Optional[str] = Field(None, description="日志级别")
    custom_llm_provider: Optional[str] = Field(None, description="自定义LLM提供商")
    custom_embedding_provider: Optional[str] = Field(None, description="自定义Embedding提供商")
    azure_api_version: Optional[str] = Field(None, description="Azure API版本")
    azure_deployment_name: Optional[str] = Field(None, description="Azure部署名称")


class PerformanceConfigRequest(BaseModel):
    """性能配置请求"""
    mode: PerformanceMode = Field(..., description="性能模式")
    custom_config: Optional[Dict[str, Any]] = Field(None, description="自定义配置")


class SystemResetRequest(BaseModel):
    """系统重置请求"""
    confirm: bool = Field(..., description="确认重置")
    backup_data: bool = Field(default=True, description="是否备份数据")
    reset_config: bool = Field(default=False, description="是否重置配置")


# 批量操作相关请求模型
class BatchInsertRequest(BaseModel):
    """批量插入请求"""
    items: List[InsertTextRequest] = Field(..., min_items=1, max_items=100, description="批量插入项目")
    parallel: bool = Field(default=True, description="是否并行处理")
    batch_size: int = Field(default=10, ge=1, le=50, description="批次大小")


# 导入导出相关请求模型
class ExportRequest(BaseModel):
    """导出请求"""
    knowledge_base: Optional[str] = Field(None, description="知识库名称")
    format: SupportedFileFormat = Field(default="json", description="导出格式")
    include_metadata: bool = Field(default=True, description="是否包含元数据")
    include_vectors: bool = Field(default=False, description="是否包含向量数据")
    compress: bool = Field(default=True, description="是否压缩")


class ImportRequest(BaseModel):
    """导入请求"""
    knowledge_base: str = Field(..., description="目标知识库")
    format: SupportedFileFormat = Field(..., description="导入格式")
    data: str = Field(..., description="导入数据")
    merge_strategy: str = Field(default="merge", description="合并策略")
    validate_data: bool = Field(default=True, description="是否验证数据")


# 监控相关请求模型
class MetricsRequest(BaseModel):
    """指标请求"""
    start_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
    metrics: List[str] = Field(default_factory=list, description="指标名称列表")
    granularity: str = Field(default="minute", description="时间粒度")


# 意图识别相关请求模型
class IntentAnalysisRequest(BaseModel):
    """意图分析请求模型"""
    query: str = Field(description="查询内容", min_length=1, max_length=2000)
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文信息")
    enable_enhancement: bool = Field(default=True, description="是否启用查询增强")
    enable_safety_check: bool = Field(default=True, description="是否启用安全检查")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "介绍一下人工智能的发展历史",
                "context": {"user_id": "123", "session_id": "abc"},
                "enable_enhancement": True,
                "enable_safety_check": True
            }
        }


class SafetyCheckRequest(BaseModel):
    """安全检查请求模型"""
    content: str = Field(description="待检查内容", min_length=1, max_length=2000)
    check_type: str = Field(default="comprehensive", description="检查类型")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "如何学习编程",
                "check_type": "comprehensive"
            }
        }


# 导出所有请求模型
__all__ = [
    # 文档管理
    "InsertTextRequest",
    "InsertTextsRequest", 
    "DirectoryInsertRequest",
    "FileUploadRequest",
    
    # 查询相关
    "QueryRequest",
    "BatchQueryRequest",
    "QueryIntentAnalysisRequest",
    "SafeQueryRequest",
    
    # 知识图谱
    "KnowledgeGraphRequest",
    "GraphVisualizationRequest",
    "GraphDataRequest",
    
    # 知识库管理
    "CreateKnowledgeBaseRequest",
    "SwitchKnowledgeBaseRequest",
    "KnowledgeBaseConfigRequest",
    
    # 系统管理
    "ConfigUpdateRequest",
    "PerformanceConfigRequest",
    "SystemResetRequest",
    
    # 批量操作
    "BatchInsertRequest",
    
    # 导入导出
    "ExportRequest",
    "ImportRequest",
    
    # 监控
    "MetricsRequest",

    # 意图识别
    "IntentAnalysisRequest",
    "SafetyCheckRequest"
]