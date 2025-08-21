import time
from fastapi import HTTPException, Request
from fastapi.responses import Response

from model import (
    BaseResponse, ConfigUpdateRequest, SystemResetRequest,
    HealthResponse, SystemStatus
)
from handler import guixiaoxirag_service
from common.config import settings
from common.logging_utils import logger_manager


class TransmitOpenAIPortAPI:
    """原生部署的模型端口转发API处理器"""
    
    def __init__(self):
        self.logger = logger_manager.setup_api_logger()
        self.start_time = time.time()
        
    async def forward_to_llm_service(self, path: str, request: Request, model_type: str = "chat"):
        """转发所有v1路径请求到LLM服务"""
        try:
            import httpx
            # 构建目标URL
            if model_type == "chat":
                target_url = f"{settings.openai_api_base}/{path}"
            elif model_type == "embedding":
                target_url = f"{settings.openai_embedding_api_base}/{path}"
            else:
                # Rank model
                target_url = f"{settings.openai_api_base}/{path}"
            # raise HTTPException(status_code=400, detail=f"不支持的模型类型: {model_type}")
            
            # 获取查询参数
            query_params = dict(request.query_params)
            
            # 获取请求头（排除不需要转发的头）
            headers = dict(request.headers)
            excluded_headers = {'host', 'content-length', 'connection', 'transfer-encoding'}
            forward_headers = {k: v for k, v in headers.items() 
                            if k.lower() not in excluded_headers}
            
            # 获取请求体
            body = await request.body() if request.method in ["POST", "PUT", "PATCH"] else None
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    params=query_params,
                    headers=forward_headers,
                    content=body
                )
                
                # 处理响应头
                response_headers = dict(response.headers)
                # 移除可能导致问题的响应头
                excluded_response_headers = {'content-encoding', 'transfer-encoding', 'connection'}
                clean_headers = {k: v for k, v in response_headers.items() 
                            if k.lower() not in excluded_response_headers}
                
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=clean_headers,
                    media_type=response.headers.get("content-type")
                )
                
        except httpx.ConnectError as e:
            self.logger.error(f"无法连接到LLM服务 {target_url}: {e}")
            raise HTTPException(
                status_code=502, 
                detail=f"LLM服务不可用，请检查 {settings.openai_api_base} 是否正常运行"
            )
        except httpx.TimeoutException as e:
            self.logger.error(f"LLM服务请求超时 {target_url}: {e}")
            raise HTTPException(
                status_code=504,
                detail="LLM服务响应超时"
            )
        except httpx.RequestError as e:
            self.logger.error(f"转发请求失败 {target_url}: {e}")
            raise HTTPException(
                status_code=502, 
                detail=f"转发请求失败: {str(e)}"
            )
        except Exception as e:
            self.logger.error(f"转发处理失败 {target_url}: {e}")
            raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")
        
        
__all__ = ["TransmitOpenAIPortAPI"]