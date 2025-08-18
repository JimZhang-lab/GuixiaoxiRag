"""
系统管理路由
处理系统状态、配置管理、性能监控等功能
"""
from fastapi import APIRouter, HTTPException, Request

from model import (
    BaseResponse, ConfigUpdateRequest, PerformanceConfigRequest,
    SystemResetRequest, MetricsRequest, HealthResponse,
    SystemStatus, ConfigResponse, ServiceConfigResponse,
    MetricsResponse, PerformanceStatsResponse
)
from api.system_api import SystemAPI

# 创建路由器
router = APIRouter(prefix="/api/v1", tags=["系统管理"])

# 创建API处理器实例
system_api = SystemAPI()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="系统健康检查",
    description="""
    检查系统的整体健康状态和各组件运行情况。
    
    **检查项目：**
    - 服务运行状态
    - 数据库连接
    - 文件系统访问
    - 内存使用情况
    - 依赖服务状态
    
    **健康状态：**
    - healthy: 系统运行正常
    - degraded: 系统部分功能受影响
    - unhealthy: 系统存在严重问题
    - initializing: 系统正在初始化
    - shutting_down: 系统正在关闭
    
    **返回信息：**
    - status: 整体健康状态
    - timestamp: 检查时间
    - system: 系统详细状态
    - dependencies: 依赖服务状态
    
    **使用场景：**
    - 服务监控和告警
    - 负载均衡健康检查
    - 运维状态监控
    """
)
async def health_check():
    """系统健康检查"""
    return await system_api.health_check()


@router.get(
    "/system/status",
    response_model=BaseResponse,
    summary="获取系统详细状态",
    description="""
    获取系统的详细运行状态和配置信息。
    
    **状态信息：**
    - 服务基本信息（名称、版本、运行时间）
    - 初始化状态
    - 当前工作目录和知识库
    - 性能指标
    - 缓存信息
    - 资源使用情况
    
    **返回数据：**
    - service_name: 服务名称
    - version: 服务版本
    - status: 服务状态
    - initialized: 是否已初始化
    - working_dir: 工作目录
    - uptime: 运行时间
    - performance: 性能指标
    - cache_info: 缓存信息
    
    **使用场景：**
    - 系统状态监控
    - 问题诊断和调试
    - 性能分析
    """
)
async def get_system_status():
    """获取系统详细状态"""
    return await system_api.get_system_status()


@router.get(
    "/metrics",
    response_model=BaseResponse,
    summary="获取系统性能指标",
    description="""
    获取系统的性能监控指标和统计信息。
    
    **性能指标：**
    - 请求统计（总数、成功率、错误率）
    - 响应时间（平均值、百分位数）
    - 资源使用（CPU、内存、磁盘）
    - 缓存统计（命中率、大小）
    - 端点性能分析
    
    **时间范围：**
    - 实时指标
    - 最近1小时
    - 最近24小时
    - 历史趋势
    
    **返回数据：**
    - request_count: 请求总数
    - error_count: 错误总数
    - error_rate: 错误率
    - avg_response_time: 平均响应时间
    - response_time_percentiles: 响应时间百分位数
    - resource_usage: 资源使用情况
    - cache_stats: 缓存统计
    - endpoint_metrics: 端点性能指标
    
    **使用场景：**
    - 性能监控和优化
    - 容量规划
    - SLA监控
    """
)
async def get_metrics():
    """获取系统性能指标"""
    return await system_api.get_metrics()


@router.get(
    "/logs",
    response_model=BaseResponse,
    summary="获取系统日志",
    description="""
    获取系统的最近日志记录。
    
    **参数说明：**
    - lines: 日志行数（默认100，最大1000）
    - level: 日志级别过滤（DEBUG/INFO/WARNING/ERROR）
    - start_time: 开始时间
    - end_time: 结束时间
    
    **日志级别：**
    - DEBUG: 调试信息
    - INFO: 一般信息
    - WARNING: 警告信息
    - ERROR: 错误信息
    - CRITICAL: 严重错误
    
    **返回数据：**
    - logs: 日志记录列表
    - total_lines: 总行数
    - log_file: 日志文件路径
    - last_update: 最后更新时间
    
    **使用场景：**
    - 问题诊断和调试
    - 系统行为分析
    - 审计和合规
    """
)
async def get_logs(lines: int = 100):
    """获取最近的日志"""
    return await system_api.get_logs(lines)


@router.post(
    "/system/reset",
    response_model=BaseResponse,
    summary="系统重置",
    description="""
    重置系统到初始状态，清理所有数据和缓存。
    
    **警告：** 此操作将清除所有数据，不可恢复！
    
    **重置内容：**
    - 清空所有知识库数据
    - 清除缓存和临时文件
    - 重置配置到默认值（可选）
    - 清理日志文件
    - 重新初始化服务
    
    **参数说明：**
    - confirm: 确认重置（必须为true）
    - backup_data: 是否备份数据（默认true）
    - reset_config: 是否重置配置（默认false）
    
    **使用场景：**
    - 系统维护和清理
    - 测试环境重置
    - 故障恢复
    
    **注意事项：**
    - 建议在操作前备份重要数据
    - 重置后需要重新配置和导入数据
    """
)
async def reset_system(request: SystemResetRequest):
    """系统重置"""
    return await system_api.reset_system(request)


@router.get(
    "/service/config",
    response_model=BaseResponse,
    summary="获取当前服务配置",
    description="""
    获取当前服务的配置信息。
    
    **配置信息：**
    - 当前工作目录
    - 当前知识库
    - 语言设置
    - 初始化状态
    - 缓存实例数量
    - 性能模式
    
    **返回数据：**
    - working_dir: 当前工作目录
    - knowledge_base: 当前知识库
    - language: 当前语言
    - initialized: 是否已初始化
    - cached_instances: 缓存实例数量
    - performance_mode: 性能模式
    
    **使用场景：**
    - 配置查看和验证
    - 系统状态确认
    - 调试和诊断
    """
)
async def get_service_config():
    """获取当前服务配置"""
    return await system_api.get_service_config()


@router.get(
    "/service/effective-config",
    response_model=BaseResponse,
    summary="获取有效配置信息",
    description="""
    获取系统的有效配置信息，包括默认值和用户自定义配置。
    
    **配置类别：**
    - 应用基本信息
    - 服务配置
    - LLM配置
    - Embedding配置
    - 文件处理配置
    - 性能配置
    
    **返回数据：**
    - app_name: 应用名称
    - version: 版本号
    - host: 服务主机
    - port: 服务端口
    - llm: LLM配置信息
    - embedding: Embedding配置信息
    - max_file_size_mb: 最大文件大小
    - streamlit_port: Streamlit端口
    
    **使用场景：**
    - 配置审查和验证
    - 问题诊断
    - 系统集成
    """
)
async def get_effective_config():
    """获取有效配置信息"""
    return await system_api.get_effective_config()


@router.post(
    "/service/config/update",
    response_model=BaseResponse,
    summary="更新服务配置",
    description="""
    更新服务的配置参数。
    
    **可更新配置：**
    - LLM API配置（URL、密钥、模型）
    - Embedding API配置
    - 系统参数（日志级别、token大小等）
    - 自定义提供商配置
    - Azure特定配置
    
    **参数说明：**
    - openai_api_base: LLM API基础URL
    - openai_embedding_api_base: Embedding API基础URL
    - openai_chat_api_key: LLM API密钥
    - openai_embedding_api_key: Embedding API密钥
    - openai_chat_model: LLM模型名称
    - openai_embedding_model: Embedding模型名称
    - embedding_dim: Embedding维度
    - max_token_size: 最大Token数
    - log_level: 日志级别
    
    **返回结果：**
    - updated_fields: 已更新的配置字段
    - effective_config: 当前有效配置
    - restart_required: 是否需要重启服务
    - validation_errors: 验证错误列表
    
    **使用示例：**
    ```json
    {
        "openai_api_base": "http://localhost:8100/v1",
        "openai_chat_model": "qwen14b",
        "log_level": "INFO"
    }
    ```
    """
)
async def update_service_config(request: ConfigUpdateRequest):
    """更新服务配置"""
    return await system_api.update_service_config(request)


# 导出路由器
__all__ = ["router"]
