"""
响应数据模型定义
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .base_models import (
    BaseResponse, SystemStatusType, SafetyLevel, IntentType,
    PerformanceMetrics, CacheInfo, BatchOperation
)


# 文档管理相关响应模型
class InsertResponse(BaseModel):
    """插入响应"""
    track_id: str = Field(..., description="跟踪ID")
    message: str = Field(default="插入成功", description="响应消息")
    processed_count: Optional[int] = Field(None, description="处理数量")
    duration: Optional[float] = Field(None, description="处理时间（秒）")


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    filename: str = Field(..., description="文件名")
    file_path: str = Field(..., description="文件路径")
    file_size: int = Field(..., description="文件大小")
    track_id: str = Field(..., description="处理跟踪ID")
    knowledge_base: Optional[str] = Field(None, description="目标知识库")
    language: Optional[str] = Field(None, description="处理语言")
    file_type: Optional[str] = Field(None, description="文件类型")
    metadata: Optional[Dict[str, Any]] = Field(None, description="文件元数据")


class BatchFileUploadResponse(BaseModel):
    """批量文件上传响应"""
    track_id: str = Field(..., description="批次跟踪ID")
    files: List[FileUploadResponse] = Field(..., description="文件列表")
    total_files: int = Field(..., description="文件总数")
    successful_files: int = Field(..., description="成功处理的文件数")
    failed_files: int = Field(..., description="失败的文件数")
    total_size: int = Field(..., description="总文件大小")


# 查询相关响应模型
class QueryResponse(BaseModel):
    """查询响应"""
    result: str = Field(..., description="查询结果")
    mode: str = Field(..., description="使用的查询模式")
    query: str = Field(..., description="原始查询")
    knowledge_base: Optional[str] = Field(None, description="使用的知识库")
    language: Optional[str] = Field(None, description="回答语言")
    context_sources: Optional[List[str]] = Field(None, description="上下文来源")
    confidence: Optional[float] = Field(None, description="置信度")
    response_time: Optional[float] = Field(None, description="响应时间（秒）")


class BatchQueryResponse(BaseModel):
    """批量查询响应"""
    results: List[QueryResponse] = Field(..., description="查询结果列表")
    total_queries: int = Field(..., description="查询总数")
    successful_queries: int = Field(..., description="成功查询数")
    failed_queries: int = Field(..., description="失败查询数")
    mode: str = Field(..., description="使用的查询模式")
    total_time: float = Field(..., description="总处理时间（秒）")


class QueryIntentAnalysisResponse(BaseModel):
    """查询意图分析响应"""
    original_query: str = Field(..., description="原始查询")
    processed_query: str = Field(..., description="处理后的查询")
    intent_type: str = Field(..., description="意图类型")
    safety_level: str = Field(..., description="安全级别")
    confidence: float = Field(..., description="置信度")
    suggestions: List[str] = Field(default_factory=list, description="改进建议")
    risk_factors: List[str] = Field(default_factory=list, description="风险因素")
    enhanced_query: Optional[str] = Field(None, description="增强后的查询")
    should_reject: bool = Field(default=False, description="是否应该拒绝")
    rejection_reason: Optional[str] = Field(None, description="拒绝原因")
    safety_tips: List[str] = Field(default_factory=list, description="安全提示")
    safe_alternatives: List[str] = Field(default_factory=list, description="安全替代建议")


class SafeQueryResponse(BaseModel):
    """安全查询响应"""
    query_analysis: Optional[QueryIntentAnalysisResponse] = Field(None, description="查询分析结果")
    query_result: Optional[QueryResponse] = Field(None, description="查询结果")
    safety_passed: bool = Field(..., description="是否通过安全检查")
    processing_time: float = Field(..., description="处理时间（秒）")


# 知识图谱相关响应模型
class GraphNode(BaseModel):
    """图节点"""
    id: str = Field(..., description="节点ID")
    label: str = Field(..., description="节点标签")
    properties: Dict[str, Any] = Field(default_factory=dict, description="节点属性")
    degree: Optional[int] = Field(None, description="节点度数")
    centrality: Optional[float] = Field(None, description="中心性")


class GraphEdge(BaseModel):
    """图边"""
    source: str = Field(..., description="源节点ID")
    target: str = Field(..., description="目标节点ID")
    label: str = Field(..., description="边标签")
    properties: Dict[str, Any] = Field(default_factory=dict, description="边属性")
    weight: Optional[float] = Field(None, description="边权重")


class KnowledgeGraphResponse(BaseModel):
    """知识图谱响应"""
    nodes: List[GraphNode] = Field(..., description="节点列表")
    edges: List[GraphEdge] = Field(..., description="边列表")
    node_count: int = Field(..., description="节点数量")
    edge_count: int = Field(..., description="边数量")
    metadata: Optional[Dict[str, Any]] = Field(None, description="图谱元数据")
    statistics: Optional[Dict[str, Any]] = Field(None, description="图谱统计信息")


class GraphVisualizationResponse(BaseModel):
    """知识图谱可视化响应"""
    html_content: str = Field(..., description="可视化HTML内容")
    html_file_path: str = Field(..., description="HTML文件保存路径")
    node_count: int = Field(..., description="节点数量")
    edge_count: int = Field(..., description="边数量")
    knowledge_base: str = Field(..., description="知识库名称")
    graph_file_exists: bool = Field(..., description="图谱文件是否存在")
    json_file_exists: bool = Field(..., description="JSON文件是否存在")
    layout_algorithm: str = Field(..., description="使用的布局算法")


class GraphDataResponse(BaseModel):
    """图谱数据响应"""
    nodes: List[Dict[str, Any]] = Field(..., description="节点数据")
    edges: List[Dict[str, Any]] = Field(..., description="边数据")
    node_count: int = Field(..., description="节点数量")
    edge_count: int = Field(..., description="边数量")
    knowledge_base: str = Field(..., description="知识库名称")
    data_source: str = Field(..., description="数据来源文件")
    format: str = Field(..., description="数据格式")
    file_size: int = Field(..., description="数据文件大小")


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


# 知识库管理相关响应模型
class KnowledgeBaseInfo(BaseModel):
    """知识库信息"""
    name: str = Field(..., description="知识库名称")
    path: str = Field(..., description="知识库路径")
    created_at: str = Field(..., description="创建时间")
    document_count: int = Field(..., description="文档数量")
    node_count: int = Field(..., description="节点数量")
    edge_count: int = Field(..., description="边数量")
    size_mb: float = Field(..., description="大小（MB）")
    language: Optional[str] = Field(None, description="默认语言")
    description: Optional[str] = Field(None, description="描述")
    status: str = Field(..., description="状态")


class KnowledgeBaseListResponse(BaseModel):
    """知识库列表响应"""
    knowledge_bases: List[KnowledgeBaseInfo] = Field(..., description="知识库列表")
    total_count: int = Field(..., description="总数量")
    current_kb: Optional[str] = Field(None, description="当前知识库")


# 系统管理相关响应模型
class SystemStatus(BaseModel):
    """系统状态"""
    service_name: str = Field(..., description="服务名称")
    version: str = Field(..., description="版本号")
    status: SystemStatusType = Field(..., description="状态")
    initialized: bool = Field(..., description="是否已初始化")
    working_dir: str = Field(..., description="工作目录")
    uptime: float = Field(..., description="运行时间（秒）")
    performance: Optional[PerformanceMetrics] = Field(None, description="性能指标")
    cache_info: Optional[CacheInfo] = Field(None, description="缓存信息")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(default="healthy", description="健康状态")
    timestamp: str = Field(..., description="检查时间")
    system: SystemStatus = Field(..., description="系统状态")
    dependencies: Optional[Dict[str, str]] = Field(None, description="依赖服务状态")


class ConfigResponse(BaseModel):
    """配置响应"""
    updated_fields: List[str] = Field(..., description="已更新的配置字段")
    effective_config: Dict[str, Any] = Field(..., description="当前有效配置")
    restart_required: bool = Field(default=False, description="是否需要重启服务")
    validation_errors: List[str] = Field(default_factory=list, description="验证错误")


class ServiceConfigResponse(BaseModel):
    """服务配置响应"""
    working_dir: Optional[str] = Field(None, description="当前工作目录")
    knowledge_base: Optional[str] = Field(None, description="当前知识库")
    language: str = Field(..., description="当前语言")
    initialized: bool = Field(..., description="是否已初始化")
    cached_instances: int = Field(..., description="缓存实例数量")
    performance_mode: str = Field(..., description="性能模式")


# 监控相关响应模型
class MetricsResponse(BaseModel):
    """指标响应"""
    metrics: Dict[str, Any] = Field(..., description="指标数据")
    time_range: Dict[str, str] = Field(..., description="时间范围")
    granularity: str = Field(..., description="时间粒度")
    total_points: int = Field(..., description="数据点总数")


class PerformanceStatsResponse(BaseModel):
    """性能统计响应"""
    request_count: int = Field(..., description="请求总数")
    average_response_time: float = Field(..., description="平均响应时间")
    error_rate: float = Field(..., description="错误率")
    throughput: float = Field(..., description="吞吐量")
    resource_usage: Dict[str, float] = Field(..., description="资源使用情况")
    cache_stats: CacheInfo = Field(..., description="缓存统计")


# 批量操作响应模型
class BatchOperationResponse(BaseModel):
    """批量操作响应"""
    batch_info: BatchOperation = Field(..., description="批次信息")
    results: List[Dict[str, Any]] = Field(..., description="操作结果")
    summary: Dict[str, int] = Field(..., description="结果摘要")


# 导入导出响应模型
class ExportResponse(BaseModel):
    """导出响应"""
    file_path: str = Field(..., description="导出文件路径")
    file_size: int = Field(..., description="文件大小")
    format: str = Field(..., description="导出格式")
    record_count: int = Field(..., description="记录数量")
    export_time: float = Field(..., description="导出时间（秒）")


class ImportResponse(BaseModel):
    """导入响应"""
    imported_records: int = Field(..., description="导入记录数")
    skipped_records: int = Field(..., description="跳过记录数")
    error_records: int = Field(..., description="错误记录数")
    import_time: float = Field(..., description="导入时间（秒）")
    validation_errors: List[str] = Field(default_factory=list, description="验证错误")


# 导出所有响应模型
__all__ = [
    # 文档管理
    "InsertResponse",
    "FileUploadResponse",
    "BatchFileUploadResponse",
    
    # 查询相关
    "QueryResponse",
    "BatchQueryResponse", 
    "QueryIntentAnalysisResponse",
    "SafeQueryResponse",
    
    # 知识图谱
    "GraphNode",
    "GraphEdge",
    "KnowledgeGraphResponse",
    "GraphVisualizationResponse",
    "GraphDataResponse",
    "GraphStatusResponse",
    
    # 知识库管理
    "KnowledgeBaseInfo",
    "KnowledgeBaseListResponse",
    
    # 系统管理
    "SystemStatus",
    "HealthResponse",
    "ConfigResponse",
    "ServiceConfigResponse",
    
    # 监控
    "MetricsResponse",
    "PerformanceStatsResponse",
    
    # 批量操作
    "BatchOperationResponse",
    
    # 导入导出
    "ExportResponse",
    "ImportResponse",

    # 意图识别
    "IntentAnalysisResponse",
    "SafetyCheckResponse",
    "ProcessorStatusResponse"
]


# 意图识别相关响应模型
class IntentAnalysisResponse(BaseModel):
    """意图分析响应模型"""
    success: bool = Field(description="是否成功")
    data: Optional[Dict[str, Any]] = Field(default=None, description="分析结果")
    message: Optional[str] = Field(default=None, description="响应消息")
    processing_time: float = Field(description="处理时间（秒）")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "original_query": "介绍一下人工智能",
                    "processed_query": "介绍一下人工智能",
                    "intent_type": "knowledge_query",
                    "safety_level": "safe",
                    "confidence": 0.95,
                    "suggestions": ["可以询问具体的AI应用领域"],
                    "enhanced_query": "请详细介绍人工智能的概念、发展历史和主要应用领域",
                    "should_reject": False
                },
                "message": "意图分析完成",
                "processing_time": 0.5
            }
        }


class SafetyCheckResponse(BaseModel):
    """安全检查响应模型"""
    success: bool = Field(description="是否成功")
    data: Optional[Dict[str, Any]] = Field(default=None, description="检查结果")
    message: Optional[str] = Field(default=None, description="响应消息")
    processing_time: float = Field(description="处理时间（秒）")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "is_safe": True,
                    "safety_level": "safe",
                    "risk_factors": [],
                    "confidence": 0.95,
                    "reason": "内容安全，无风险因素"
                },
                "message": "安全检查完成",
                "processing_time": 0.2
            }
        }


class ProcessorStatusResponse(BaseModel):
    """处理器状态响应模型"""
    success: bool = Field(description="是否成功")
    data: Optional[Dict[str, Any]] = Field(default=None, description="状态信息")
    message: Optional[str] = Field(default=None, description="响应消息")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "processor_status": "healthy",
                    "dfa_filter_loaded": True,
                    "llm_available": True,
                    "config": {
                        "confidence_threshold": 0.7,
                        "enable_llm": True,
                        "enable_dfa_filter": True,
                        "enable_query_enhancement": True
                    }
                },
                "message": "处理器状态正常"
            }
        }
