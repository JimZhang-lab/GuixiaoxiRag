"""
意图识别工具函数
"""
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


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
            # 如果是教育/防范导向，降低风险
            if has_edu and not has_instr:
                risk_score += 0.3
            else:
                risk_score += 1.2  # 明显非法且有实施导向
        
        # 可疑模式
        suspicious_patterns = [
            r"如何.*违法",
            r"怎样.*犯罪", 
            r"教我.*非法",
            r"制作.*毒品",
            r"购买.*枪支",
            r"(如何|怎么|怎样).*实施",
            r"how to.*illegal",
            r"where to buy.*drugs"
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
        return [
            "如何识别和防范相关风险？",
            "遇到类似情况该如何求助和举报？",
            "相关法律风险与合规解读"
        ]
