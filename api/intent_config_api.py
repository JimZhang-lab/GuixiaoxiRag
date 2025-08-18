"""
意图识别配置管理API
支持动态配置管理、热更新和配置验证
"""
import json
import time
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from common.logging_utils import logger_manager
from core.intent_recognition.config_manager import get_config_manager, get_processor_config
from core.intent_recognition.models import ProcessorConfig

logger = logger_manager.get_logger("intent_config_api")


class IntentConfigAPI:
    """意图识别配置管理API"""
    
    def __init__(self):
        self.config_manager = get_config_manager()
        logger.info("意图识别配置API初始化完成")
    
    async def get_current_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        try:
            config = self.config_manager.get_config()
            return {
                "success": True,
                "data": config.to_dict(),
                "message": "获取配置成功",
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"获取配置失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")
    
    async def update_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新配置"""
        try:
            self.config_manager.update_config(updates)
            return {
                "success": True,
                "message": "配置更新成功",
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"更新配置失败: {e}")
            raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")
    
    async def reload_config(self) -> Dict[str, Any]:
        """重新加载配置"""
        try:
            self.config_manager.reload_config()
            return {
                "success": True,
                "message": "配置重新加载成功",
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"重新加载配置失败: {e}")
            raise HTTPException(status_code=500, detail=f"重新加载配置失败: {str(e)}")
    
    async def get_intent_types(self) -> Dict[str, Any]:
        """获取意图类型配置"""
        try:
            config = self.config_manager.get_config()
            intent_config = config.intent_type_config
            
            return {
                "success": True,
                "data": {
                    "intent_types": intent_config.intent_types,
                    "custom_intent_types": intent_config.custom_intent_types,
                    "intent_priorities": intent_config.intent_priorities,
                    "intent_categories": intent_config.intent_categories
                },
                "message": "获取意图类型成功"
            }
        except Exception as e:
            logger.error(f"获取意图类型失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取意图类型失败: {str(e)}")
    
    async def add_intent_type(self, intent_type: str, display_name: str, 
                            priority: int = 50, category: str = "custom") -> Dict[str, Any]:
        """添加意图类型"""
        try:
            config = self.config_manager.get_config()
            
            # 检查是否已存在
            all_intents = {**config.intent_type_config.intent_types, 
                          **config.intent_type_config.custom_intent_types}
            if intent_type in all_intents:
                raise HTTPException(status_code=400, detail=f"意图类型 '{intent_type}' 已存在")
            
            # 添加新意图类型
            config.intent_type_config.custom_intent_types[intent_type] = display_name
            config.intent_type_config.intent_priorities[intent_type] = priority
            config.intent_type_config.intent_categories[intent_type] = category
            
            # 保存配置
            self.config_manager.save_config()
            
            return {
                "success": True,
                "message": f"意图类型 '{intent_type}' 添加成功",
                "data": {
                    "intent_type": intent_type,
                    "display_name": display_name,
                    "priority": priority,
                    "category": category
                }
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"添加意图类型失败: {e}")
            raise HTTPException(status_code=500, detail=f"添加意图类型失败: {str(e)}")
    
    async def remove_intent_type(self, intent_type: str) -> Dict[str, Any]:
        """移除意图类型"""
        try:
            config = self.config_manager.get_config()
            
            # 检查是否为内置类型
            if intent_type in config.intent_type_config.intent_types:
                raise HTTPException(status_code=400, detail=f"不能删除内置意图类型 '{intent_type}'")
            
            # 检查是否存在
            if intent_type not in config.intent_type_config.custom_intent_types:
                raise HTTPException(status_code=404, detail=f"意图类型 '{intent_type}' 不存在")
            
            # 移除意图类型
            del config.intent_type_config.custom_intent_types[intent_type]
            if intent_type in config.intent_type_config.intent_priorities:
                del config.intent_type_config.intent_priorities[intent_type]
            if intent_type in config.intent_type_config.intent_categories:
                del config.intent_type_config.intent_categories[intent_type]
            
            # 保存配置
            self.config_manager.save_config()
            
            return {
                "success": True,
                "message": f"意图类型 '{intent_type}' 移除成功"
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"移除意图类型失败: {e}")
            raise HTTPException(status_code=500, detail=f"移除意图类型失败: {str(e)}")
    
    async def get_prompts(self) -> Dict[str, Any]:
        """获取提示词配置"""
        try:
            config = self.config_manager.get_config()
            prompt_config = config.llm_prompt_config
            
            return {
                "success": True,
                "data": {
                    "safety_check_prompt": prompt_config.safety_check_prompt,
                    "intent_analysis_prompt": prompt_config.intent_analysis_prompt,
                    "query_enhancement_prompt": prompt_config.query_enhancement_prompt,
                    "custom_prompts": prompt_config.custom_prompts
                },
                "message": "获取提示词成功"
            }
        except Exception as e:
            logger.error(f"获取提示词失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取提示词失败: {str(e)}")
    
    async def update_prompt(self, prompt_type: str, prompt_content: str) -> Dict[str, Any]:
        """更新提示词"""
        try:
            config = self.config_manager.get_config()
            
            if prompt_type == "safety_check":
                config.llm_prompt_config.safety_check_prompt = prompt_content
            elif prompt_type == "intent_analysis":
                config.llm_prompt_config.intent_analysis_prompt = prompt_content
            elif prompt_type == "query_enhancement":
                config.llm_prompt_config.query_enhancement_prompt = prompt_content
            else:
                # 自定义提示词
                config.llm_prompt_config.custom_prompts[prompt_type] = prompt_content
            
            # 保存配置
            self.config_manager.save_config()
            
            return {
                "success": True,
                "message": f"提示词 '{prompt_type}' 更新成功"
            }
        except Exception as e:
            logger.error(f"更新提示词失败: {e}")
            raise HTTPException(status_code=500, detail=f"更新提示词失败: {str(e)}")
    
    async def get_safety_config(self) -> Dict[str, Any]:
        """获取安全配置"""
        try:
            config = self.config_manager.get_config()
            safety_config = config.safety_config
            
            return {
                "success": True,
                "data": {
                    "safety_levels": safety_config.safety_levels,
                    "risk_keywords": safety_config.risk_keywords,
                    "educational_patterns": safety_config.educational_patterns,
                    "instructive_patterns": safety_config.instructive_patterns,
                    "custom_safety_rules": safety_config.custom_safety_rules
                },
                "message": "获取安全配置成功"
            }
        except Exception as e:
            logger.error(f"获取安全配置失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取安全配置失败: {str(e)}")
    
    async def update_safety_config(self, safety_updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新安全配置"""
        try:
            config = self.config_manager.get_config()
            safety_config = config.safety_config
            
            # 更新各项安全配置
            if "risk_keywords" in safety_updates:
                safety_config.risk_keywords = safety_updates["risk_keywords"]
            
            if "educational_patterns" in safety_updates:
                safety_config.educational_patterns = safety_updates["educational_patterns"]
            
            if "instructive_patterns" in safety_updates:
                safety_config.instructive_patterns = safety_updates["instructive_patterns"]
            
            if "custom_safety_rules" in safety_updates:
                safety_config.custom_safety_rules.update(safety_updates["custom_safety_rules"])
            
            # 保存配置
            self.config_manager.save_config()
            
            return {
                "success": True,
                "message": "安全配置更新成功"
            }
        except Exception as e:
            logger.error(f"更新安全配置失败: {e}")
            raise HTTPException(status_code=500, detail=f"更新安全配置失败: {str(e)}")
    
    async def validate_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证配置"""
        try:
            errors = []
            warnings = []
            
            # 验证基础配置
            if "base" in config_data:
                base_config = config_data["base"]
                if "confidence_threshold" in base_config:
                    threshold = base_config["confidence_threshold"]
                    if not 0 <= threshold <= 1:
                        errors.append("confidence_threshold 必须在 0-1 之间")
            
            # 验证意图类型
            if "intent_types" in config_data:
                intent_config = config_data["intent_types"]
                if "custom_intent_types" in intent_config:
                    custom_intents = intent_config["custom_intent_types"]
                    if not isinstance(custom_intents, dict):
                        errors.append("custom_intent_types 必须是字典格式")
            
            # 验证提示词
            if "llm_prompts" in config_data:
                prompt_config = config_data["llm_prompts"]
                for prompt_type, prompt_content in prompt_config.items():
                    if prompt_content and not isinstance(prompt_content, str):
                        errors.append(f"提示词 '{prompt_type}' 必须是字符串格式")
            
            return {
                "success": len(errors) == 0,
                "data": {
                    "errors": errors,
                    "warnings": warnings,
                    "is_valid": len(errors) == 0
                },
                "message": "配置验证完成"
            }
        except Exception as e:
            logger.error(f"配置验证失败: {e}")
            raise HTTPException(status_code=500, detail=f"配置验证失败: {str(e)}")
    
    async def export_config(self) -> Dict[str, Any]:
        """导出配置"""
        try:
            config = self.config_manager.get_config()
            return {
                "success": True,
                "data": config.to_dict(),
                "message": "配置导出成功",
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"导出配置失败: {e}")
            raise HTTPException(status_code=500, detail=f"导出配置失败: {str(e)}")
    
    async def import_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """导入配置"""
        try:
            # 先验证配置
            validation_result = await self.validate_config(config_data)
            if not validation_result["data"]["is_valid"]:
                raise HTTPException(status_code=400, detail=f"配置验证失败: {validation_result['data']['errors']}")
            
            # 更新配置
            await self.update_config(config_data)
            
            return {
                "success": True,
                "message": "配置导入成功",
                "timestamp": time.time()
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            raise HTTPException(status_code=500, detail=f"导入配置失败: {str(e)}")


# 全局API实例
intent_config_api = IntentConfigAPI()


# 导出
__all__ = ["IntentConfigAPI", "intent_config_api"]
