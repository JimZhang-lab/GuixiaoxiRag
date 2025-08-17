"""
意图识别工具函数
优化版本 - 适配项目架构
"""
import re
from typing import List, Dict, Any
from common.logging_utils import logger_manager

logger = logger_manager.get_logger("intent_utils")


class QueryUtils:
    """查询处理工具类"""
    
    @staticmethod
    async def clean_and_normalize_query(query: str) -> str:
        """清理和标准化查询"""
        if not query:
            return ""
        
        # 去除多余空格
        query = re.sub(r'\s+', ' ', query.strip())
        
        # 去除特殊字符（保留基本标点）
        query = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()（）。，！？；：]', '', query)
        
        return query
    
    @staticmethod
    def find_illegal_hits(query: str, illegal_keywords: List[str]) -> List[str]:
        """查找命中的非法关键词"""
        hits = []
        query_lower = query.lower()
        
        for keyword in illegal_keywords:
            if keyword.lower() in query_lower:
                hits.append(keyword)
        
        return hits
    
    @staticmethod
    def has_educational_intent(query: str, educational_patterns: List[str]) -> bool:
        """检查是否有教育/防范意图"""
        query_lower = query.lower()
        return any(pattern.lower() in query_lower for pattern in educational_patterns)
    
    @staticmethod
    def has_instructive_intent(query: str, instructive_patterns: List[str]) -> bool:
        """检查是否有实施/教程意图"""
        query_lower = query.lower()
        return any(pattern.lower() in query_lower for pattern in instructive_patterns)
    
    @staticmethod
    def calculate_risk_score(query: str, illegal_keywords: List[str], 
                           educational_patterns: List[str], 
                           instructive_patterns: List[str]) -> float:
        """计算风险评分"""
        query_lower = query.lower()
        risk_score = 0.0
        
        # 检查非法关键词
        hits = QueryUtils.find_illegal_hits(query, illegal_keywords)
        has_edu = QueryUtils.has_educational_intent(query, educational_patterns)
        has_instr = QueryUtils.has_instructive_intent(query, instructive_patterns)
        
        if hits:
            if has_edu and not has_instr:
                risk_score += 0.3  # 教育导向，降低风险
            else:
                risk_score += 1.2  # 明显非法且有实施导向
        
        # 可疑模式检查
        suspicious_patterns = [
            r"如何.*违法", r"怎样.*犯罪", r"教我.*非法",
            r"制作.*毒品", r"购买.*枪支", r"(如何|怎么|怎样).*实施",
            r"how to.*illegal", r"where to buy.*drugs"
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, query_lower):
                risk_score += 0.8
        
        return min(risk_score, 2.0)  # 最大风险评分为2.0
    
    @staticmethod
    def determine_safety_level(risk_score: float) -> str:
        """根据风险评分确定安全级别"""
        if risk_score >= 1.0:
            return "illegal"
        elif risk_score >= 0.7:
            return "unsafe"
        elif risk_score >= 0.3:
            return "suspicious"
        else:
            return "safe"
    
    @staticmethod
    def generate_default_safety_tips(safety_level: str) -> List[str]:
        """生成默认安全提示"""
        if safety_level in ["unsafe", "illegal"]:
            return [
                "请遵守法律法规，不要尝试获取违法信息",
                "若遇到疑似非法行为，请及时向相关部门举报",
                "建议咨询专业法律人士了解相关法律风险"
            ]
        elif safety_level == "suspicious":
            return [
                "请确保查询内容符合法律法规要求",
                "建议以正向、教育的方式获取相关信息"
            ]
        else:
            return []
    
    @staticmethod
    def generate_default_alternatives(query: str) -> List[str]:
        """生成默认的安全替代建议"""
        alternatives = [
            "如何识别和防范相关风险？",
            "遇到类似情况该如何求助和举报？",
            "相关法律风险与合规解读"
        ]
        
        # 根据查询内容生成更具体的建议
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["赌博", "gambling"]):
            alternatives.extend([
                "如何识别网络赌博陷阱？",
                "赌博成瘾如何寻求帮助？"
            ])
        
        if any(word in query_lower for word in ["毒品", "drugs"]):
            alternatives.extend([
                "如何识别毒品的危害？",
                "毒品预防教育的重要性"
            ])
        
        if any(word in query_lower for word in ["诈骗", "fraud", "scam"]):
            alternatives.extend([
                "如何识别和防范网络诈骗？",
                "遇到诈骗如何举报和维权？"
            ])
        
        return alternatives[:3]  # 返回最多3个建议


class IntentPatterns:
    """意图模式管理类"""
    
    @staticmethod
    def get_default_patterns() -> Dict[str, List[str]]:
        """获取默认意图识别模式"""
        return {
            "knowledge_query": [
                r"什么是", r"介绍一下", r"解释", r"定义", r"概念",
                r"what is", r"explain", r"define", r"describe"
            ],
            "factual_question": [
                r"谁是", r"何时", r"哪里", r"多少", r"几个",
                r"who is", r"when", r"where", r"how many", r"how much"
            ],
            "analytical_question": [
                r"为什么", r"如何", r"怎样", r"分析", r"比较", r"评价",
                r"why", r"how", r"analyze", r"compare", r"evaluate"
            ],
            "procedural_question": [
                r"步骤", r"流程", r"方法", r"操作", r"教程", r"指南",
                r"steps", r"process", r"method", r"tutorial", r"guide"
            ],
            "creative_request": [
                r"创作", r"写", r"设计", r"生成", r"创造", r"编写",
                r"create", r"write", r"design", r"generate", r"compose"
            ],
            "greeting": [
                r"你好", r"您好", r"hi", r"hello", r"嗨", r"早上好", r"晚上好",
                r"good morning", r"good evening", r"good afternoon"
            ]
        }
    
    @staticmethod
    def get_educational_patterns() -> List[str]:
        """获取教育导向模式"""
        return [
            "防范", "避免", "识别", "辨别", "举报", "报警", "危害", "风险", "法律后果",
            "合规", "合法", "合规要求", "不良后果", "如何远离", "不该做", "违法与否",
            "how to avoid", "how to report", "how to identify", "risk", "legal consequences"
        ]
    
    @staticmethod
    def get_instructive_patterns() -> List[str]:
        """获取实施导向模式"""
        return [
            "实施", "教程", "步骤", "方法", "技巧", "购买", "在哪里买", "获取", "制作",
            "how to", "guide", "step by step", "where to buy", "make", "build"
        ]


class EnhancementTemplates:
    """查询增强模板管理类"""
    
    @staticmethod
    def get_default_templates() -> Dict[str, List[str]]:
        """获取默认查询增强模板"""
        return {
            "knowledge_query": [
                "请详细解释{query}的概念、特点和应用场景",
                "关于{query}，请提供全面的背景信息和相关知识",
                "请从多个角度分析{query}的重要性和影响"
            ],
            "factual_question": [
                "请提供关于{query}的准确事实信息和数据",
                "关于{query}，请给出具体的时间、地点、人物等详细信息",
                "请列出与{query}相关的关键事实和统计数据"
            ],
            "analytical_question": [
                "请深入分析{query}，包括原因、影响和解决方案",
                "关于{query}，请提供多角度的分析和见解",
                "请系统性地分析{query}的各个方面和相互关系"
            ],
            "procedural_question": [
                "请提供{query}的详细步骤和操作指南",
                "关于{query}，请给出清晰的流程和注意事项",
                "请列出{query}的具体方法和最佳实践"
            ],
            "creative_request": [
                "请根据{query}的要求进行创意创作",
                "关于{query}，请发挥创意并提供独特的见解",
                "请以创新的方式回应{query}的需求"
            ]
        }


# 导出所有工具类
__all__ = [
    "QueryUtils",
    "IntentPatterns", 
    "EnhancementTemplates"
]
