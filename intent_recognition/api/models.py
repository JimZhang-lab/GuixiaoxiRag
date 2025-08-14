"""
意图识别API数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Generic, TypeVar

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """基础响应模型"""
    success: bool = Field(default=True, description="请求是否成功")
    message: str = Field(default="操作成功", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")


class IntentAnalysisRequest(BaseModel):
    """意图分析请求"""
    query: str = Field(..., description="查询内容")
    context: Optional[Dict[str, Any]] = Field(None, description="查询上下文")
    enable_enhancement: bool = Field(default=True, description="是否启用查询增强")
    safety_check: bool = Field(default=True, description="是否进行安全检查")


class IntentAnalysisResponse(BaseModel):
    """意图分析响应"""
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


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="服务版本")
    timestamp: str = Field(..., description="检查时间")
    llm_available: bool = Field(..., description="LLM是否可用")


class ServiceInfo(BaseModel):
    """服务信息"""
    name: str = Field(..., description="服务名称")
    version: str = Field(..., description="服务版本")
    description: str = Field(..., description="服务描述")
    endpoints: List[str] = Field(..., description="可用端点")
    features: List[str] = Field(..., description="功能特性")
