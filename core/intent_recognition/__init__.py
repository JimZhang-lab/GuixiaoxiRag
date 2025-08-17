"""
意图识别核心模块
优化版本 - 整合参考项目最佳实践
"""

from .models import (
    QueryIntentType,
    ContentSafetyLevel,
    QueryAnalysisResult,
    SafetyCheckResult,
    IntentAnalysisResult,
    QueryEnhancementResult,
    ProcessorConfig
)

from .processor import (
    IntentRecognitionProcessor,
    extracted_think_and_answer
)

from .dfa_filter import (
    DFAFilter,
    SensitiveWordManager
)

from .utils import (
    QueryUtils,
    IntentPatterns,
    EnhancementTemplates
)

# 版本信息
__version__ = "1.0.0"
__author__ = "GuiXiaoXiRag Team"

# 导出所有公共接口
__all__ = [
    # 模型类
    "QueryIntentType",
    "ContentSafetyLevel", 
    "QueryAnalysisResult",
    "SafetyCheckResult",
    "IntentAnalysisResult",
    "QueryEnhancementResult",
    "ProcessorConfig",
    
    # 处理器类
    "IntentRecognitionProcessor",
    "extracted_think_and_answer",
    
    # 过滤器类
    "DFAFilter",
    "SensitiveWordManager",
    
    # 工具类
    "QueryUtils",
    "IntentPatterns",
    "EnhancementTemplates"
]
