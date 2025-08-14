"""
查询处理器 - 基于大模型的意图识别、意图补充、意图修复和内容过滤
"""
import re
import logging
import json
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)


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


def extracted_think_and_answer(response_content):
    think_str = response_content.split("<think>")[1]
    think_str = think_str.split("</think>")[0].strip()
    answer_str = response_content.split("</think>")[1].strip()
    return think_str, answer_str
    
class QueryProcessor:
    """基于大模型的查询处理器"""

    def __init__(self, llm_func=None):
        self.llm_func = llm_func
        self.illegal_keywords = self._load_illegal_keywords()
        self.intent_patterns = self._load_intent_patterns()
        self.enhancement_templates = self._load_enhancement_templates()
        # 方向性意图：正向教育/防范 与 负面实施/教程
        self.educational_intent_patterns = [
            "防范", "避免", "识别", "辨别", "举报", "报警", "危害", "风险", "法律后果",
            "合规", "合法", "合规要求", "不良后果", "如何远离", "不该做", "违法与否",
            "how to avoid", "how to report", "how to identify", "risk", "legal consequences"
        ]
        self.instructive_intent_patterns = [
            "实施", "教程", "步骤", "方法", "技巧", "购买", "在哪里买", "获取", "制作",
            "how to", "guide", "step by step", "where to buy", "make", "build"
        ]

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

意图类型定义：
- knowledge_query: 知识查询（什么是、介绍、解释、定义等）
- factual_question: 事实性问题（谁、何时、哪里、多少等）
- analytical_question: 分析性问题（为什么、如何分析、比较、评价等）
- procedural_question: 程序性问题（步骤、流程、方法、操作等）
- creative_request: 创意请求（创作、写作、设计、生成等）
- greeting: 问候（你好、再见等）
- unclear: 意图不明确

请以JSON格式返回分析结果：
{{
    "intent_type": "knowledge_query",
    "confidence": 0.95,
    "reason": "分析原因",
    "keywords": ["关键词1", "关键词2"]
}}

严格按照JSON格式返回，不要包含其他内容。
"""

        self.query_enhancement_prompt = """
你是一个查询优化专家。请根据查询意图对以下查询进行优化和增强。

原始查询："{query}"
意图类型：{intent_type}
安全级别：{safety_level}

优化原则：
1. 如果是安全的知识查询，可以扩展为更详细、更全面的问题
2. 如果涉及敏感内容，不要进行增强
3. 保持查询的核心意图不变
4. 使查询更加清晰、具体

请以JSON格式返回优化结果：
{{
    "enhanced_query": "优化后的查询",
    "should_enhance": true/false,
    "enhancement_reason": "优化原因",
    "suggestions": ["建议1", "建议2"]
}}

如果不适合增强，请设置should_enhance为false。
严格按照JSON格式返回，不要包含其他内容。
"""

    def _find_illegal_hits(self, query_lower: str) -> List[str]:
        """查找命中的非法关键词"""
        hits: List[str] = []
        for _, keywords in self.illegal_keywords.items():
            for kw in keywords:
                if kw.lower() in query_lower:
                    hits.append(kw)
        # 去重
        return list(dict.fromkeys(hits))

    def _has_educational_intent(self, query_lower: str) -> bool:
        return any(term.lower() in query_lower for term in self.educational_intent_patterns)

    def _has_instructive_intent(self, query_lower: str) -> bool:
        return any(term.lower() in query_lower for term in self.instructive_intent_patterns)
    
    def _load_illegal_keywords(self) -> Dict[str, List[str]]:
        """加载非法关键词库"""
        return {
            "gambling": [
                "赌博", "赌场", "赌钱", "赌注", "博彩", "彩票作弊", "赌球", "赌马",
                "网络赌博", "地下赌场", "赌博网站", "赌博平台", "赌博技巧",
                "gambling", "casino", "betting", "poker", "blackjack"
            ],
            "drugs": [
                "毒品", "吸毒", "贩毒", "制毒", "海洛因", "可卡因", "冰毒", "摇头丸",
                "大麻", "鸦片", "吗啡", "芬太尼", "毒品交易", "毒品制作",
                "drugs", "cocaine", "heroin", "marijuana", "methamphetamine"
            ],
            "pornography": [
                "色情", "黄色", "淫秽", "性交易", "卖淫", "嫖娼", "色情网站",
                "成人内容", "性服务", "色情视频", "裸体", "性爱", "裸聊",
                "pornography", "adult content", "sexual services", "prostitution"
            ],
            "violence": [
                "暴力", "杀人", "谋杀", "自杀", "恐怖主义", "爆炸", "枪支", "武器",
                "伤害他人", "暴力犯罪", "恐怖袭击", "自残", "虐待",
                "violence", "murder", "terrorism", "weapons", "suicide"
            ],
            "fraud": [
                "诈骗", "欺诈", "骗钱", "传销", "非法集资", "洗钱", "假币",
                "信用卡诈骗", "网络诈骗", "电信诈骗", "金融诈骗", "敲诈勒索",
                "fraud", "scam", "money laundering", "pyramid scheme"
            ],
            "illegal_loans": [
                "裸贷", "校园贷", "套路贷", "高利贷", "砍头息", "黑贷", "暴力催收", "软暴力",
                "非法放贷", "非法讨债"
            ],
            "others": [
                "制作炸弹", "如何制爆", "买枪", "如何买枪"
            ]
        }
    
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
                r"你好", r"您好", r"早上好", r"晚上好", r"再见",
                r"hello", r"hi", r"good morning", r"good evening", r"goodbye"
            ]
        }
    
    def _load_enhancement_templates(self) -> Dict[QueryIntentType, List[str]]:
        """加载查询增强模板"""
        return {
            QueryIntentType.KNOWLEDGE_QUERY: [
                "请详细解释{query}的概念、特点和应用场景",
                "关于{query}，请提供全面的背景信息和相关知识",
                "请从多个角度分析{query}的重要性和影响"
            ],
            QueryIntentType.FACTUAL_QUESTION: [
                "请提供关于{query}的准确事实信息和数据",
                "关于{query}，请给出具体的时间、地点、人物等详细信息",
                "请列出与{query}相关的关键事实和统计数据"
            ],
            QueryIntentType.ANALYTICAL_QUESTION: [
                "请深入分析{query}，包括原因、影响和解决方案",
                "关于{query}，请提供多角度的分析和见解",
                "请系统性地分析{query}的各个方面和相互关系"
            ],
            QueryIntentType.PROCEDURAL_QUESTION: [
                "请提供{query}的详细步骤和操作指南",
                "关于{query}，请给出清晰的流程和注意事项",
                "请列出{query}的具体方法和最佳实践"
            ]
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

            # 如果不安全，直接返回拒绝结果
            if not is_safe:
                logger.info("查询被标记为不安全，返回拒绝结果")
                safety_tips = [
                    "请遵守法律法规与平台使用规范，不要寻求或传播违法内容",
                    "若遇到疑似非法行为，建议保留证据并向警方或相关机构举报",
                    "注意个人隐私与财产安全，避免卷入高风险行为"
                ]
                safe_alternatives = await self._generate_safe_alternatives(processed_query)

                # 处理安全级别
                safety_level_str = safety_result.get("safety_level")
                if safety_level_str is None:
                    # 兼容旧格式
                    safety_level = safety_result.get("level", ContentSafetyLevel.SUSPICIOUS)
                else:
                    try:
                        safety_level = ContentSafetyLevel(safety_level_str)
                    except ValueError:
                        logger.warning(f"无效的安全级别: {safety_level_str}")
                        safety_level = ContentSafetyLevel.SUSPICIOUS

                return QueryAnalysisResult(
                    original_query=query,
                    processed_query=processed_query,
                    intent_type=QueryIntentType.ILLEGAL_CONTENT,
                    safety_level=safety_level,
                    confidence=safety_result.get("confidence", 0.5),
                    suggestions=[],
                    risk_factors=safety_result.get("risk_factors", []),
                    enhanced_query=None,
                    should_reject=True,
                    rejection_reason=safety_result.get("reason") or safety_result.get("rejection_reason", "查询内容不符合安全要求"),
                    safety_tips=safety_tips,
                    safe_alternatives=safe_alternatives
                )

            # 3. 使用大模型进行意图识别
            logger.debug("开始意图识别")
            intent_result = await self._llm_intent_analysis(processed_query)
            logger.info(f"意图识别完成: {intent_result.get('intent_type', 'unknown')}")

            try:
                intent_type = QueryIntentType(intent_result["intent_type"])
            except ValueError as e:
                logger.warning(f"无效的意图类型: {intent_result['intent_type']}, 使用unclear: {e}")
                intent_type = QueryIntentType.UNCLEAR

            # 4. 使用大模型进行查询增强
            logger.debug("开始查询增强")
            enhancement_result = await self._llm_query_enhancement(
                processed_query,
                intent_result["intent_type"],
                safety_result["safety_level"]
            )
            logger.info(f"查询增强完成: 是否增强={enhancement_result.get('should_enhance', False)}")

            enhanced_query = enhancement_result["enhanced_query"] if enhancement_result["should_enhance"] else None
            suggestions = enhancement_result["suggestions"]

            # 5. 构建结果
            # 处理安全级别
            safety_level_str = safety_result.get("safety_level")
            if safety_level_str is None:
                safety_level = safety_result.get("level", ContentSafetyLevel.SAFE)
            else:
                try:
                    safety_level = ContentSafetyLevel(safety_level_str)
                except ValueError:
                    logger.warning(f"无效的安全级别: {safety_level_str}")
                    safety_level = ContentSafetyLevel.SAFE

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

    async def _generate_safe_alternatives(self, query: str) -> List[str]:
        """生成安全的替代查询"""
        try:
            if not self.llm_func:
                # 回退到固定模板
                return [
                    "如何识别和防范相关风险？",
                    "遇到类似情况该如何求助和举报？",
                    "相关法律风险与合规解读"
                ]

            prompt = f"""
请为以下被拒绝的查询生成3个安全、正向的替代问法：

原查询："{query}"

要求：
1. 将问题转向识别、防范、举报等正向角度
2. 符合法律法规和道德规范
3. 具有教育意义

请以JSON格式返回：
{{"alternatives": ["替代问法1", "替代问法2", "替代问法3"]}}
"""

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
                return result.get("alternatives", [
                    "如何识别和防范相关风险？",
                    "遇到类似情况该如何求助和举报？",
                    "相关法律风险与合规解读"
                ])
            except json.JSONDecodeError as je:
                logger.warning(f"生成安全替代查询JSON解析失败: {je}")
                return [
                    "如何识别和防范相关风险？",
                    "遇到类似情况该如何求助和举报？",
                    "相关法律风险与合规解读"
                ]

        except Exception as e:
            logger.error(f"生成安全替代查询失败: {e}")
            return [
                "如何识别和防范相关风险？",
                "遇到类似情况该如何求助和举报？",
                "相关法律风险与合规解读"
            ]
    
    async def _check_content_safety(self, query: str) -> Dict[str, Any]:
        """检查内容安全性（区分教育/防范 vs 实施/教程导向）"""
        query_lower = query.lower()
        risk_factors: List[str] = []
        risk_score = 0.0

        hits = self._find_illegal_hits(query_lower)
        has_edu = self._has_educational_intent(query_lower)
        has_instr = self._has_instructive_intent(query_lower)

        # 命中非法主题
        if hits:
            risk_factors.append(f"命中非法主题: {', '.join(hits)}")
            # 如果是教育/防范导向，降低风险，但仍保持警惕，不拒绝
            if has_edu and not has_instr:
                risk_score += 0.3
            else:
                risk_score += 1.2  # 明显非法且有实施导向，强烈拒绝

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
                risk_factors.append(f"包含可疑模式: {pattern}")
                risk_score += 0.5

        # 安全级别与拒绝逻辑
        if risk_score >= 1.0:
            safety_level = ContentSafetyLevel.ILLEGAL
            should_reject = True
            rejection_reason = "查询内容涉及违法违规信息，无法处理"
        elif risk_score >= 0.5:
            # 对教育/防范导向的非法主题，给出“可疑但允许”的结果（不拒绝）
            if has_edu and hits and not has_instr:
                safety_level = ContentSafetyLevel.SUSPICIOUS
                should_reject = False
                rejection_reason = None
            else:
                safety_level = ContentSafetyLevel.UNSAFE
                should_reject = True
                rejection_reason = "查询内容可能涉及不当信息，建议重新表述"
        elif risk_score > 0:
            safety_level = ContentSafetyLevel.SUSPICIOUS
            should_reject = False
            rejection_reason = None
        else:
            safety_level = ContentSafetyLevel.SAFE
            should_reject = False
            rejection_reason = None

        confidence = min(1.0, max(0.0, 1.0 - risk_score * 0.25))

        return {
            "is_safe": not should_reject,
            "safety_level": safety_level.value if hasattr(safety_level, 'value') else str(safety_level),
            "level": safety_level,  # 保持向后兼容
            "confidence": confidence,
            "risk_factors": risk_factors,
            "should_reject": should_reject,
            "rejection_reason": rejection_reason,
            "reason": rejection_reason or "规则检查"
        }
    
    async def _identify_intent(self, query: str) -> QueryIntentType:
        """识别查询意图（区分教育/防范 vs 实施/教程）"""
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

        # 基于查询长度和结构的启发式判断
        if len(query) < 10:
            return QueryIntentType.GREETING
        elif "?" in query or "？" in query:
            if any(word in query_lower for word in ["什么", "什么是", "what", "how"]):
                return QueryIntentType.KNOWLEDGE_QUERY
            else:
                return QueryIntentType.FACTUAL_QUESTION
        else:
            return QueryIntentType.UNCLEAR
    
    async def _clean_and_normalize_query(self, query: str) -> str:
        """清理和标准化查询"""
        # 移除多余的空格和特殊字符
        cleaned = re.sub(r'\s+', ' ', query.strip())
        
        # 移除无意义的前缀
        prefixes_to_remove = [
            "请问", "你好", "您好", "我想问", "我想知道",
            "hello", "hi", "please", "can you"
        ]
        
        for prefix in prefixes_to_remove:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):].strip()
                break
        
        # 标准化标点符号
        cleaned = cleaned.replace("？", "?").replace("！", "!")
        
        return cleaned
    
    async def _enhance_query(self, query: str, intent_type: QueryIntentType) -> Optional[str]:
        """增强查询：避免将可能违规的查询朝“实施/教程”方向引导"""
        # 若包含“实施/教程”等导向词，则避免增强
        ql = query.lower()
        if any(term.lower() in ql for term in self.instructive_intent_patterns):
            return None

        if intent_type in self.enhancement_templates:
            templates = self.enhancement_templates[intent_type]
            if templates:
                # 选择第一个模板进行增强
                template = templates[0]
                enhanced = template.format(query=query)
                return enhanced

        return None
    
    async def _generate_suggestions(self, query: str, intent_type: QueryIntentType) -> List[str]:
        """生成查询建议"""
        suggestions = []
        
        if intent_type == QueryIntentType.UNCLEAR:
            suggestions.extend([
                "请尝试更具体地描述您的问题",
                "您可以提供更多背景信息",
                "建议使用疑问词（什么、如何、为什么等）"
            ])
        elif intent_type == QueryIntentType.KNOWLEDGE_QUERY:
            suggestions.extend([
                "可以询问相关的应用场景",
                "可以了解历史发展过程",
                "可以探讨相关的技术细节"
            ])
        elif intent_type == QueryIntentType.FACTUAL_QUESTION:
            suggestions.extend([
                "可以询问更具体的时间范围",
                "可以了解相关的统计数据",
                "可以探讨影响因素"
            ])
        
        return suggestions


# 创建带有LLM功能的查询处理器
async def create_llm_func(rag_service):
    """创建LLM函数，用于查询处理器"""
    async def llm_func(prompt: str) -> str:
        try:
            logger.debug(f"尝试调用LLM，提示词长度: {len(prompt)}")

            # 检查rag_service是否可用
            if not rag_service:
                logger.warning("rag_service不可用")
                return ""

            # 使用GuiXiaoXiRag的LLM功能
            if hasattr(rag_service, 'rag') and rag_service.rag:
                logger.debug("找到rag实例")

                # 尝试获取LLM模型函数
                if hasattr(rag_service.rag, 'llm_model_func') and rag_service.rag.llm_model_func:
                    logger.debug("使用llm_model_func")
                    llm_func = rag_service.rag.llm_model_func

                    # 检查是否为异步函数
                    import asyncio
                    if asyncio.iscoroutinefunction(llm_func):
                        response = await llm_func(prompt)
                    else:
                        response = llm_func(prompt)

                    logger.debug(f"LLM响应长度: {len(str(response))}")
                    return str(response)

                # 尝试直接使用LLM对象
                elif hasattr(rag_service.rag, 'llm') and rag_service.rag.llm:
                    logger.debug("使用llm对象")
                    llm = rag_service.rag.llm

                    # 尝试不同的调用方式
                    if hasattr(llm, 'agenerate'):
                        logger.debug("使用agenerate方法")
                        response = await llm.agenerate([prompt])
                        return response.generations[0][0].text
                    elif hasattr(llm, 'acall'):
                        logger.debug("使用acall方法")
                        response = await llm.acall(prompt)
                        return str(response)
                    elif hasattr(llm, '__call__'):
                        logger.debug("使用__call__方法")
                        response = llm(prompt)
                        return str(response)
                    else:
                        logger.warning("LLM对象没有可用的调用方法")
                else:
                    logger.warning("未找到可用的LLM函数或对象")
            else:
                logger.warning("rag实例不可用")

            # 如果无法获取LLM，返回空字符串触发回退逻辑
            logger.info("LLM不可用，将使用规则回退")
            return ""

        except Exception as e:
            logger.error(f"LLM调用失败: {e}", exc_info=True)
            return ""

    return llm_func

# 全局查询处理器实例（初始化时不带LLM，后续通过set_llm_func设置）
query_processor = QueryProcessor()

def set_llm_func_for_processor(llm_func):
    """为全局查询处理器设置LLM函数"""
    global query_processor
    query_processor.llm_func = llm_func
