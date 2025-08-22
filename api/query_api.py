"""
查询API处理器
处理查询相关的业务逻辑
"""
import asyncio
import time
import json
from typing import Dict, Any, Optional, AsyncIterator
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from model import (
    BaseResponse, QueryRequest, BatchQueryRequest,
    QueryIntentAnalysisRequest, SafeQueryRequest,
    QueryResponse, QueryIntentAnalysisResponse, SafeQueryResponse
)
from handler import guixiaoxirag_service, QueryProcessor
from common.logging_utils import logger_manager
from common.constants import QUERY_MODE_DESCRIPTIONS, SUPPORTED_QUERY_MODES
from common.utils import get_query_mode_info


class QueryAPI:
    """查询API处理器"""
    
    def __init__(self):
        self.logger = logger_manager.setup_api_logger()
        self.query_processor = QueryProcessor(llm_func=None)  # 稍后设置LLM函数
    
    async def query(self, request: QueryRequest) -> BaseResponse:
        """智能知识查询"""
        try:
            self.logger.info(f"开始查询: {request.query[:50]}...")
            
            # 验证输入
            if not request.query.strip():
                raise HTTPException(status_code=400, detail="查询内容不能为空")
            
            if request.mode not in SUPPORTED_QUERY_MODES:
                raise HTTPException(status_code=400, detail=f"不支持的查询模式: {request.mode}")
            
            # 构建查询参数
            query_kwargs = {}
            if request.max_entity_tokens:
                query_kwargs["max_entity_tokens"] = request.max_entity_tokens
            if request.max_relation_tokens:
                query_kwargs["max_relation_tokens"] = request.max_relation_tokens
            if request.max_total_tokens:
                query_kwargs["max_total_tokens"] = request.max_total_tokens
            if request.hl_keywords:
                query_kwargs["hl_keywords"] = request.hl_keywords
            if request.ll_keywords:
                query_kwargs["ll_keywords"] = request.ll_keywords
            if request.conversation_history:
                query_kwargs["conversation_history"] = request.conversation_history
            if request.user_prompt:
                query_kwargs["user_prompt"] = request.user_prompt
            if request.enable_rerank is not None:
                query_kwargs["enable_rerank"] = request.enable_rerank
            
            # 执行查询并计时
            start_time = time.time()
            result = await guixiaoxirag_service.query(
                query=request.query,
                mode=request.mode,
                top_k=request.top_k,
                stream=request.stream,
                working_dir=self._get_working_dir(request.knowledge_base),
                language=request.language,
                performance_mode=request.performance_mode,
                **query_kwargs
            )
            elapsed = time.time() - start_time

            # 如果是流式响应，返回StreamingResponse
            if request.stream and hasattr(result, '__aiter__'):
                async def generate_stream():
                    """生成流式响应数据"""
                    try:
                        # 发送初始元数据
                        metadata = {
                            "type": "metadata",
                            "data": {
                                "mode": request.mode,
                                "query": request.query,
                                "knowledge_base": request.knowledge_base,
                                "language": request.language,
                                "stream": True
                            }
                        }
                        yield f"data: {json.dumps(metadata, ensure_ascii=False)}\n\n"

                        # 流式输出内容
                        async for chunk in result:
                            if chunk:  # 只发送非空内容
                                chunk_data = {
                                    "type": "content",
                                    "data": chunk
                                }
                                yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"

                        # 发送结束标记
                        end_data = {
                            "type": "done",
                            "data": {
                                "response_time": elapsed
                            }
                        }
                        yield f"data: {json.dumps(end_data, ensure_ascii=False)}\n\n"

                    except Exception as e:
                        error_data = {
                            "type": "error",
                            "data": {
                                "error": str(e)
                            }
                        }
                        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

                return StreamingResponse(
                    generate_stream(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "*"
                    }
                )

            # 构建响应，填充响应时间（如可得）
            response_time = None
            if isinstance(result, dict) and "response_time" in result:
                response_time = result.get("response_time")
            else:
                response_time = elapsed

            query_response = QueryResponse(
                result=result if isinstance(result, str) else str(result),
                mode=request.mode,
                query=request.query,
                knowledge_base=request.knowledge_base,
                language=request.language,
                response_time=response_time,
            )
            
            return BaseResponse(
                success=True,
                message="查询成功",
                data=query_response
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"查询失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    
    # async def safe_query(self, request: SafeQueryRequest) -> BaseResponse:
    #     """安全智能查询"""
    #     try:
    #         self.logger.info(f"开始安全查询: {request.query[:50]}...")
            
    #         # 验证输入
    #         if not request.query.strip():
    #             raise HTTPException(status_code=400, detail="查询内容不能为空")
            
    #         query_analysis = None
    #         query_result = None
            
    #         # 1. 查询意图分析（如果启用）
    #         if request.enable_intent_analysis:
    #             analysis_request = QueryIntentAnalysisRequest(
    #                 query=request.query,
    #                 enable_enhancement=request.enable_query_enhancement,
    #                 safety_check=request.safety_check
    #             )
    #             analysis_response = await self.analyze_query(analysis_request)
    #             query_analysis = analysis_response.data
                
    #             # 如果查询被拒绝，直接返回
    #             if query_analysis.should_reject:
    #                 return BaseResponse(
    #                     success=True,
    #                     message="查询已被安全检查拒绝",
    #                     data=SafeQueryResponse(
    #                         query_analysis=query_analysis,
    #                         query_result=None,
    #                         safety_passed=False,
    #                         processing_time=0.0
    #                     )
    #                 )
            
    #         # 2. 执行查询（如果通过安全检查）
    #         start_time = time.time()
            
    #         # 使用增强后的查询（如果有）
    #         final_query = request.query
    #         if query_analysis and query_analysis.enhanced_query:
    #             final_query = query_analysis.enhanced_query
            
    #         query_request = QueryRequest(
    #             query=final_query,
    #             mode=request.mode or "hybrid",
    #             knowledge_base=request.knowledge_base,
    #             language=request.language
    #         )
            
    #         query_response = await self.query(query_request)
    #         query_result = query_response.data
            
    #         processing_time = time.time() - start_time
            
    #         # 构建安全查询响应
    #         safe_response = SafeQueryResponse(
    #             query_analysis=query_analysis,
    #             query_result=query_result,
    #             safety_passed=True,
    #             processing_time=processing_time
    #         )
            
    #         return BaseResponse(
    #             success=True,
    #             message="安全查询完成",
    #             data=safe_response
    #         )
            
    #     except HTTPException:
    #         raise
    #     except Exception as e:
    #         self.logger.error(f"安全查询失败: {str(e)}")
    #         raise HTTPException(status_code=500, detail=f"安全查询失败: {str(e)}")
    
    async def get_query_modes(self) -> BaseResponse:
        """获取查询模式列表"""
        try:
            mode_info = get_query_mode_info()
            return BaseResponse(
                success=True,
                message="获取查询模式成功",
                data=mode_info
            )
        except Exception as e:
            self.logger.error(f"获取查询模式失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取查询模式失败: {str(e)}")
    
    async def batch_query(self, request: BatchQueryRequest) -> BaseResponse:
        """批量查询处理"""
        try:
            self.logger.info(f"开始批量查询，数量: {len(request.queries)}")
            
            # 验证输入
            if not request.queries:
                raise HTTPException(status_code=400, detail="查询列表不能为空")
            
            if len(request.queries) > 50:
                raise HTTPException(status_code=400, detail="批量查询数量不能超过50个")
            
            start_time = time.time()
            results = []
            
            if request.parallel:
                # 并行处理
                tasks = []
                for query_text in request.queries:
                    query_request = QueryRequest(
                        query=query_text,
                        mode=request.mode,
                        top_k=request.top_k,
                        knowledge_base=request.knowledge_base,
                        language=request.language
                    )
                    task = self.query(query_request)
                    tasks.append(task)
                
                # 等待所有任务完成，设置超时
                try:
                    responses = await asyncio.wait_for(
                        asyncio.gather(*tasks, return_exceptions=True),
                        timeout=request.timeout
                    )
                    
                    for i, response in enumerate(responses):
                        if isinstance(response, Exception):
                            results.append({
                                "query": request.queries[i],
                                "success": False,
                                "error": str(response)
                            })
                        else:
                            results.append({
                                "query": request.queries[i],
                                "success": True,
                                "result": response.data
                            })
                            
                except asyncio.TimeoutError:
                    raise HTTPException(status_code=408, detail="批量查询超时")
            else:
                # 串行处理
                for query_text in request.queries:
                    try:
                        query_request = QueryRequest(
                            query=query_text,
                            mode=request.mode,
                            top_k=request.top_k,
                            knowledge_base=request.knowledge_base,
                            language=request.language
                        )
                        response = await self.query(query_request)
                        results.append({
                            "query": query_text,
                            "success": True,
                            "result": response.data
                        })
                    except Exception as e:
                        results.append({
                            "query": query_text,
                            "success": False,
                            "error": str(e)
                        })
            
            total_time = time.time() - start_time
            successful_count = sum(1 for r in results if r.get("success", False))
            
            return BaseResponse(
                success=True,
                message=f"批量查询完成，成功: {successful_count}/{len(request.queries)}",
                data={
                    "results": results,
                    "total_queries": len(request.queries),
                    "successful_queries": successful_count,
                    "failed_queries": len(request.queries) - successful_count,
                    "mode": request.mode,
                    "total_time": total_time
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"批量查询失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"批量查询失败: {str(e)}")
    
    async def optimized_query(self, request: dict) -> BaseResponse:
        """使用优化参数的查询"""
        try:
            # 这里可以实现查询参数优化逻辑
            # 暂时使用基础查询
            query_request = QueryRequest(**request)
            return await self.query(query_request)
        except Exception as e:
            self.logger.error(f"优化查询失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"优化查询失败: {str(e)}")
    
    def _get_working_dir(self, knowledge_base: Optional[str]) -> Optional[str]:
        """获取工作目录"""
        if knowledge_base:
            from pathlib import Path
            from common.config import settings
            # 使用配置文件中的knowledgeBase目录
            kb_base_dir = str(Path(settings.working_dir).parent)
            return f"{kb_base_dir}/{knowledge_base}"
        return None
    
    def _get_llm_func(self):
        """获取LLM函数"""
        # 从GuiXiaoXiRag服务获取LLM函数
        try:
            return guixiaoxirag_service.get_llm_func()
        except Exception as e:
            self.logger.warning(f"获取LLM函数失败: {e}")
            return None


# 导出API处理器
__all__ = ["QueryAPI"]
