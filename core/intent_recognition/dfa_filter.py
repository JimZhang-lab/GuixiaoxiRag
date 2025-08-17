"""
DFA（确定有限状态自动机）敏感词过滤器
优化版本 - 适配项目架构和性能要求
"""
import re
from typing import Set, List, Tuple, Dict, Any
from pathlib import Path
from common.logging_utils import logger_manager

logger = logger_manager.get_logger("dfa_filter")


class DFAFilter:
    """DFA敏感词过滤器"""
    
    def __init__(self, case_sensitive: bool = False, enable_fuzzy_match: bool = True):
        self.case_sensitive = case_sensitive
        self.enable_fuzzy_match = enable_fuzzy_match
        self.root = {}
        self.end_flag = "END"
        self.sensitive_words: Set[str] = set()
        
        # 模糊匹配字符映射
        self.fuzzy_map = {
            '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't', '8': 'b',
            '@': 'a', '$': 's', '!': 'i', '|': 'l', '+': 't',
            '０': 'o', '１': 'i', '３': 'e', '４': 'a', '５': 's', '７': 't', '８': 'b',
            '零': '0', '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
            '六': '6', '七': '7', '八': '8', '九': '9',
            '＠': 'a', '＄': 's', '！': 'i', '｜': 'l', '＋': 't'
        }
    
    def load_from_file(self, file_path: str) -> int:
        """从文件加载敏感词"""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"敏感词文件不存在: {file_path}")
                return 0
            
            count = 0
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    word = line if self.case_sensitive else line.lower()
                    self.add_word(word)
                    count += 1
            
            logger.info(f"从文件 {file_path} 加载 {count} 个敏感词")
            return count
            
        except Exception as e:
            logger.error(f"加载敏感词文件失败: {e}")
            return 0
    
    def load_from_directory(self, dir_path: str) -> int:
        """从目录加载所有敏感词文件"""
        try:
            path = Path(dir_path)
            if not path.exists() or not path.is_dir():
                logger.warning(f"敏感词目录不存在: {dir_path}")
                return 0
            
            total_count = 0
            extensions = {'.txt', '.csv', '.dat'}
            
            for file_path in path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in extensions:
                    logger.debug(f"加载敏感词文件: {file_path.name}")
                    count = self.load_from_file(str(file_path))
                    total_count += count
            
            logger.info(f"从目录 {dir_path} 总共加载 {total_count} 个敏感词")
            return total_count
            
        except Exception as e:
            logger.error(f"加载敏感词目录失败: {e}")
            return 0
    
    def add_word(self, word: str):
        """添加敏感词到DFA树"""
        if not word or not word.strip():
            return
        
        word = word.strip()
        if not self.case_sensitive:
            word = word.lower()
        
        self.sensitive_words.add(word)
        
        # 构建DFA树
        current = self.root
        for char in word:
            if char not in current:
                current[char] = {}
            current = current[char]
        current[self.end_flag] = True
    
    def add_words(self, words: List[str]):
        """批量添加敏感词"""
        for word in words:
            self.add_word(word)
    
    def _normalize_text(self, text: str) -> str:
        """文本标准化"""
        if not self.case_sensitive:
            text = text.lower()
        
        if self.enable_fuzzy_match:
            for old_char, new_char in self.fuzzy_map.items():
                text = text.replace(old_char, new_char)
        
        return text
    
    def search(self, text: str) -> List[Tuple[int, int, str]]:
        """搜索文本中的敏感词"""
        if not text or not self.root:
            return []
        
        text = self._normalize_text(text)
        results = []
        text_length = len(text)
        
        for i in range(text_length):
            current = self.root
            j = i
            
            while j < text_length and text[j] in current:
                current = current[text[j]]
                j += 1
                
                if self.end_flag in current:
                    matched_word = text[i:j]
                    results.append((i, j, matched_word))
        
        return results
    
    def contains_sensitive(self, text: str) -> bool:
        """检查文本是否包含敏感词"""
        return len(self.search(text)) > 0
    
    def filter_text(self, text: str, replacement: str = "*") -> str:
        """过滤文本中的敏感词"""
        if not text:
            return text
        
        matches = self.search(text)
        if not matches:
            return text
        
        filtered_text = text
        for start, end, word in reversed(matches):
            replace_len = end - start
            filtered_text = (
                filtered_text[:start] + 
                replacement * replace_len + 
                filtered_text[end:]
            )
        
        return filtered_text
    
    def get_sensitive_words(self, text: str) -> List[str]:
        """获取文本中的敏感词列表"""
        matches = self.search(text)
        return [word for _, _, word in matches]
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """分析文本的敏感词情况"""
        matches = self.search(text)
        sensitive_words = [word for _, _, word in matches]
        
        return {
            "has_sensitive": len(matches) > 0,
            "sensitive_count": len(matches),
            "sensitive_words": list(set(sensitive_words)),
            "matches": matches,
            "risk_level": self._calculate_risk_level(matches),
            "filtered_text": self.filter_text(text)
        }
    
    def _calculate_risk_level(self, matches: List[Tuple[int, int, str]]) -> str:
        """计算风险级别"""
        if not matches:
            return "safe"
        
        count = len(matches)
        if count >= 3:
            return "high"
        elif count >= 2:
            return "medium"
        else:
            return "low"
    
    def get_stats(self) -> Dict[str, Any]:
        """获取过滤器统计信息"""
        return {
            "total_words": len(self.sensitive_words),
            "case_sensitive": self.case_sensitive,
            "fuzzy_match": self.enable_fuzzy_match,
            "tree_nodes": self._count_tree_nodes()
        }
    
    def _count_tree_nodes(self) -> int:
        """计算DFA树节点数量"""
        def count_nodes(node):
            count = 1
            for key, child in node.items():
                if key != self.end_flag and isinstance(child, dict):
                    count += count_nodes(child)
            return count
        
        return count_nodes(self.root) if self.root else 0
    
    def clear(self):
        """清空过滤器"""
        self.root = {}
        self.sensitive_words.clear()


class SensitiveWordManager:
    """敏感词管理器"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.dfa_filter = None

        # 教育导向关键词
        self.educational_patterns = [
            "防范", "避免", "识别", "辨别", "举报", "报警", "危害", "风险", "法律后果",
            "合规", "合法", "合规要求", "不良后果", "如何远离", "不该做", "违法与否",
            "how to avoid", "how to report", "how to identify", "risk", "legal consequences"
        ]

    def initialize(self, base_path: str = "core/intent_recognition/sensitive_vocabulary"):
        """初始化敏感词过滤器"""
        try:
            # 创建DFA过滤器
            dfa_config = self.config.get("dfa", {})
            self.dfa_filter = DFAFilter(
                case_sensitive=dfa_config.get("case_sensitive", False),
                enable_fuzzy_match=dfa_config.get("enable_fuzzy_match", True)
            )

            # 加载敏感词
            vocab_path = Path(base_path)

            if vocab_path.is_file():
                count = self.dfa_filter.load_from_file(str(vocab_path))
            elif vocab_path.is_dir():
                count = self.dfa_filter.load_from_directory(str(vocab_path))
            else:
                logger.warning(f"敏感词路径不存在: {vocab_path}")
                count = 0

            logger.info(f"敏感词过滤器初始化完成，加载 {count} 个敏感词")
            return count > 0

        except Exception as e:
            logger.error(f"敏感词过滤器初始化失败: {e}")
            return False

    def check_content_safety(self, text: str) -> Dict[str, Any]:
        """检查内容安全性"""
        if not self.dfa_filter:
            logger.warning("DFA过滤器未初始化")
            return {
                "is_safe": True,
                "safety_level": "safe",
                "risk_factors": [],
                "confidence": 0.5,
                "reason": "过滤器未初始化"
            }

        # DFA分析
        analysis = self.dfa_filter.analyze_text(text)

        # 检查教育导向
        text_lower = text.lower()
        has_educational_intent = any(
            pattern.lower() in text_lower for pattern in self.educational_patterns
        )

        # 额外检查教育性表达
        educational_expressions = [
            "如何识别", "如何防范", "如何避免", "如何预防", "如何举报",
            "怎样识别", "怎样防范", "怎样避免", "怎样预防", "怎样举报",
            "怎么识别", "怎么防范", "怎么避免", "怎么预防", "怎么举报",
            "的危害", "的风险", "的后果", "有什么危害", "有什么风险",
            "how to avoid", "how to prevent", "how to identify", "how to report"
        ]

        if not has_educational_intent:
            has_educational_intent = any(
                expr in text_lower for expr in educational_expressions
            )

        # 判断安全级别
        if not analysis["has_sensitive"]:
            safety_level = "safe"
            is_safe = True
        elif has_educational_intent:
            if analysis["risk_level"] == "low":
                safety_level = "safe"
                is_safe = True
            else:
                safety_level = "suspicious"
                is_safe = False
        else:
            risk_level = analysis["risk_level"]
            if risk_level == "high":
                safety_level = "illegal"
            elif risk_level == "medium":
                safety_level = "unsafe"
            else:
                safety_level = "suspicious"
            is_safe = False

        # 生成风险因素
        risk_factors = []
        if analysis["sensitive_words"]:
            risk_factors.append(f"检测到敏感词: {', '.join(analysis['sensitive_words'])}")

        return {
            "is_safe": is_safe,
            "safety_level": safety_level,
            "risk_factors": risk_factors,
            "confidence": 0.9,
            "reason": "DFA敏感词检测",
            "sensitive_words": analysis["sensitive_words"],
            "filtered_text": analysis["filtered_text"]
        }


# 导出
__all__ = ["DFAFilter", "SensitiveWordManager"]
