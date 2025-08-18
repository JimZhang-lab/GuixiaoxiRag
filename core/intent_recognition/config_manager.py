"""
意图识别配置管理器
支持动态配置加载、热更新和配置验证
"""
import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

from common.logging_utils import logger_manager
from common.config import settings
from .models import ProcessorConfig, LLMPromptConfig, IntentTypeConfig, SafetyConfig

# 可选的文件监听功能
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None

logger = logger_manager.get_logger("config_manager")


if WATCHDOG_AVAILABLE:
    class ConfigFileHandler(FileSystemEventHandler):
        """配置文件变更监听器"""

        def __init__(self, config_manager):
            self.config_manager = config_manager
            self.last_modified = {}

        def on_modified(self, event):
            if event.is_directory:
                return

            file_path = event.src_path
            if not file_path.endswith('.json'):
                return

            # 防止重复触发
            current_time = time.time()
            if file_path in self.last_modified:
                if current_time - self.last_modified[file_path] < 1.0:  # 1秒内的重复事件忽略
                    return

            self.last_modified[file_path] = current_time

            try:
                logger.info(f"检测到配置文件变更: {file_path}")
                self.config_manager.reload_config()
            except Exception as e:
                logger.error(f"重新加载配置失败: {e}")
else:
    class ConfigFileHandler:
        """配置文件变更监听器（占位符）"""
        def __init__(self, config_manager):
            pass


class IntentConfigManager:
    """意图识别配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config: Optional[ProcessorConfig] = None
        self.observer: Optional[Observer] = None
        self.file_handler: Optional[ConfigFileHandler] = None
        self._config_cache = {}
        self._last_reload_time = 0
        
        # 初始化配置
        self.load_config()
    
    def _get_default_config_path(self) -> str:
        """获取默认配置路径"""
        # 使用环境变量或配置文件中的路径
        intent_config_path = getattr(settings, 'intent_config_path', './data/custom_intents')
        return os.path.join(intent_config_path, 'processor_config.json')
    
    def load_config(self) -> ProcessorConfig:
        """加载配置"""
        try:
            if os.path.exists(self.config_path):
                logger.info(f"从文件加载配置: {self.config_path}")
                self.config = ProcessorConfig.from_file(self.config_path)
            else:
                logger.info("配置文件不存在，使用默认配置")
                self.config = self._create_default_config()
                # 保存默认配置到文件
                self.save_config()
            
            self._last_reload_time = time.time()
            logger.info("配置加载完成")
            return self.config
            
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            logger.info("使用默认配置")
            self.config = self._create_default_config()
            return self.config
    
    def reload_config(self):
        """重新加载配置"""
        logger.info("重新加载配置...")
        old_config = self.config
        try:
            self.load_config()
            logger.info("配置重新加载成功")
        except Exception as e:
            logger.error(f"配置重新加载失败，保持原配置: {e}")
            self.config = old_config
    
    def save_config(self):
        """保存当前配置到文件"""
        if self.config:
            try:
                self.config.save_to_file(self.config_path)
                logger.info(f"配置已保存到: {self.config_path}")
            except Exception as e:
                logger.error(f"保存配置失败: {e}")
    
    def _create_default_config(self) -> ProcessorConfig:
        """创建默认配置"""
        # 加载自定义意图类型
        custom_intents = self._load_custom_intents()
        
        # 创建意图类型配置
        intent_type_config = IntentTypeConfig(
            intent_types={
                "knowledge_query": "知识查询",
                "factual_question": "事实性问题", 
                "analytical_question": "分析性问题",
                "procedural_question": "程序性问题",
                "creative_request": "创意请求",
                "greeting": "问候",
                "unclear": "意图不明确",
                "illegal_content": "非法内容"
            },
            custom_intent_types=custom_intents.get('intent_types', {}),
            intent_priorities=custom_intents.get('priorities', {}),
            intent_categories=custom_intents.get('categories', {})
        )
        
        # 创建安全配置
        safety_config = SafetyConfig(
            safety_levels={
                "safe": "安全",
                "suspicious": "可疑", 
                "unsafe": "不安全",
                "illegal": "非法"
            },
            risk_keywords=[
                "赌博", "毒品", "色情", "暴力", "诈骗", "非法", "违法",
                "gambling", "drugs", "pornography", "violence", "fraud"
            ],
            educational_patterns=[
                "如何防范", "如何识别", "如何举报", "防范措施", "安全知识",
                "how to prevent", "how to identify", "safety measures"
            ],
            instructive_patterns=[
                "如何实施", "如何制作", "如何购买", "制作方法", "购买渠道",
                "how to implement", "how to make", "how to buy"
            ]
        )
        
        # 创建提示词配置
        llm_prompt_config = LLMPromptConfig()
        
        return ProcessorConfig(
            confidence_threshold=0.7,
            enable_llm=True,
            enable_dfa_filter=True,
            enable_query_enhancement=True,
            sensitive_vocabulary_path="core/intent_recognition/sensitive_vocabulary",
            config_path=self.config_path,
            llm_prompt_config=llm_prompt_config,
            intent_type_config=intent_type_config,
            safety_config=safety_config
        )
    
    def _load_custom_intents(self) -> Dict[str, Any]:
        """加载自定义意图配置"""
        custom_intents = {
            'intent_types': {},
            'priorities': {},
            'categories': {}
        }
        
        try:
            intent_config_path = getattr(settings, 'intent_config_path', './data/custom_intents')
            intents_file = os.path.join(intent_config_path, 'intents.json')
            
            if os.path.exists(intents_file):
                with open(intents_file, 'r', encoding='utf-8') as f:
                    intents_data = json.load(f)
                
                for intent in intents_data:
                    if intent.get('is_active', True):
                        intent_name = intent.get('name')
                        display_name = intent.get('display_name', intent_name)
                        priority = intent.get('priority', 50)
                        category = intent.get('category', 'general')
                        
                        if intent_name:
                            custom_intents['intent_types'][intent_name] = display_name
                            custom_intents['priorities'][intent_name] = priority
                            custom_intents['categories'][intent_name] = category
                
                logger.info(f"加载了 {len(custom_intents['intent_types'])} 个自定义意图类型")
            
        except Exception as e:
            logger.warning(f"加载自定义意图配置失败: {e}")
        
        return custom_intents
    
    def start_watching(self):
        """开始监听配置文件变更"""
        if not WATCHDOG_AVAILABLE:
            logger.warning("watchdog 模块不可用，无法启用文件监听功能")
            return

        if self.observer is not None:
            return  # 已经在监听

        try:
            config_dir = os.path.dirname(self.config_path)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)

            self.file_handler = ConfigFileHandler(self)
            self.observer = Observer()
            self.observer.schedule(self.file_handler, config_dir, recursive=False)
            self.observer.start()
            logger.info(f"开始监听配置文件变更: {config_dir}")

        except Exception as e:
            logger.error(f"启动配置文件监听失败: {e}")

    def stop_watching(self):
        """停止监听配置文件变更"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.file_handler = None
            logger.info("停止监听配置文件变更")
    
    def get_config(self) -> ProcessorConfig:
        """获取当前配置"""
        if self.config is None:
            self.load_config()
        return self.config
    
    def update_config(self, updates: Dict[str, Any]):
        """更新配置"""
        if self.config is None:
            self.load_config()
        
        try:
            # 更新基础配置
            if 'base' in updates:
                base_updates = updates['base']
                for key, value in base_updates.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
            
            # 更新提示词配置
            if 'llm_prompts' in updates:
                prompt_updates = updates['llm_prompts']
                for key, value in prompt_updates.items():
                    if hasattr(self.config.llm_prompt_config, key):
                        setattr(self.config.llm_prompt_config, key, value)
            
            # 更新意图类型配置
            if 'intent_types' in updates:
                intent_updates = updates['intent_types']
                for key, value in intent_updates.items():
                    if hasattr(self.config.intent_type_config, key):
                        setattr(self.config.intent_type_config, key, value)
            
            # 更新安全配置
            if 'safety' in updates:
                safety_updates = updates['safety']
                for key, value in safety_updates.items():
                    if hasattr(self.config.safety_config, key):
                        setattr(self.config.safety_config, key, value)
            
            # 保存更新后的配置
            self.save_config()
            logger.info("配置更新成功")
            
        except Exception as e:
            logger.error(f"更新配置失败: {e}")
            raise


# 全局配置管理器实例
_config_manager: Optional[IntentConfigManager] = None


def get_config_manager() -> IntentConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = IntentConfigManager()
    return _config_manager


def get_processor_config() -> ProcessorConfig:
    """获取处理器配置"""
    return get_config_manager().get_config()


# 导出
__all__ = [
    "IntentConfigManager",
    "get_config_manager", 
    "get_processor_config"
]
