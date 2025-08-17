"""
查询处理器 - 基于大模型的意图识别、意图补充、意图修复和内容过滤
优化版本 - 整合参考项目最佳实践
"""
import re
import json
import time
from typing import Dict, List, Optional, Any, Callable

from common.logging_utils import logger_manager
from .models import (
    QueryIntentType, ContentSafetyLevel, QueryAnalysisResult,
    SafetyCheckResult, IntentAnalysisResult, QueryEnhancementResult,
    ProcessorConfig
)
from .dfa_filter import SensitiveWordManager
from .utils import QueryUtils, IntentPatterns, EnhancementTemplates

logger = logger_manager.get_logger("intent_processor")


def extracted_think_and_answer(response_content: str) -> tuple[str, str]:
    """提取大模型响应中的思考过程和最终答案"""
    try:
        think_str = response_content.split("<think>")[1]
        think_str = think_str.split("</think>")[0].strip()
        answer_str = response_content.split("</think>")[1].strip()
        return think_str, answer_str
    except (IndexError, AttributeError):
        return "", response_content


class IntentRecognitionProcessor:
    """基于大模型的意图识别处理器"""

    def __init__(self, config: ProcessorConfig = None, llm_func: Optional[Callable] = None):
        self.config = config or ProcessorConfig()
        self.llm_func = llm_func
        
        # 初始化敏感词管理器
        self.sensitive_word_manager = None
        if self.config.enable_dfa_filter:
            self.sensitive_word_manager = SensitiveWordManager()
            self.sensitive_word_manager.initialize(self.config.sensitive_vocabulary_path)
        
        # 加载模式和模板
        self.intent_patterns = IntentPatterns.get_default_patterns()
        self.educational_patterns = IntentPatterns.get_educational_patterns()
        self.instructive_patterns = IntentPatterns.get_instructive_patterns()
        self.enhancement_templates = EnhancementTemplates.get_default_templates()
        
        # 大模型提示词模板
        self._init_prompts()

    def _init_prompts(self):
        """初始化提示词模板"""
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

    async def process_query(self, query: str, context: Optional[Dict] = None) -> QueryAnalysisResult:
        """基于大模型的查询处理"""
        start_time = time.time()
        
        try:
            logger.info(f"开始处理查询: {query[:50]}...")

            # 1. 查询清理和标准化
            processed_query = await self._clean_and_normalize_query(query)
            logger.debug(f"查询清理完成: {processed_query[:50]}...")

            # 2. 安全检查
            logger.debug("开始安全检查")
            safety_result = await self._safety_check(processed_query)
            logger.info(f"安全检查完成: {safety_result.safety_level}, 安全: {safety_result.is_safe}")

            # 如果查询不安全，返回拒绝结果
            if not safety_result.is_safe:
                logger.info("查询被标记为不安全，返回拒绝结果")
                
                safety_tips = QueryUtils.generate_default_safety_tips(safety_result.safety_level)
                safe_alternatives = QueryUtils.generate_default_alternatives(processed_query)

                return QueryAnalysisResult(
                    original_query=query,
                    processed_query=processed_query,
                    intent_type=QueryIntentType.ILLEGAL_CONTENT,
                    safety_level=ContentSafetyLevel(safety_result.safety_level),
                    confidence=safety_result.confidence,
                    suggestions=[],
                    risk_factors=safety_result.risk_factors,
                    enhanced_query=None,
                    should_reject=True,
                    rejection_reason=safety_result.reason,
                    safety_tips=safety_tips,
                    safe_alternatives=safe_alternatives,
                    processing_time=time.time() - start_time
                )

            # 3. 意图识别
            logger.debug("开始意图识别")
            intent_result = await self._intent_analysis(processed_query)
            logger.info(f"意图识别完成: {intent_result.intent_type}")

            # 4. 查询增强
            enhanced_query = None
            if self.config.enable_query_enhancement and safety_result.is_safe:
                logger.debug("开始查询增强")
                enhancement_result = await self._query_enhancement(
                    processed_query, intent_result.intent_type, safety_result.safety_level
                )
                if enhancement_result.should_enhance:
                    enhanced_query = enhancement_result.enhanced_query
                    logger.info(f"查询增强完成: {enhanced_query[:50] if enhanced_query else 'None'}...")

            # 5. 生成建议
            suggestions = intent_result.keywords + (enhancement_result.suggestions if 'enhancement_result' in locals() else [])

            processing_time = time.time() - start_time
            logger.info(f"查询处理完成，总耗时: {processing_time:.2f}s")

            return QueryAnalysisResult(
                original_query=query,
                processed_query=processed_query,
                intent_type=QueryIntentType(intent_result.intent_type),
                safety_level=ContentSafetyLevel(safety_result.safety_level),
                confidence=min(safety_result.confidence, intent_result.confidence),
                suggestions=suggestions,
                risk_factors=safety_result.risk_factors,
                enhanced_query=enhanced_query,
                should_reject=False,
                rejection_reason=None,
                safety_tips=[],
                safe_alternatives=[],
                processing_time=processing_time
            )

        except Exception as e:
            logger.error(f"查询处理失败: {e}", exc_info=True)
            return QueryAnalysisResult(
                original_query=query,
                processed_query=query,
                intent_type=QueryIntentType.UNCLEAR,
                safety_level=ContentSafetyLevel.SUSPICIOUS,
                confidence=0.0,
                suggestions=["查询处理出现错误，请重试"],
                risk_factors=["处理异常"],
                enhanced_query=None,
                should_reject=True,
                rejection_reason="查询处理异常",
                safety_tips=[],
                safe_alternatives=[],
                processing_time=time.time() - start_time
            )

    async def _clean_and_normalize_query(self, query: str) -> str:
        """清理和标准化查询"""
        return await QueryUtils.clean_and_normalize_query(query)

    async def _safety_check(self, query: str) -> SafetyCheckResult:
        """安全检查 - 优先使用大模型，失败时回退到DFA"""
        try:
            # 第一优先级：使用大模型检查
            if self.config.enable_llm and self.llm_func:
                try:
                    logger.debug("尝试使用大模型进行安全检查")
                    result = await self._llm_safety_check(query)
                    logger.debug("大模型安全检查成功")
                    return result
                except Exception as e:
                    logger.warning(f"大模型安全检查失败，回退到DFA: {e}")
                    # 继续执行DFA检查

            # 第二优先级：回退到DFA过滤器检查
            if self.sensitive_word_manager:
                logger.debug("使用DFA过滤器进行安全检查")
                result = self.sensitive_word_manager.check_content_safety(query)
                return SafetyCheckResult(
                    is_safe=result["is_safe"],
                    safety_level=result["safety_level"],
                    risk_factors=result["risk_factors"],
                    confidence=result["confidence"],
                    reason=result["reason"] + " (DFA回退)",
                    sensitive_words=result.get("sensitive_words", []),
                    filtered_text=result.get("filtered_text")
                )

            # 第三优先级：基础规则检查
            logger.debug("使用基础规则进行安全检查")
            return await self._basic_safety_check(query)

        except Exception as e:
            logger.error(f"所有安全检查方法都失败: {e}")
            return SafetyCheckResult(
                is_safe=False,
                safety_level="suspicious",
                risk_factors=["安全检查异常"],
                confidence=0.5,
                reason=f"安全检查异常: {e}"
            )

    async def _llm_safety_check(self, query: str) -> SafetyCheckResult:
        """使用大模型进行安全检查"""
        if not self.llm_func:
            raise Exception("LLM函数未提供")

        try:
            prompt = self.safety_check_prompt.format(query=query)
            logger.debug(f"发送安全检查请求到大模型，查询长度: {len(query)}")

            response = await self.llm_func(prompt)

            if not response or not response.strip():
                raise Exception("大模型返回空响应")

            # 处理包含 <think> 标签的响应
            if "<think>" in response and "</think>" in response:
                _, response = extracted_think_and_answer(response)

            # 清理响应格式
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
            response_clean = response_clean.strip()

            if not response_clean:
                raise Exception("清理后的响应为空")

            try:
                result = json.loads(response_clean)
            except json.JSONDecodeError as e:
                raise Exception(f"JSON解析失败: {e}, 响应内容: {response_clean[:200]}")

            # 验证必要字段
            required_fields = ["is_safe", "safety_level", "confidence", "reason"]
            for field in required_fields:
                if field not in result:
                    raise Exception(f"大模型响应缺少必要字段: {field}")

            logger.debug(f"大模型安全检查成功: {result.get('safety_level')}")

            return SafetyCheckResult(
                is_safe=result.get("is_safe", True),
                safety_level=result.get("safety_level", "safe"),
                risk_factors=result.get("risk_factors", []),
                confidence=result.get("confidence", 0.8),
                reason=result.get("reason", "大模型安全检查"),
                intent_direction=result.get("intent_direction")
            )

        except Exception as e:
            logger.error(f"大模型安全检查失败: {e}")
            # 重新抛出异常，让上层处理回退逻辑
            raise e

    async def _basic_safety_check(self, query: str) -> SafetyCheckResult:
        """基础安全检查（规则基础）"""
        # 使用工具类进行基础检查
        illegal_keywords = [
            "赌博", "毒品", "色情", "暴力", "诈骗", "非法", "违法",
            "gambling", "drugs", "pornography", "violence", "fraud"
        ]

        risk_score = QueryUtils.calculate_risk_score(
            query, illegal_keywords, self.educational_patterns, self.instructive_patterns
        )

        safety_level = QueryUtils.determine_safety_level(risk_score)
        is_safe = safety_level == "safe"

        hits = QueryUtils.find_illegal_hits(query, illegal_keywords)

        return SafetyCheckResult(
            is_safe=is_safe,
            safety_level=safety_level,
            risk_factors=hits,
            confidence=0.7,
            reason="基础规则检查"
        )

    async def _intent_analysis(self, query: str) -> IntentAnalysisResult:
        """意图分析 - 优先使用大模型，失败时回退到规则分析"""
        try:
            # 第一优先级：使用大模型分析
            if self.config.enable_llm and self.llm_func:
                try:
                    logger.debug("尝试使用大模型进行意图分析")
                    result = await self._llm_intent_analysis(query)
                    logger.debug("大模型意图分析成功")
                    return result
                except Exception as e:
                    logger.warning(f"大模型意图分析失败，回退到规则分析: {e}")
                    # 继续执行规则分析

            # 第二优先级：回退到规则分析
            logger.debug("使用规则进行意图分析")
            result = await self._basic_intent_analysis(query)
            # 标记为回退结果
            result.reason = result.reason + " (规则回退)"
            return result

        except Exception as e:
            logger.error(f"所有意图分析方法都失败: {e}")
            return IntentAnalysisResult(
                intent_type="unclear",
                confidence=0.0,
                reason=f"意图分析异常: {e}",
                keywords=[]
            )

    async def _llm_intent_analysis(self, query: str) -> IntentAnalysisResult:
        """使用大模型进行意图分析"""
        if not self.llm_func:
            raise Exception("LLM函数未提供")

        try:
            prompt = self.intent_analysis_prompt.format(query=query)
            logger.debug(f"发送意图分析请求到大模型，查询长度: {len(query)}")

            response = await self.llm_func(prompt)

            if not response or not response.strip():
                raise Exception("大模型返回空响应")

            # 处理包含 <think> 标签的响应
            if "<think>" in response and "</think>" in response:
                _, response = extracted_think_and_answer(response)

            # 清理响应格式
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
            response_clean = response_clean.strip()

            if not response_clean:
                raise Exception("清理后的响应为空")

            try:
                result = json.loads(response_clean)
            except json.JSONDecodeError as e:
                raise Exception(f"JSON解析失败: {e}, 响应内容: {response_clean[:200]}")

            # 验证必要字段
            required_fields = ["intent_type", "confidence", "reason"]
            for field in required_fields:
                if field not in result:
                    raise Exception(f"大模型响应缺少必要字段: {field}")

            # 验证intent_type是否有效
            intent_type_str = result.get("intent_type", "unclear")
            try:
                QueryIntentType(intent_type_str)
            except ValueError:
                logger.warning(f"无效的意图类型: {intent_type_str}，使用unclear")
                intent_type_str = "unclear"

            logger.debug(f"大模型意图分析成功: {intent_type_str}")

            return IntentAnalysisResult(
                intent_type=intent_type_str,
                confidence=result.get("confidence", 0.8),
                reason=result.get("reason", "大模型意图分析"),
                keywords=result.get("keywords", [])
            )

        except Exception as e:
            logger.error(f"大模型意图分析失败: {e}")
            # 重新抛出异常，让上层处理回退逻辑
            raise e

    async def _basic_intent_analysis(self, query: str) -> IntentAnalysisResult:
        """基础意图分析（规则基础）"""
        query_lower = query.lower()

        # 特殊：若包含教育/防范导向词，优先视为知识查询或程序性问题
        if QueryUtils.has_educational_intent(query, self.educational_patterns):
            if any(w in query_lower for w in ["如何", "怎样", "怎么", "how"]):
                return IntentAnalysisResult(
                    intent_type="procedural_question",
                    confidence=0.8,
                    reason="检测到教育导向的程序性问题",
                    keywords=["教育", "防范"]
                )
            return IntentAnalysisResult(
                intent_type="knowledge_query",
                confidence=0.8,
                reason="检测到教育导向的知识查询",
                keywords=["教育", "知识"]
            )

        # 检查每种意图类型的模式
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return IntentAnalysisResult(
                        intent_type=intent_type,
                        confidence=0.7,
                        reason=f"匹配模式: {pattern}",
                        keywords=[pattern]
                    )

        return IntentAnalysisResult(
            intent_type="unclear",
            confidence=0.5,
            reason="未匹配到明确意图模式",
            keywords=[]
        )

    async def _query_enhancement(self, query: str, intent_type: str, safety_level: str) -> QueryEnhancementResult:
        """查询增强 - 优先使用大模型，失败时回退到模板增强"""
        try:
            # 第一优先级：使用大模型增强
            if self.config.enable_llm and self.llm_func:
                try:
                    logger.debug("尝试使用大模型进行查询增强")
                    result = await self._llm_query_enhancement(query, intent_type, safety_level)
                    logger.debug("大模型查询增强成功")
                    return result
                except Exception as e:
                    logger.warning(f"大模型查询增强失败，回退到模板增强: {e}")
                    # 继续执行模板增强

            # 第二优先级：回退到模板增强
            logger.debug("使用模板进行查询增强")
            result = await self._template_enhancement(query, intent_type)
            # 标记为回退结果
            if result.should_enhance:
                result.enhancement_reason = result.enhancement_reason + " (模板回退)"
            return result

        except Exception as e:
            logger.error(f"所有查询增强方法都失败: {e}")
            return QueryEnhancementResult(
                should_enhance=False,
                enhanced_query=None,
                enhancement_reason=f"增强异常: {e}",
                suggestions=[]
            )

    async def _llm_query_enhancement(self, query: str, intent_type: str, safety_level: str) -> QueryEnhancementResult:
        """使用大模型进行查询增强"""
        if not self.llm_func:
            raise Exception("LLM函数未提供")

        try:
            prompt = self.query_enhancement_prompt.format(
                query=query, intent_type=intent_type, safety_level=safety_level
            )
            logger.debug(f"发送查询增强请求到大模型，查询长度: {len(query)}")

            response = await self.llm_func(prompt)

            if not response or not response.strip():
                raise Exception("大模型返回空响应")

            # 处理包含 <think> 标签的响应
            if "<think>" in response and "</think>" in response:
                _, response = extracted_think_and_answer(response)

            # 清理响应格式
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
            response_clean = response_clean.strip()

            if not response_clean:
                raise Exception("清理后的响应为空")

            try:
                result = json.loads(response_clean)
            except json.JSONDecodeError as e:
                raise Exception(f"JSON解析失败: {e}, 响应内容: {response_clean[:200]}")

            # 验证必要字段
            required_fields = ["should_enhance", "enhancement_reason"]
            for field in required_fields:
                if field not in result:
                    raise Exception(f"大模型响应缺少必要字段: {field}")

            should_enhance = result.get("should_enhance", False)
            enhanced_query = result.get("enhanced_query") if should_enhance else None

            logger.debug(f"大模型查询增强成功: 是否增强={should_enhance}")

            return QueryEnhancementResult(
                should_enhance=should_enhance,
                enhanced_query=enhanced_query,
                enhancement_reason=result.get("enhancement_reason", "大模型增强"),
                suggestions=result.get("suggestions", [])
            )

        except Exception as e:
            logger.error(f"大模型查询增强失败: {e}")
            # 重新抛出异常，让上层处理回退逻辑
            raise e

    async def _template_enhancement(self, query: str, intent_type: str) -> QueryEnhancementResult:
        """使用模板增强查询"""
        templates = self.enhancement_templates.get(intent_type, [])
        if templates:
            enhanced_query = templates[0].format(query=query)
            return QueryEnhancementResult(
                should_enhance=True,
                enhanced_query=enhanced_query,
                enhancement_reason="模板增强",
                suggestions=["使用了预定义模板进行查询增强"]
            )

        return QueryEnhancementResult(
            should_enhance=False,
            enhanced_query=None,
            enhancement_reason="无可用模板",
            suggestions=[]
        )


# 导出
__all__ = ["IntentRecognitionProcessor", "extracted_think_and_answer"]
