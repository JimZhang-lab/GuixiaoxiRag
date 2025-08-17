"""
系统相关数据模型定义
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .base_models import SystemStatusType, PerformanceMode


class SystemConfiguration(BaseModel):
    """系统配置模型"""
    config_id: str = Field(..., description="配置ID")
    section: str = Field(..., description="配置节")
    key: str = Field(..., description="配置键")
    value: Any = Field(..., description="配置值")
    data_type: str = Field(..., description="数据类型")
    description: Optional[str] = Field(None, description="配置描述")
    is_sensitive: bool = Field(default=False, description="是否敏感信息")
    is_readonly: bool = Field(default=False, description="是否只读")
    validation_rule: Optional[str] = Field(None, description="验证规则")
    default_value: Optional[Any] = Field(None, description="默认值")
    updated_at: str = Field(..., description="更新时间")
    updated_by: Optional[str] = Field(None, description="更新者")


class SystemHealth(BaseModel):
    """系统健康状态模型"""
    status: SystemStatusType = Field(..., description="系统状态")
    timestamp: str = Field(..., description="检查时间")
    uptime: float = Field(..., description="运行时间（秒）")
    version: str = Field(..., description="系统版本")
    components: Dict[str, str] = Field(..., description="组件状态")
    dependencies: Dict[str, str] = Field(..., description="依赖服务状态")
    resource_usage: Dict[str, float] = Field(..., description="资源使用情况")
    performance_metrics: Dict[str, float] = Field(..., description="性能指标")
    alerts: List[str] = Field(default_factory=list, description="告警信息")
    warnings: List[str] = Field(default_factory=list, description="警告信息")


class SystemMetrics(BaseModel):
    """系统指标模型"""
    metric_id: str = Field(..., description="指标ID")
    metric_name: str = Field(..., description="指标名称")
    metric_type: str = Field(..., description="指标类型")
    value: float = Field(..., description="指标值")
    unit: str = Field(..., description="单位")
    timestamp: str = Field(..., description="时间戳")
    tags: Dict[str, str] = Field(default_factory=dict, description="标签")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class SystemAlert(BaseModel):
    """系统告警模型"""
    alert_id: str = Field(..., description="告警ID")
    alert_type: str = Field(..., description="告警类型")
    severity: str = Field(..., description="严重程度")
    title: str = Field(..., description="告警标题")
    message: str = Field(..., description="告警消息")
    source: str = Field(..., description="告警源")
    metric_name: Optional[str] = Field(None, description="相关指标")
    threshold: Optional[float] = Field(None, description="阈值")
    current_value: Optional[float] = Field(None, description="当前值")
    status: str = Field(default="active", description="告警状态")
    created_at: str = Field(..., description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")
    resolved_at: Optional[str] = Field(None, description="解决时间")
    acknowledged_at: Optional[str] = Field(None, description="确认时间")
    acknowledged_by: Optional[str] = Field(None, description="确认者")


class SystemLog(BaseModel):
    """系统日志模型"""
    log_id: str = Field(..., description="日志ID")
    level: str = Field(..., description="日志级别")
    logger_name: str = Field(..., description="日志器名称")
    message: str = Field(..., description="日志消息")
    timestamp: str = Field(..., description="时间戳")
    module: Optional[str] = Field(None, description="模块名")
    function: Optional[str] = Field(None, description="函数名")
    line_number: Optional[int] = Field(None, description="行号")
    thread_id: Optional[str] = Field(None, description="线程ID")
    process_id: Optional[str] = Field(None, description="进程ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    request_id: Optional[str] = Field(None, description="请求ID")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="额外数据")


class SystemBackup(BaseModel):
    """系统备份模型"""
    backup_id: str = Field(..., description="备份ID")
    backup_type: str = Field(..., description="备份类型")
    backup_name: str = Field(..., description="备份名称")
    backup_path: str = Field(..., description="备份路径")
    backup_size: int = Field(..., description="备份大小（字节）")
    compression: Optional[str] = Field(None, description="压缩方式")
    encryption: Optional[str] = Field(None, description="加密方式")
    checksum: Optional[str] = Field(None, description="校验和")
    status: str = Field(..., description="备份状态")
    start_time: str = Field(..., description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
    duration: Optional[float] = Field(None, description="备份时长（秒）")
    retention_period: Optional[int] = Field(None, description="保留期限（天）")
    metadata: Optional[Dict[str, Any]] = Field(None, description="备份元数据")


class SystemMaintenance(BaseModel):
    """系统维护模型"""
    maintenance_id: str = Field(..., description="维护ID")
    maintenance_type: str = Field(..., description="维护类型")
    title: str = Field(..., description="维护标题")
    description: str = Field(..., description="维护描述")
    status: str = Field(..., description="维护状态")
    priority: str = Field(..., description="优先级")
    scheduled_start: str = Field(..., description="计划开始时间")
    scheduled_end: str = Field(..., description="计划结束时间")
    actual_start: Optional[str] = Field(None, description="实际开始时间")
    actual_end: Optional[str] = Field(None, description="实际结束时间")
    affected_services: List[str] = Field(default_factory=list, description="受影响的服务")
    maintenance_steps: List[str] = Field(default_factory=list, description="维护步骤")
    rollback_plan: Optional[str] = Field(None, description="回滚计划")
    created_by: str = Field(..., description="创建者")
    assigned_to: Optional[str] = Field(None, description="负责人")


class SystemAudit(BaseModel):
    """系统审计模型"""
    audit_id: str = Field(..., description="审计ID")
    event_type: str = Field(..., description="事件类型")
    action: str = Field(..., description="操作")
    resource: str = Field(..., description="资源")
    resource_id: Optional[str] = Field(None, description="资源ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    timestamp: str = Field(..., description="时间戳")
    success: bool = Field(..., description="是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")
    before_state: Optional[Dict[str, Any]] = Field(None, description="变更前状态")
    after_state: Optional[Dict[str, Any]] = Field(None, description="变更后状态")
    metadata: Optional[Dict[str, Any]] = Field(None, description="审计元数据")


class SystemCapacity(BaseModel):
    """系统容量模型"""
    resource_type: str = Field(..., description="资源类型")
    current_usage: float = Field(..., description="当前使用量")
    total_capacity: float = Field(..., description="总容量")
    usage_percentage: float = Field(..., description="使用百分比")
    available: float = Field(..., description="可用量")
    unit: str = Field(..., description="单位")
    threshold_warning: float = Field(..., description="警告阈值")
    threshold_critical: float = Field(..., description="严重阈值")
    projected_usage: Optional[float] = Field(None, description="预计使用量")
    growth_rate: Optional[float] = Field(None, description="增长率")
    estimated_full_date: Optional[str] = Field(None, description="预计满载日期")


class SystemPerformance(BaseModel):
    """系统性能模型"""
    timestamp: str = Field(..., description="时间戳")
    cpu_usage: float = Field(..., description="CPU使用率")
    memory_usage: float = Field(..., description="内存使用率")
    disk_usage: float = Field(..., description="磁盘使用率")
    network_io: Dict[str, float] = Field(..., description="网络IO")
    disk_io: Dict[str, float] = Field(..., description="磁盘IO")
    response_time: float = Field(..., description="响应时间")
    throughput: float = Field(..., description="吞吐量")
    error_rate: float = Field(..., description="错误率")
    active_connections: int = Field(..., description="活跃连接数")
    queue_size: int = Field(..., description="队列大小")
    cache_hit_rate: float = Field(..., description="缓存命中率")


class SystemDependency(BaseModel):
    """系统依赖模型"""
    dependency_id: str = Field(..., description="依赖ID")
    name: str = Field(..., description="依赖名称")
    type: str = Field(..., description="依赖类型")
    version: str = Field(..., description="版本")
    status: str = Field(..., description="状态")
    endpoint: Optional[str] = Field(None, description="端点")
    health_check_url: Optional[str] = Field(None, description="健康检查URL")
    last_check: str = Field(..., description="最后检查时间")
    response_time: Optional[float] = Field(None, description="响应时间")
    error_message: Optional[str] = Field(None, description="错误信息")
    is_critical: bool = Field(default=False, description="是否关键依赖")
    retry_count: int = Field(default=0, description="重试次数")
    max_retries: int = Field(default=3, description="最大重试次数")


class SystemEnvironment(BaseModel):
    """系统环境模型"""
    environment_name: str = Field(..., description="环境名称")
    environment_type: str = Field(..., description="环境类型")
    platform: str = Field(..., description="平台信息")
    python_version: str = Field(..., description="Python版本")
    os_info: Dict[str, str] = Field(..., description="操作系统信息")
    hardware_info: Dict[str, Any] = Field(..., description="硬件信息")
    installed_packages: List[Dict[str, str]] = Field(..., description="已安装包")
    environment_variables: Dict[str, str] = Field(..., description="环境变量")
    configuration: Dict[str, Any] = Field(..., description="配置信息")
    last_updated: str = Field(..., description="最后更新时间")


# 导出所有系统相关模型
__all__ = [
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
