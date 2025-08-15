"""
查询处理器 - 基于大模型的意图识别、意图补充、意图修复和内容过滤
"""
import re
import logging
import json
from typing import Dict, List, Optional, Tuple, Any
import asyncio

import sys
from pathlib import Path

# 添加父目录到路径
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from core.models import QueryIntentType, ContentSafetyLevel, QueryAnalysisResult
from core.utils import QueryUtils
from core.dfa_filter import SensitiveWordManager
from config.settings import Config

logger = logging.getLogger(__name__)


def extracted_think_and_answer(response_content):
    """提取大模型响应中的思考过程和最终答案"""
    think_str = response_content.split("<think>")[1]
    think_str = think_str.split("</think>")[0].strip()
    answer_str = response_content.split("</think>")[1].strip()
    return think_str, answer_str


class QueryProcessor:
    """基于大模型的查询处理器"""

    def __init__(self, config: Config = None, llm_func=None):
        self.config = config or Config()
        self.llm_func = llm_func

        # 初始化DFA敏感词管理器
        self.sensitive_word_manager = SensitiveWordManager(self.config.safety.model_dump())
        self.sensitive_word_manager.initialize()

        # 从配置加载数据
        self.educational_intent_patterns = self._get_default_educational_patterns()

        # 意图识别模式
        self.intent_patterns = self._load_intent_patterns()

        # 查询增强模板（内置）
        self.enhancement_templates = self._get_default_enhancement_templates()

        # 置信度阈值
        self.confidence_threshold = self.config.intent.confidence_threshold

        # 大模型提示词模板
        self.safety_check_prompt = """
你是一个内容安全审核专家。请分析以下查询是否涉及违法违规内容。

查询内容："{query}"

请从以下维度进行分析：
1. 是否涉及违法犯罪活动（如赌博、毒品、诈骗、暴力等）
2. 是否涉及不当内容（如色情、仇恨言论等）
3. 查询意图是正向教育/防范，还是负面实施/教程

请以JSON格式返回分析结果：
{{
    "is_safe": true/false,
    "safety_level": "safe/suspicious/unsafe/illegal",
    "risk_factors": ["风险因素1", "风险因素2"],
    "intent_direction": "educational/instructive/neutral",
    "confidence": 0.95,
    "reason": "详细分析原因"
}}

注意：
- 对于"如何防范/识别/举报"等正向教育内容，应标记为安全
- 对于"如何实施/制作/购买"等可能的违法指导，应标记为不安全
- 严格按照JSON格式返回，不要包含其他内容
"""

        self.intent_analysis_prompt = """
你是一个查询意图分析专家。请分析以下查询的具体意图类型。

查询内容："{query}"

可选的意图类型：
1. knowledge_query: 知识查询（如"什么是人工智能"）
2. factual_question: 事实性问题（如"谁发明了电话"）
3. analytical_question: 分析性问题（如"为什么会发生这种现象"）
4. procedural_question: 程序性问题（如"如何操作某个软件"）
5. creative_request: 创意请求（如"写一首诗"）
6. greeting: 问候（如"你好"）
7. unclear: 意图不明确
8. illegal_content: 非法内容

请以JSON格式返回分析结果：
{{
    "intent_type": "knowledge_query",
    "confidence": 0.95,
    "reason": "用户询问某个概念的定义，属于知识查询",
    "keywords": ["关键词1", "关键词2"]
}}

注意：
- 严格按照JSON格式返回，不要包含其他内容
- confidence 应该是 0-1 之间的数值
"""

        self.query_enhancement_prompt = """
你是一个查询优化专家。请分析以下查询是否需要增强，如果需要，请提供优化后的查询。

原始查询："{query}"
意图类型：{intent_type}
安全级别：{safety_level}

请考虑以下优化方向：
1. 补充缺失的关键信息
2. 明确查询的具体范围
3. 添加相关的上下文
4. 优化表达方式

请以JSON格式返回结果：
{{
    "should_enhance": true/false,
    "enhanced_query": "优化后的查询（如果需要优化）",
    "enhancement_reason": "优化原因",
    "suggestions": ["建议1", "建议2"]
}}

注意：
- 只有在确实能改进查询质量时才建议增强
- 严格按照JSON格式返回，不要包含其他内容
"""



    def _load_intent_patterns(self) -> Dict[QueryIntentType, List[str]]:
        """加载意图识别模式"""
        return {
            QueryIntentType.KNOWLEDGE_QUERY: [
                r"什么是", r"介绍一下", r"解释", r"定义", r"概念",
                r"what is", r"explain", r"define", r"describe"
            ],
            QueryIntentType.FACTUAL_QUESTION: [
                r"谁是", r"何时", r"哪里", r"多少", r"几个",
                r"who is", r"when", r"where", r"how many", r"how much"
            ],
            QueryIntentType.ANALYTICAL_QUESTION: [
                r"为什么", r"如何", r"怎样", r"分析", r"比较", r"评价",
                r"why", r"how", r"analyze", r"compare", r"evaluate"
            ],
            QueryIntentType.PROCEDURAL_QUESTION: [
                r"步骤", r"流程", r"方法", r"操作", r"教程", r"指南",
                r"steps", r"process", r"method", r"tutorial", r"guide"
            ],
            QueryIntentType.CREATIVE_REQUEST: [
                r"创作", r"写", r"设计", r"生成", r"创造", r"编写",
                r"create", r"write", r"design", r"generate", r"compose"
            ],
            QueryIntentType.GREETING: [
                r"你好", r"您好", r"hi", r"hello", r"嗨", r"早上好", r"晚上好",
                r"good morning", r"good evening", r"good afternoon"
            ]
        }

    def _get_default_enhancement_templates(self) -> Dict[QueryIntentType, str]:
        """获取默认查询增强模板"""
        return {
            QueryIntentType.KNOWLEDGE_QUERY: "请详细解释{query}的概念、特点和应用场景",
            QueryIntentType.FACTUAL_QUESTION: "关于{query}，请提供准确的事实信息和相关背景",
            QueryIntentType.ANALYTICAL_QUESTION: "请深入分析{query}，包括原因、影响和相关因素",
            QueryIntentType.PROCEDURAL_QUESTION: "请提供{query}的详细步骤和操作指南",
            QueryIntentType.CREATIVE_REQUEST: "请根据{query}的要求进行创意创作"
        }

    async def process_query(self, query: str, context: Optional[Dict] = None) -> QueryAnalysisResult:
        """基于大模型的查询处理"""
        try:
            logger.info(f"开始处理查询: {query[:50]}...")

            # 1. 查询清理和标准化
            processed_query = await self._clean_and_normalize_query(query)
            logger.debug(f"查询清理完成: {processed_query[:50]}...")

            # 2. 使用大模型进行安全检查
            logger.debug("开始安全检查")
            safety_result = await self._llm_safety_check(processed_query)
            logger.info(f"安全检查完成: {safety_result.get('safety_level', 'unknown')}, 安全: {safety_result.get('is_safe', False)}")

            # 检查安全结果格式并统一处理
            is_safe = safety_result.get("is_safe")
            if is_safe is None:
                # 兼容旧格式，通过should_reject判断
                is_safe = not safety_result.get("should_reject", False)

            # 确定安全级别
            safety_level_str = safety_result.get("safety_level", "safe")
            try:
                safety_level = ContentSafetyLevel(safety_level_str)
            except ValueError:
                logger.warning(f"无效的安全级别: {safety_level_str}，使用默认值")
                safety_level = ContentSafetyLevel.SUSPICIOUS

            # 如果查询不安全，标记为拒绝并生成安全提示
            if not is_safe or safety_level in [ContentSafetyLevel.UNSAFE, ContentSafetyLevel.ILLEGAL]:
                logger.info("查询被标记为不安全，返回拒绝结果")

                # 生成安全提示和替代建议
                safety_tips = await self._generate_safety_tips(processed_query, safety_level)
                safe_alternatives = await self._generate_safe_alternatives(processed_query)

                return QueryAnalysisResult(
                    original_query=query,
                    processed_query=processed_query,
                    intent_type=QueryIntentType.ILLEGAL_CONTENT,
                    safety_level=safety_level,
                    confidence=safety_result.get("confidence", 0.9),
                    suggestions=[],
                    risk_factors=safety_result.get("risk_factors", []),
                    enhanced_query=None,
                    should_reject=True,
                    rejection_reason=safety_result.get("reason", "查询内容涉及违法违规信息，无法处理"),
                    safety_tips=safety_tips,
                    safe_alternatives=safe_alternatives
                )

            # 3. 意图识别
            logger.debug("开始意图识别")
            intent_result = await self._llm_intent_analysis(processed_query)
            logger.info(f"意图识别完成: {intent_result.get('intent_type', 'unknown')}")

            # 确定意图类型
            intent_type_str = intent_result.get("intent_type", "unclear")
            try:
                intent_type = QueryIntentType(intent_type_str)
            except ValueError:
                logger.warning(f"无效的意图类型: {intent_type_str}，使用unclear")
                intent_type = QueryIntentType.UNCLEAR

            # 4. 查询增强
            logger.debug("开始查询增强")
            enhancement_result = await self._llm_query_enhancement(
                processed_query, intent_type.value, safety_level.value
            )
            logger.info(f"查询增强完成: 是否增强={enhancement_result.get('should_enhance', False)}")

            # 提取增强查询
            enhanced_query = None
            if enhancement_result.get("should_enhance"):
                enhanced_query = enhancement_result.get("enhanced_query")

            # 5. 生成建议
            suggestions = intent_result.get("keywords", []) + enhancement_result.get("suggestions", [])

            result = QueryAnalysisResult(
                original_query=query,
                processed_query=processed_query,
                intent_type=intent_type,
                safety_level=safety_level,
                confidence=min(safety_result.get("confidence", 0.8), intent_result.get("confidence", 0.8)),
                suggestions=suggestions,
                risk_factors=safety_result.get("risk_factors", []),
                enhanced_query=enhanced_query,
                should_reject=False,
                rejection_reason=None,
                safety_tips=[],
                safe_alternatives=[]
            )

            logger.info("查询处理完成")
            return result

        except Exception as e:
            logger.error(f"查询处理失败: {e}")
            return QueryAnalysisResult(
                original_query=query,
                processed_query=query,
                intent_type=QueryIntentType.UNCLEAR,
                safety_level=ContentSafetyLevel.SUSPICIOUS,
                confidence=0.0,
                suggestions=[],
                risk_factors=["处理异常"],
                should_reject=True,
                rejection_reason="查询处理过程中发生错误",
                safety_tips=[],
                safe_alternatives=[]
            )

    async def _clean_and_normalize_query(self, query: str) -> str:
        """清理和标准化查询"""
        return await QueryUtils.clean_and_normalize_query(query)

    async def _llm_safety_check(self, query: str) -> Dict[str, Any]:
        """使用大模型进行安全检查"""
        try:
            if not self.llm_func:
                logger.info("LLM函数未设置，使用规则检查")
                return await self._check_content_safety(query)

            prompt = self.safety_check_prompt.format(query=query)
            logger.debug(f"发送安全检查提示词: {prompt[:100]}...")

            response = await self.llm_func(prompt)
            logger.debug(f"LLM安全检查响应: {response[:200]}...")

            # 检查响应是否为空
            if not response or not response.strip():
                logger.warning("LLM返回空响应，使用规则检查")
                return await self._check_content_safety(query)

            # 处理包含 <think> 标签的响应
            try:
                if "<think>" in response and "</think>" in response:
                    logger.debug("检测到think标签，提取最终答案")
                    think_str, answer_str = extracted_think_and_answer(response)
                    logger.debug(f"思考过程: {think_str[:100]}...")
                    logger.debug(f"最终答案: {answer_str[:100]}...")
                    response = answer_str
            except Exception as e:
                logger.warning(f"提取think和answer失败: {e}，使用原始响应")

            # 解析JSON响应
            import json
            try:
                # 尝试提取JSON部分（如果响应包含其他内容）
                response_clean = response.strip()
                if response_clean.startswith('```json'):
                    response_clean = response_clean[7:]
                if response_clean.endswith('```'):
                    response_clean = response_clean[:-3]
                response_clean = response_clean.strip()

                result = json.loads(response_clean)

                # 验证必要字段
                is_safe = result.get("is_safe", True)
                safety_level = result.get("safety_level", "safe")

                return {
                    "is_safe": is_safe,
                    "safety_level": safety_level,
                    "risk_factors": result.get("risk_factors", []),
                    "confidence": result.get("confidence", 0.8),
                    "reason": result.get("reason", "大模型安全检查")
                }
            except json.JSONDecodeError as je:
                logger.warning(f"大模型返回非JSON格式: {response[:200]}..., 错误: {je}")
                # 回退到规则检查
                return await self._check_content_safety(query)

        except Exception as e:
            logger.error(f"大模型安全检查失败: {e}")
            # 回退到规则检查
            return await self._check_content_safety(query)

    async def _check_content_safety(self, query: str) -> Dict[str, Any]:
        """检查内容安全性（DFA过滤器）"""
        if not self.sensitive_word_manager:
            logger.warning("敏感词管理器未初始化")
            return {
                "is_safe": True,
                "safety_level": "safe",
                "risk_factors": [],
                "confidence": 0.5,
                "reason": "敏感词管理器未初始化"
            }

        # 使用DFA过滤器检查
        return self.sensitive_word_manager.check_content_safety(query)

    async def _llm_intent_analysis(self, query: str) -> Dict[str, Any]:
        """使用大模型进行意图分析"""
        try:
            if not self.llm_func:
                logger.info("LLM函数未设置，使用规则识别")
                intent_type = await self._identify_intent(query)
                return {
                    "intent_type": intent_type.value,
                    "confidence": 0.7,
                    "reason": "规则匹配",
                    "keywords": []
                }

            prompt = self.intent_analysis_prompt.format(query=query)
            logger.debug(f"发送意图分析提示词: {prompt[:100]}...")

            response = await self.llm_func(prompt)
            logger.debug(f"LLM意图分析响应: {response[:200]}...")

            # 检查响应是否为空
            if not response or not response.strip():
                logger.warning("LLM返回空响应，使用规则识别")
                intent_type = await self._identify_intent(query)
                return {
                    "intent_type": intent_type.value,
                    "confidence": 0.7,
                    "reason": "规则匹配（空响应）",
                    "keywords": []
                }

            # 处理包含 <think> 标签的响应
            try:
                if "<think>" in response and "</think>" in response:
                    logger.debug("检测到think标签，提取最终答案")
                    think_str, answer_str = extracted_think_and_answer(response)
                    logger.debug(f"思考过程: {think_str[:100]}...")
                    logger.debug(f"最终答案: {answer_str[:100]}...")
                    response = answer_str
            except Exception as e:
                logger.warning(f"提取think和answer失败: {e}，使用原始响应")

            # 解析JSON响应
            import json
            try:
                # 清理响应格式
                response_clean = response.strip()
                if response_clean.startswith('```json'):
                    response_clean = response_clean[7:]
                if response_clean.endswith('```'):
                    response_clean = response_clean[:-3]
                response_clean = response_clean.strip()

                result = json.loads(response_clean)

                # 验证intent_type是否有效
                intent_type_str = result.get("intent_type", "unclear")
                try:
                    QueryIntentType(intent_type_str)  # 验证是否为有效的枚举值
                except ValueError:
                    logger.warning(f"无效的意图类型: {intent_type_str}，使用unclear")
                    intent_type_str = "unclear"

                return {
                    "intent_type": intent_type_str,
                    "confidence": result.get("confidence", 0.8),
                    "reason": result.get("reason", "大模型意图分析"),
                    "keywords": result.get("keywords", [])
                }
            except json.JSONDecodeError as je:
                logger.warning(f"大模型返回非JSON格式: {response[:200]}..., 错误: {je}")
                # 回退到规则识别
                intent_type = await self._identify_intent(query)
                return {
                    "intent_type": intent_type.value,
                    "confidence": 0.7,
                    "reason": "规则匹配（JSON解析失败）",
                    "keywords": []
                }

        except Exception as e:
            logger.error(f"大模型意图分析失败: {e}")
            # 回退到规则识别
            intent_type = await self._identify_intent(query)
            return {
                "intent_type": intent_type.value,
                "confidence": 0.7,
                "reason": f"规则匹配（异常: {e}）",
                "keywords": []
            }

    async def _identify_intent(self, query: str) -> QueryIntentType:
        """识别查询意图（规则回退）"""
        query_lower = query.lower()

        # 特殊：若包含教育/防范导向词，优先视为知识查询或程序性问题（正向）
        if any(term.lower() in query_lower for term in self.educational_intent_patterns):
            # 更偏向知识/程序说明
            if any(w in query_lower for w in ["如何", "怎样", "怎么", "how"]):
                return QueryIntentType.PROCEDURAL_QUESTION
            return QueryIntentType.KNOWLEDGE_QUERY

        # 检查每种意图类型的模式
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent_type

        return QueryIntentType.UNCLEAR

    async def _llm_query_enhancement(self, query: str, intent_type: str, safety_level: str) -> Dict[str, Any]:
        """使用大模型进行查询增强"""
        try:
            if not self.llm_func:
                # 回退到模板增强
                enhanced = await self._enhance_query(query, QueryIntentType(intent_type))
                return {
                    "enhanced_query": enhanced,
                    "should_enhance": enhanced is not None,
                    "enhancement_reason": "模板增强",
                    "suggestions": []
                }

            prompt = self.query_enhancement_prompt.format(
                query=query,
                intent_type=intent_type,
                safety_level=safety_level
            )
            response = await self.llm_func(prompt)

            # 处理包含 <think> 标签的响应
            try:
                if "<think>" in response and "</think>" in response:
                    logger.debug("检测到think标签，提取最终答案")
                    think_str, answer_str = extracted_think_and_answer(response)
                    logger.debug(f"思考过程: {think_str[:100]}...")
                    logger.debug(f"最终答案: {answer_str[:100]}...")
                    response = answer_str
            except Exception as e:
                logger.warning(f"提取think和answer失败: {e}，使用原始响应")

            # 解析JSON响应
            import json
            try:
                # 清理响应格式
                response_clean = response.strip()
                if response_clean.startswith('```json'):
                    response_clean = response_clean[7:]
                if response_clean.endswith('```'):
                    response_clean = response_clean[:-3]
                response_clean = response_clean.strip()

                result = json.loads(response_clean)
                return {
                    "enhanced_query": result.get("enhanced_query") if result.get("should_enhance") else None,
                    "should_enhance": result.get("should_enhance", False),
                    "enhancement_reason": result.get("enhancement_reason", "大模型增强"),
                    "suggestions": result.get("suggestions", [])
                }
            except json.JSONDecodeError as je:
                logger.warning(f"大模型返回非JSON格式: {response[:200]}..., 错误: {je}")
                # 回退到模板增强
                enhanced = await self._enhance_query(query, QueryIntentType(intent_type))
                return {
                    "enhanced_query": enhanced,
                    "should_enhance": enhanced is not None,
                    "enhancement_reason": "模板增强（JSON解析失败）",
                    "suggestions": []
                }

        except Exception as e:
            logger.error(f"大模型查询增强失败: {e}")
            # 回退到模板增强
            enhanced = await self._enhance_query(query, QueryIntentType(intent_type))
            return {
                "enhanced_query": enhanced,
                "should_enhance": enhanced is not None,
                "enhancement_reason": f"模板增强（异常: {e}）",
                "suggestions": []
            }

    async def _enhance_query(self, query: str, intent_type: QueryIntentType) -> Optional[str]:
        """使用模板增强查询"""
        template = self.enhancement_templates.get(intent_type)
        if template:
            return template.format(query=query)
        return None

    async def _generate_safety_tips(self, query: str, safety_level: ContentSafetyLevel) -> List[str]:
        """生成安全提示"""
        return QueryUtils.generate_default_safety_tips(safety_level.value)

    async def _generate_safe_alternatives(self, query: str) -> List[str]:
        """生成安全替代建议"""
        return QueryUtils.generate_default_alternatives(query)

    def _get_default_educational_patterns(self) -> List[str]:
        """获取默认教育导向模式"""
        return [
            "防范", "避免", "识别", "辨别", "举报", "报警", "危害", "风险", "法律后果",
            "合规", "合法", "合规要求", "不良后果", "如何远离", "不该做", "违法与否",
            "how to avoid", "how to report", "how to identify", "risk", "legal consequences"
        ]
