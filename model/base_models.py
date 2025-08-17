"""
基础数据模型定义
"""
from typing import Any, Optional, Dict, List, Literal
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


class PaginationModel(BaseModel):
    """分页模型"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页大小")
    total: Optional[int] = Field(None, description="总数量")
    total_pages: Optional[int] = Field(None, description="总页数")


class TimestampModel(BaseModel):
    """时间戳模型"""
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")


class MetadataModel(BaseModel):
    """元数据模型"""
    version: str = Field(default="1.0", description="版本号")
    source: Optional[str] = Field(None, description="数据来源")
    tags: List[str] = Field(default_factory=list, description="标签")
    extra: Dict[str, Any] = Field(default_factory=dict, description="额外信息")


# 支持的语言类型
SupportedLanguage = Literal[
    "中文", "英文", "English", "Chinese", 
    "zh", "en", "zh-CN", "en-US"
]

# 支持的查询模式
SupportedQueryMode = Literal[
    "local", "global", "hybrid", "naive", "mix", "bypass"
]

# 支持的文件格式
SupportedFileFormat = Literal[
    "json", "csv", "txt", "xml", "pdf", "docx", "md"
]

# 安全级别
SafetyLevel = Literal["safe", "suspicious", "unsafe", "illegal"]

# 意图类型
IntentType = Literal[
    "knowledge_query", "factual_question", "analytical_question",
    "procedural_question", "creative_request", "greeting", 
    "unclear", "illegal_content"
]

# 响应类型
ResponseType = Literal[
    "Multiple Paragraphs", "Single Paragraph", "Single Sentence",
    "List of Points", "JSON Format"
]

# 性能模式
PerformanceMode = Literal["fast", "balanced", "quality"]

# 系统状态
SystemStatusType = Literal[
    "healthy", "degraded", "unhealthy", "initializing", "shutting_down"
]


class HealthCheckModel(BaseModel):
    """健康检查模型"""
    status: SystemStatusType = "healthy"
    timestamp: str
    uptime: float = Field(description="运行时间（秒）")
    version: str = Field(description="服务版本")


class ConfigModel(BaseModel):
    """配置模型"""
    key: str = Field(description="配置键")
    value: Any = Field(description="配置值")
    description: Optional[str] = Field(None, description="配置描述")
    is_sensitive: bool = Field(default=False, description="是否敏感信息")


class ValidationError(BaseModel):
    """验证错误模型"""
    field: str = Field(description="字段名")
    message: str = Field(description="错误消息")
    value: Optional[Any] = Field(None, description="错误值")


class OperationResult(BaseModel):
    """操作结果模型"""
    success: bool = Field(description="是否成功")
    message: str = Field(description="结果消息")
    data: Optional[Any] = Field(None, description="结果数据")
    errors: List[ValidationError] = Field(default_factory=list, description="错误列表")
    warnings: List[str] = Field(default_factory=list, description="警告列表")


class ProgressModel(BaseModel):
    """进度模型"""
    current: int = Field(description="当前进度")
    total: int = Field(description="总数")
    percentage: float = Field(description="完成百分比")
    status: str = Field(description="状态描述")
    estimated_remaining: Optional[float] = Field(None, description="预计剩余时间（秒）")


class ResourceUsageModel(BaseModel):
    """资源使用模型"""
    cpu_percent: float = Field(description="CPU使用率")
    memory_percent: float = Field(description="内存使用率")
    disk_percent: float = Field(description="磁盘使用率")
    network_io: Optional[Dict[str, int]] = Field(None, description="网络IO")


class PerformanceMetrics(BaseModel):
    """性能指标模型"""
    response_time: float = Field(description="响应时间（秒）")
    throughput: float = Field(description="吞吐量（请求/秒）")
    error_rate: float = Field(description="错误率")
    resource_usage: ResourceUsageModel = Field(description="资源使用情况")


class CacheInfo(BaseModel):
    """缓存信息模型"""
    hit_rate: float = Field(description="缓存命中率")
    miss_rate: float = Field(description="缓存未命中率")
    size: int = Field(description="缓存大小")
    max_size: int = Field(description="最大缓存大小")
    ttl: int = Field(description="生存时间（秒）")


class BatchOperation(BaseModel):
    """批量操作模型"""
    batch_id: str = Field(description="批次ID")
    total_items: int = Field(description="总项目数")
    processed_items: int = Field(description="已处理项目数")
    failed_items: int = Field(description="失败项目数")
    status: str = Field(description="批次状态")
    start_time: str = Field(description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")


class APIEndpointInfo(BaseModel):
    """API端点信息模型"""
    path: str = Field(description="端点路径")
    method: str = Field(description="HTTP方法")
    description: str = Field(description="端点描述")
    parameters: List[Dict[str, Any]] = Field(default_factory=list, description="参数列表")
    responses: Dict[str, Any] = Field(default_factory=dict, description="响应示例")


class ServiceInfo(BaseModel):
    """服务信息模型"""
    name: str = Field(description="服务名称")
    version: str = Field(description="服务版本")
    description: str = Field(description="服务描述")
    status: SystemStatusType = Field(description="服务状态")
    endpoints: List[APIEndpointInfo] = Field(default_factory=list, description="API端点列表")


# 导出所有模型
__all__ = [
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
    "SystemStatusType"
]
