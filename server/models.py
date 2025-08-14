"""
FastAPI数据模型定义
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


# 支持的语言类型
SupportedLanguage = Literal["中文", "英文", "English", "Chinese", "zh", "en", "zh-CN", "en-US"]

# 文档插入相关模型
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


class InsertResponse(BaseModel):
    """插入响应"""
    track_id: str = Field(..., description="跟踪ID")
    message: str = Field(default="插入成功", description="响应消息")


# 查询相关模型
class QueryRequest(BaseModel):
    """查询请求"""
    query: str = Field(..., description="查询内容")
    mode: Literal["local", "global", "hybrid", "naive", "mix", "bypass"] = Field(
        default="hybrid",
        description="查询模式"
    )
    top_k: int = Field(default=20, description="返回结果数量")
    stream: bool = Field(default=False, description="是否流式返回")
    only_need_context: bool = Field(default=False, description="是否只返回上下文")
    only_need_prompt: bool = Field(default=False, description="是否只返回提示")
    response_type: str = Field(default="Multiple Paragraphs", description="响应类型")
    max_entity_tokens: Optional[int] = Field(None, description="最大实体token数")
    max_relation_tokens: Optional[int] = Field(None, description="最大关系token数")
    max_total_tokens: Optional[int] = Field(None, description="最大总token数")
    hl_keywords: Optional[List[str]] = Field(default=[], description="高级关键词")
    ll_keywords: Optional[List[str]] = Field(default=[], description="低级关键词")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=[],
        description="对话历史"
    )
    user_prompt: Optional[str] = Field(None, description="用户自定义提示")
    enable_rerank: bool = Field(default=True, description="是否启用重排序")
    knowledge_base: Optional[str] = Field(None, description="知识库名称")
    language: Optional[SupportedLanguage] = Field(None, description="回答语言")


class QueryResponse(BaseModel):
    """查询响应"""
    result: str = Field(..., description="查询结果")
    mode: str = Field(..., description="使用的查询模式")
    query: str = Field(..., description="原始查询")
    knowledge_base: Optional[str] = Field(None, description="使用的知识库")
    language: Optional[str] = Field(None, description="回答语言")


# 知识图谱相关模型
class KnowledgeGraphRequest(BaseModel):
    """知识图谱请求"""
    node_label: str = Field(..., description="节点标签")
    max_depth: int = Field(default=3, description="最大深度")
    max_nodes: Optional[int] = Field(None, description="最大节点数")


class GraphNode(BaseModel):
    """图节点"""
    id: str
    label: str
    properties: Dict[str, Any] = {}


class GraphEdge(BaseModel):
    """图边"""
    source: str
    target: str
    label: str
    properties: Dict[str, Any] = {}


class KnowledgeGraphResponse(BaseModel):
    """知识图谱响应"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    node_count: int
    edge_count: int


# 文件上传相关模型
class FileUploadResponse(BaseModel):
    """文件上传响应"""
    filename: str = Field(..., description="文件名")
    file_path: str = Field(..., description="文件路径")
    file_size: int = Field(..., description="文件大小")
    track_id: str = Field(..., description="处理跟踪ID")
    knowledge_base: Optional[str] = Field(None, description="目标知识库")
    language: Optional[str] = Field(None, description="处理语言")


# 系统状态相关模型
class SystemStatus(BaseModel):
    """系统状态"""
    service_name: str
    version: str
    status: str
    initialized: bool
    working_dir: str
    uptime: float


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "healthy"
    timestamp: str
    system: SystemStatus


# 知识库管理相关模型
class KnowledgeBaseInfo(BaseModel):
    """知识库信息"""
    name: str
    path: str
    created_at: str
    document_count: int
    node_count: int
    edge_count: int
    size_mb: float


class CreateKnowledgeBaseRequest(BaseModel):
    """创建知识库请求"""
    name: str = Field(..., description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")


class SwitchKnowledgeBaseRequest(BaseModel):
    """切换知识库请求"""
    name: str = Field(..., description="要切换到的知识库名称")


# 批量处理相关模型
class BatchInsertRequest(BaseModel):
    """批量插入请求"""
    items: List[InsertTextRequest] = Field(..., description="批量插入项目")
    parallel: bool = Field(default=True, description="是否并行处理")


class BatchQueryRequest(BaseModel):
    """批量查询请求"""
    queries: List[QueryRequest] = Field(..., description="批量查询项目")
    parallel: bool = Field(default=True, description="是否并行处理")


# 导入导出相关模型
class ExportRequest(BaseModel):
    """导出请求"""
    format: Literal["json", "csv", "txt"] = Field(default="json", description="导出格式")
    include_metadata: bool = Field(default=True, description="是否包含元数据")


class ImportRequest(BaseModel):
    """导入请求"""
    format: Literal["json", "csv", "txt"] = Field(..., description="导入格式")
    data: str = Field(..., description="导入数据")
    merge_strategy: Literal["replace", "merge", "skip"] = Field(
        default="merge",
        description="合并策略"
    )


# 语言和知识库管理相关模型
class LanguageRequest(BaseModel):
    """语言设置请求"""
    language: SupportedLanguage = Field(..., description="目标语言")


class LanguageResponse(BaseModel):
    """语言响应"""
    current_language: str = Field(..., description="当前语言")
    supported_languages: List[str] = Field(..., description="支持的语言列表")


class KnowledgeBaseRequest(BaseModel):
    """知识库请求"""
    knowledge_base: str = Field(..., description="知识库名称")
    language: Optional[SupportedLanguage] = Field(None, description="语言设置")


class ServiceConfigResponse(BaseModel):
    """服务配置响应"""
    working_dir: Optional[str] = Field(None, description="当前工作目录")
    knowledge_base: Optional[str] = Field(None, description="当前知识库")
    language: str = Field(..., description="当前语言")
    initialized: bool = Field(..., description="是否已初始化")
    cached_instances: int = Field(..., description="缓存实例数量")


class DirectoryInsertRequest(BaseModel):
    """目录插入请求"""
    directory_path: str = Field(..., description="目录路径")
    knowledge_base: Optional[str] = Field(None, description="知识库名称")
    language: Optional[SupportedLanguage] = Field(None, description="处理语言")


# 配置管理相关模型
class ConfigUpdateRequest(BaseModel):
    """配置更新请求"""
    openai_api_base: Optional[str] = Field(None, description="LLM API基础URL")
    openai_embedding_api_base: Optional[str] = Field(None, description="Embedding API基础URL")
    openai_chat_api_key: Optional[str] = Field(None, description="LLM API密钥")
    openai_embedding_api_key: Optional[str] = Field(None, description="Embedding API密钥")
    openai_chat_model: Optional[str] = Field(None, description="LLM模型名称")
    openai_embedding_model: Optional[str] = Field(None, description="Embedding模型名称")
    embedding_dim: Optional[int] = Field(None, description="Embedding维度")
    max_token_size: Optional[int] = Field(None, description="最大Token数")
    log_level: Optional[str] = Field(None, description="日志级别")
    custom_llm_provider: Optional[str] = Field(None, description="自定义LLM提供商")
    custom_embedding_provider: Optional[str] = Field(None, description="自定义Embedding提供商")
    azure_api_version: Optional[str] = Field(None, description="Azure API版本")
    azure_deployment_name: Optional[str] = Field(None, description="Azure部署名称")


class ConfigResponse(BaseModel):
    """配置响应"""
    updated_fields: List[str] = Field(..., description="已更新的配置字段")
    effective_config: Dict[str, Any] = Field(..., description="当前有效配置")
    restart_required: bool = Field(default=False, description="是否需要重启服务")


# 文件上传相关模型
class FileUploadRequest(BaseModel):
    """文件上传请求"""
    knowledge_base: Optional[str] = Field(None, description="目标知识库名称")
    language: Optional[SupportedLanguage] = Field(None, description="处理语言")
    track_id: Optional[str] = Field(None, description="跟踪ID")


# 知识图谱可视化相关模型
# 查询处理相关模型
class QueryIntentAnalysisRequest(BaseModel):
    """查询意图分析请求"""
    query: str = Field(..., description="查询内容")
    context: Optional[Dict[str, Any]] = Field(None, description="查询上下文（可包含 mode、knowledge_base、language）")
    enable_enhancement: bool = Field(default=True, description="是否启用查询增强")
    safety_check: bool = Field(default=True, description="是否进行安全检查")
    proceed_if_safe: bool = Field(default=False, description="[已弃用] /query/analyze 接口只做分析，不执行查询。如需执行查询请使用 /query/safe 接口")


class QueryIntentAnalysisResponse(BaseModel):
    """查询意图分析响应"""
    original_query: str = Field(..., description="原始查询")
    processed_query: str = Field(..., description="处理后的查询")
    intent_type: str = Field(..., description="意图类型")
    safety_level: str = Field(..., description="安全级别")
    confidence: float = Field(..., description="置信度")
    suggestions: List[str] = Field(default_factory=list, description="改进建议（通常为正向建议）")
    risk_factors: List[str] = Field(default_factory=list, description="风险因素")
    enhanced_query: Optional[str] = Field(None, description="增强后的查询（仅在安全时提供）")
    should_reject: bool = Field(default=False, description="是否应该拒绝")
    rejection_reason: Optional[str] = Field(None, description="拒绝原因")
    safety_tips: List[str] = Field(default_factory=list, description="安全与合规提示")
    safe_alternatives: List[str] = Field(default_factory=list, description="建议改写（正向、安全）")


class SafeQueryRequest(BaseModel):
    """安全查询请求"""
    query: str = Field(..., description="查询内容")
    # 使用字符串作为查询模式，避免将模式写死为枚举，保持与 /query/modes 动态能力一致
    mode: Optional[str] = Field(default="hybrid", description="查询模式")
    knowledge_base: Optional[str] = Field(None, description="知识库名称")
    language: Optional[SupportedLanguage] = Field(None, description="查询语言")
    enable_intent_analysis: bool = Field(default=True, description="是否启用意图分析")
    enable_query_enhancement: bool = Field(default=True, description="是否启用查询增强")
    safety_check: bool = Field(default=True, description="是否进行安全检查")


class GraphVisualizationRequest(BaseModel):
    """知识图谱可视化请求"""
    knowledge_base: Optional[str] = Field(None, description="知识库名称")
    max_nodes: Optional[int] = Field(default=100, description="最大显示节点数")
    layout: Optional[str] = Field(default="spring", description="布局算法")
    node_size_field: Optional[str] = Field(default="degree", description="节点大小字段")
    edge_width_field: Optional[str] = Field(default="weight", description="边宽度字段")


class GraphVisualizationResponse(BaseModel):
    """知识图谱可视化响应"""
    html_content: str = Field(..., description="可视化HTML内容")
    html_file_path: str = Field(..., description="HTML文件保存路径")
    node_count: int = Field(..., description="节点数量")
    edge_count: int = Field(..., description="边数量")
    knowledge_base: str = Field(..., description="知识库名称")
    graph_file_exists: bool = Field(..., description="图谱文件是否存在")
    json_file_exists: bool = Field(..., description="JSON文件是否存在")


class GraphDataRequest(BaseModel):
    """图谱数据请求"""
    knowledge_base: Optional[str] = Field(None, description="知识库名称")
    format: Literal["json", "graphml"] = Field(default="json", description="数据格式")


class GraphDataResponse(BaseModel):
    """图谱数据响应"""
    nodes: List[Dict[str, Any]] = Field(..., description="节点数据")
    edges: List[Dict[str, Any]] = Field(..., description="边数据")
    node_count: int = Field(..., description="节点数量")
    edge_count: int = Field(..., description="边数量")
    knowledge_base: str = Field(..., description="知识库名称")
    data_source: str = Field(..., description="数据来源文件")


class GraphStatusResponse(BaseModel):
    """图谱状态响应"""
    knowledge_base: str = Field(..., description="知识库名称")
    working_dir: str = Field(..., description="工作目录")
    xml_file_exists: bool = Field(..., description="XML文件是否存在")
    xml_file_size: int = Field(..., description="XML文件大小")
    json_file_exists: bool = Field(..., description="JSON文件是否存在")
    json_file_size: int = Field(..., description="JSON文件大小")
    last_xml_modified: Optional[float] = Field(None, description="XML文件最后修改时间")
    last_json_modified: Optional[float] = Field(None, description="JSON文件最后修改时间")
    status: str = Field(..., description="状态描述")
