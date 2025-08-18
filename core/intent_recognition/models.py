"""
意图识别核心数据模型
"""
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


class QueryIntentType(Enum):
    """查询意图类型"""
    KNOWLEDGE_QUERY = "knowledge_query"  # 知识查询
    FACTUAL_QUESTION = "factual_question"  # 事实性问题
    ANALYTICAL_QUESTION = "analytical_question"  # 分析性问题
    PROCEDURAL_QUESTION = "procedural_question"  # 程序性问题
    CREATIVE_REQUEST = "creative_request"  # 创意请求
    GREETING = "greeting"  # 问候
    UNCLEAR = "unclear"  # 意图不明确
    ILLEGAL_CONTENT = "illegal_content"  # 非法内容


class ContentSafetyLevel(Enum):
    """内容安全级别"""
    SAFE = "safe"  # 安全
    SUSPICIOUS = "suspicious"  # 可疑
    UNSAFE = "unsafe"  # 不安全
    ILLEGAL = "illegal"  # 非法


@dataclass
class QueryAnalysisResult:
    """查询分析结果"""
    original_query: str
    processed_query: str
    intent_type: QueryIntentType
    safety_level: ContentSafetyLevel
    confidence: float
    suggestions: List[str]
    risk_factors: List[str]
    enhanced_query: Optional[str] = None
    should_reject: bool = False
    rejection_reason: Optional[str] = None
    safety_tips: List[str] = None
    safe_alternatives: List[str] = None
    processing_time: float = 0.0
    
    def __post_init__(self):
        """初始化后处理"""
        if self.safety_tips is None:
            self.safety_tips = []
        if self.safe_alternatives is None:
            self.safe_alternatives = []


@dataclass
class SafetyCheckResult:
    """安全检查结果"""
    is_safe: bool
    safety_level: str
    risk_factors: List[str]
    confidence: float
    reason: str
    intent_direction: Optional[str] = None
    sensitive_words: List[str] = None
    filtered_text: Optional[str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.sensitive_words is None:
            self.sensitive_words = []


@dataclass
class IntentAnalysisResult:
    """意图分析结果"""
    intent_type: str
    confidence: float
    reason: str
    keywords: List[str]
    
    def __post_init__(self):
        """初始化后处理"""
        if self.keywords is None:
            self.keywords = []


@dataclass
class QueryEnhancementResult:
    """查询增强结果"""
    should_enhance: bool
    enhanced_query: Optional[str]
    enhancement_reason: str
    suggestions: List[str]
    
    def __post_init__(self):
        """初始化后处理"""
        if self.suggestions is None:
            self.suggestions = []


@dataclass
class LLMPromptConfig:
    """大模型提示词配置"""
    safety_check_prompt: Optional[str] = None
    intent_analysis_prompt: Optional[str] = None
    query_enhancement_prompt: Optional[str] = None
    custom_prompts: Optional[Dict[str, str]] = None

    def __post_init__(self):
        """初始化后处理"""
        if self.custom_prompts is None:
            self.custom_prompts = {}


@dataclass
class IntentTypeConfig:
    """意图类型配置"""
    intent_types: Dict[str, str]  # intent_type -> display_name
    custom_intent_types: Optional[Dict[str, str]] = None
    intent_priorities: Optional[Dict[str, int]] = None
    intent_categories: Optional[Dict[str, str]] = None

    def __post_init__(self):
        """初始化后处理"""
        if self.custom_intent_types is None:
            self.custom_intent_types = {}
        if self.intent_priorities is None:
            self.intent_priorities = {}
        if self.intent_categories is None:
            self.intent_categories = {}


@dataclass
class SafetyConfig:
    """安全检查配置"""
    safety_levels: Dict[str, str]  # level -> display_name
    risk_keywords: Optional[List[str]] = None
    educational_patterns: Optional[List[str]] = None
    instructive_patterns: Optional[List[str]] = None
    custom_safety_rules: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """初始化后处理"""
        if self.risk_keywords is None:
            self.risk_keywords = []
        if self.educational_patterns is None:
            self.educational_patterns = []
        if self.instructive_patterns is None:
            self.instructive_patterns = []
        if self.custom_safety_rules is None:
            self.custom_safety_rules = {}


class ProcessorConfig:
    """处理器配置 - 支持灵活配置"""

    def __init__(self,
                 confidence_threshold: float = 0.7,
                 enable_llm: bool = True,
                 enable_dfa_filter: bool = True,
                 enable_query_enhancement: bool = True,
                 sensitive_vocabulary_path: str = "core/intent_recognition/sensitive_vocabulary",
                 config_path: Optional[str] = None,
                 llm_prompt_config: Optional[LLMPromptConfig] = None,
                 intent_type_config: Optional[IntentTypeConfig] = None,
                 safety_config: Optional[SafetyConfig] = None):
        self.confidence_threshold = confidence_threshold
        self.enable_llm = enable_llm
        self.enable_dfa_filter = enable_dfa_filter
        self.enable_query_enhancement = enable_query_enhancement
        self.sensitive_vocabulary_path = sensitive_vocabulary_path
        self.config_path = config_path

        # 配置对象
        self.llm_prompt_config = llm_prompt_config or LLMPromptConfig()
        self.intent_type_config = intent_type_config or IntentTypeConfig(
            intent_types={
                "knowledge_query": "知识查询",
                "factual_question": "事实性问题",
                "analytical_question": "分析性问题",
                "procedural_question": "程序性问题",
                "creative_request": "创意请求",
                "greeting": "问候",
                "unclear": "意图不明确",
                "illegal_content": "非法内容"
            }
        )
        self.safety_config = safety_config or SafetyConfig(
            safety_levels={
                "safe": "安全",
                "suspicious": "可疑",
                "unsafe": "不安全",
                "illegal": "非法"
            }
        )

    @classmethod
    def from_file(cls, config_path: str) -> 'ProcessorConfig':
        """从配置文件加载配置"""
        import json
        import os

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 解析基础配置
        base_config = config_data.get('base', {})

        # 解析提示词配置
        prompt_data = config_data.get('llm_prompts', {})
        llm_prompt_config = LLMPromptConfig(
            safety_check_prompt=prompt_data.get('safety_check_prompt'),
            intent_analysis_prompt=prompt_data.get('intent_analysis_prompt'),
            query_enhancement_prompt=prompt_data.get('query_enhancement_prompt'),
            custom_prompts=prompt_data.get('custom_prompts', {})
        )

        # 解析意图类型配置
        intent_data = config_data.get('intent_types', {})
        intent_type_config = IntentTypeConfig(
            intent_types=intent_data.get('intent_types', {}),
            custom_intent_types=intent_data.get('custom_intent_types', {}),
            intent_priorities=intent_data.get('intent_priorities', {}),
            intent_categories=intent_data.get('intent_categories', {})
        )

        # 解析安全配置
        safety_data = config_data.get('safety', {})
        safety_config = SafetyConfig(
            safety_levels=safety_data.get('safety_levels', {}),
            risk_keywords=safety_data.get('risk_keywords', []),
            educational_patterns=safety_data.get('educational_patterns', []),
            instructive_patterns=safety_data.get('instructive_patterns', []),
            custom_safety_rules=safety_data.get('custom_safety_rules', {})
        )

        return cls(
            confidence_threshold=base_config.get('confidence_threshold', 0.7),
            enable_llm=base_config.get('enable_llm', True),
            enable_dfa_filter=base_config.get('enable_dfa_filter', True),
            enable_query_enhancement=base_config.get('enable_query_enhancement', True),
            sensitive_vocabulary_path=base_config.get('sensitive_vocabulary_path',
                                                    "core/intent_recognition/sensitive_vocabulary"),
            config_path=config_path,
            llm_prompt_config=llm_prompt_config,
            intent_type_config=intent_type_config,
            safety_config=safety_config
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'base': {
                'confidence_threshold': self.confidence_threshold,
                'enable_llm': self.enable_llm,
                'enable_dfa_filter': self.enable_dfa_filter,
                'enable_query_enhancement': self.enable_query_enhancement,
                'sensitive_vocabulary_path': self.sensitive_vocabulary_path
            },
            'llm_prompts': {
                'safety_check_prompt': self.llm_prompt_config.safety_check_prompt,
                'intent_analysis_prompt': self.llm_prompt_config.intent_analysis_prompt,
                'query_enhancement_prompt': self.llm_prompt_config.query_enhancement_prompt,
                'custom_prompts': self.llm_prompt_config.custom_prompts
            },
            'intent_types': {
                'intent_types': self.intent_type_config.intent_types,
                'custom_intent_types': self.intent_type_config.custom_intent_types,
                'intent_priorities': self.intent_type_config.intent_priorities,
                'intent_categories': self.intent_type_config.intent_categories
            },
            'safety': {
                'safety_levels': self.safety_config.safety_levels,
                'risk_keywords': self.safety_config.risk_keywords,
                'educational_patterns': self.safety_config.educational_patterns,
                'instructive_patterns': self.safety_config.instructive_patterns,
                'custom_safety_rules': self.safety_config.custom_safety_rules
            }
        }

    def save_to_file(self, config_path: str):
        """保存配置到文件"""
        import json
        import os

        # 确保目录存在
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)


# 导出所有模型
__all__ = [
    "QueryIntentType",
    "ContentSafetyLevel", 
    "QueryAnalysisResult",
    "SafetyCheckResult",
    "IntentAnalysisResult",
    "QueryEnhancementResult",
    "ProcessorConfig"
]
