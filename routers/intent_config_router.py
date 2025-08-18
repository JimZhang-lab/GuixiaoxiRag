"""
意图识别配置管理路由
支持动态配置管理、热更新和配置验证

功能包括：
- 配置的获取、更新和重载
- 意图类型的管理（获取、添加、删除）
- 提示词的管理
- 安全配置的管理
- 配置验证和导入导出

注意：静态模板和示例数据已移至API文档，减少冗余接口
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Body
from pydantic import BaseModel, Field

from api.intent_config_api import intent_config_api

# 创建路由器
router = APIRouter(prefix="/api/v1/intent-config", tags=["意图识别配置管理"])


class IntentTypeRequest(BaseModel):
    """意图类型请求模型"""
    intent_type: str = Field(..., description="意图类型标识")
    display_name: str = Field(..., description="显示名称")
    priority: int = Field(default=50, description="优先级")
    category: str = Field(default="custom", description="分类")


class PromptUpdateRequest(BaseModel):
    """提示词更新请求模型"""
    prompt_type: str = Field(..., description="提示词类型")
    prompt_content: str = Field(..., description="提示词内容")


class SafetyConfigRequest(BaseModel):
    """安全配置请求模型"""
    risk_keywords: List[str] = Field(default=[], description="风险关键词")
    educational_patterns: List[str] = Field(default=[], description="教育模式")
    instructive_patterns: List[str] = Field(default=[], description="指导模式")
    custom_safety_rules: Dict[str, Any] = Field(default={}, description="自定义安全规则")


@router.get("/current", summary="获取当前配置")
async def get_current_config():
    """获取当前意图识别配置"""
    return await intent_config_api.get_current_config()


@router.post("/update", summary="更新配置")
async def update_config(updates: Dict[str, Any] = Body(...)):
    """更新意图识别配置"""
    return await intent_config_api.update_config(updates)


@router.post("/reload", summary="重新加载配置")
async def reload_config():
    """重新加载配置文件"""
    return await intent_config_api.reload_config()


@router.get("/intent-types", summary="获取意图类型")
async def get_intent_types():
    """获取所有意图类型配置"""
    return await intent_config_api.get_intent_types()


@router.post("/intent-types", summary="添加意图类型")
async def add_intent_type(request: IntentTypeRequest):
    """添加新的意图类型"""
    return await intent_config_api.add_intent_type(
        intent_type=request.intent_type,
        display_name=request.display_name,
        priority=request.priority,
        category=request.category
    )


@router.delete("/intent-types/{intent_type}", summary="删除意图类型")
async def remove_intent_type(intent_type: str):
    """删除指定的意图类型"""
    return await intent_config_api.remove_intent_type(intent_type)


@router.get("/prompts", summary="获取提示词")
async def get_prompts():
    """获取所有提示词配置"""
    return await intent_config_api.get_prompts()


@router.post("/prompts", summary="更新提示词")
async def update_prompt(request: PromptUpdateRequest):
    """更新指定的提示词"""
    return await intent_config_api.update_prompt(
        prompt_type=request.prompt_type,
        prompt_content=request.prompt_content
    )


@router.get("/safety", summary="获取安全配置")
async def get_safety_config():
    """获取安全检查配置"""
    return await intent_config_api.get_safety_config()


@router.post("/safety", summary="更新安全配置")
async def update_safety_config(request: SafetyConfigRequest):
    """更新安全检查配置"""
    safety_updates = {}
    if request.risk_keywords:
        safety_updates["risk_keywords"] = request.risk_keywords
    if request.educational_patterns:
        safety_updates["educational_patterns"] = request.educational_patterns
    if request.instructive_patterns:
        safety_updates["instructive_patterns"] = request.instructive_patterns
    if request.custom_safety_rules:
        safety_updates["custom_safety_rules"] = request.custom_safety_rules
    
    return await intent_config_api.update_safety_config(safety_updates)


@router.post("/validate", summary="验证配置")
async def validate_config(config_data: Dict[str, Any] = Body(...)):
    """验证配置数据的有效性"""
    return await intent_config_api.validate_config(config_data)


@router.get("/export", summary="导出配置")
async def export_config():
    """导出当前配置为JSON格式"""
    return await intent_config_api.export_config()


@router.post("/import", summary="导入配置")
async def import_config(config_data: Dict[str, Any] = Body(...)):
    """从JSON数据导入配置"""
    return await intent_config_api.import_config(config_data)


# 配置模板已移至API文档中，减少冗余的静态数据接口


# 配置状态信息已整合到 /current 接口中，避免重复功能


# 配置示例已移至API文档中，减少冗余的静态数据接口


# 导出路由器
__all__ = ["router"]
