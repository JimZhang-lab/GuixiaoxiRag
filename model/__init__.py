"""
数据模型包
统一导出所有数据模型
"""

# 基础模型
from .base_models import (
    BaseResponse,
    ErrorResponse,
    PaginationModel,
    TimestampModel,
    MetadataModel,
    HealthCheckModel,
    ConfigModel,
    ValidationError,
    OperationResult,
    ProgressModel,
    ResourceUsageModel,
    PerformanceMetrics,
    CacheInfo,
    BatchOperation,
    APIEndpointInfo,
    ServiceInfo,
    # 类型定义
    SupportedLanguage,
    SupportedQueryMode,
    SupportedFileFormat,
    SafetyLevel,
    IntentType,
    ResponseType,
    PerformanceMode,
    SystemStatusType
)

# 请求模型
from .request_models import (
    # 文档管理
    InsertTextRequest,
    InsertTextsRequest,
    DirectoryInsertRequest,
    FileUploadRequest,
    # 查询相关
    QueryRequest,
    BatchQueryRequest,
    QueryIntentAnalysisRequest,
    SafeQueryRequest,
    # 知识图谱
    KnowledgeGraphRequest,
    GraphVisualizationRequest,
    GraphDataRequest,
    # 知识库管理
    CreateKnowledgeBaseRequest,
    SwitchKnowledgeBaseRequest,
    KnowledgeBaseConfigRequest,
    # 系统管理
    ConfigUpdateRequest,
    PerformanceConfigRequest,
    SystemResetRequest,
    # 批量操作
    BatchInsertRequest,
    # 导入导出
    ExportRequest,
    ImportRequest,
    # 监控
    MetricsRequest
)

# 响应模型
from .response_models import (
    # 文档管理
    InsertResponse,
    FileUploadResponse,
    BatchFileUploadResponse,
    # 查询相关
    QueryResponse,
    BatchQueryResponse,
    QueryIntentAnalysisResponse,
    SafeQueryResponse,
    # 知识图谱
    GraphNode,
    GraphEdge,
    KnowledgeGraphResponse,
    GraphVisualizationResponse,
    GraphDataResponse,
    GraphStatusResponse,
    # 知识库管理
    KnowledgeBaseInfo,
    KnowledgeBaseListResponse,
    # 系统管理
    SystemStatus,
    HealthResponse,
    ConfigResponse,
    ServiceConfigResponse,
    # 监控
    MetricsResponse,
    PerformanceStatsResponse,
    # 批量操作
    BatchOperationResponse,
    # 导入导出
    ExportResponse,
    ImportResponse
)

# 文档相关模型
from .document_models import (
    DocumentInfo,
    DocumentChunk,
    DocumentProcessingStatus,
    DocumentStatistics,
    DocumentSearchResult,
    DocumentVersion,
    DocumentTemplate,
    DocumentAnnotation,
    DocumentRelation,
    DocumentCollection,
    DocumentProcessingConfig,
    DocumentQualityMetrics,
    DocumentBackup
)

# 查询相关模型
from .query_models import (
    QueryContext,
    QueryAnalysisResult,
    QueryExecutionPlan,
    QueryResult,
    QueryPerformanceMetrics,
    QueryFeedback,
    QueryTemplate,
    QueryHistory,
    QueryStatistics,
    QueryOptimization,
    QueryCache,
    QueryBatch
)

# 系统相关模型
from .system_models import (
    SystemConfiguration,
    SystemHealth,
    SystemMetrics,
    SystemAlert,
    SystemLog,
    SystemBackup,
    SystemMaintenance,
    SystemAudit,
    SystemCapacity,
    SystemPerformance,
    SystemDependency,
    SystemEnvironment
)

# 导出所有模型
__all__ = [
    # 基础模型
    "BaseResponse",
    "ErrorResponse",
    "PaginationModel",
    "TimestampModel",
    "MetadataModel",
    "HealthCheckModel",
    "ConfigModel",
    "ValidationError",
    "OperationResult",
    "ProgressModel",
    "ResourceUsageModel",
    "PerformanceMetrics",
    "CacheInfo",
    "BatchOperation",
    "APIEndpointInfo",
    "ServiceInfo",

    # 类型定义
    "SupportedLanguage",
    "SupportedQueryMode",
    "SupportedFileFormat",
    "SafetyLevel",
    "IntentType",
    "ResponseType",
    "PerformanceMode",
    "SystemStatusType",

    # 请求模型
    "InsertTextRequest",
    "InsertTextsRequest",
    "DirectoryInsertRequest",
    "FileUploadRequest",
    "QueryRequest",
    "BatchQueryRequest",
    "QueryIntentAnalysisRequest",
    "SafeQueryRequest",
    "KnowledgeGraphRequest",
    "GraphVisualizationRequest",
    "GraphDataRequest",
    "CreateKnowledgeBaseRequest",
    "SwitchKnowledgeBaseRequest",
    "KnowledgeBaseConfigRequest",
    "ConfigUpdateRequest",
    "PerformanceConfigRequest",
    "SystemResetRequest",
    "BatchInsertRequest",
    "ExportRequest",
    "ImportRequest",
    "MetricsRequest",

    # 响应模型
    "InsertResponse",
    "FileUploadResponse",
    "BatchFileUploadResponse",
    "QueryResponse",
    "BatchQueryResponse",
    "QueryIntentAnalysisResponse",
    "SafeQueryResponse",
    "GraphNode",
    "GraphEdge",
    "KnowledgeGraphResponse",
    "GraphVisualizationResponse",
    "GraphDataResponse",
    "GraphStatusResponse",
    "KnowledgeBaseInfo",
    "KnowledgeBaseListResponse",
    "SystemStatus",
    "HealthResponse",
    "ConfigResponse",
    "ServiceConfigResponse",
    "MetricsResponse",
    "PerformanceStatsResponse",
    "BatchOperationResponse",
    "ExportResponse",
    "ImportResponse",

    # 文档相关模型
    "DocumentInfo",
    "DocumentChunk",
    "DocumentProcessingStatus",
    "DocumentStatistics",
    "DocumentSearchResult",
    "DocumentVersion",
    "DocumentTemplate",
    "DocumentAnnotation",
    "DocumentRelation",
    "DocumentCollection",
    "DocumentProcessingConfig",
    "DocumentQualityMetrics",
    "DocumentBackup",

    # 查询相关模型
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
    "QueryBatch",

    # 系统相关模型
    "SystemConfiguration",
    "SystemHealth",
    "SystemMetrics",
    "SystemAlert",
    "SystemLog",
    "SystemBackup",
    "SystemMaintenance",
    "SystemAudit",
    "SystemCapacity",
    "SystemPerformance",
    "SystemDependency",
    "SystemEnvironment"
]