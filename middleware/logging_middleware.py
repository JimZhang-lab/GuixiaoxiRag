"""
日志中间件
"""
import time
import logging
import uuid
from typing import Callable
from fastapi import Request, Response
try:
    from fastapi.middleware.base import BaseHTTPMiddleware
except ImportError:
    from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint

from common.logging_utils import get_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    def __init__(self, app, logger_name: str = "api"):
        super().__init__(app)
        self.logger = get_logger(logger_name)
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 生成请求ID
        request_id = str(uuid.uuid4())
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取客户端信息
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # 记录请求信息
        self.logger.info(
            f"请求开始 - ID: {request_id}, "
            f"方法: {request.method}, "
            f"路径: {request.url.path}, "
            f"客户端IP: {client_ip}, "
            f"User-Agent: {user_agent}"
        )
        
        # 将请求ID添加到请求状态中
        request.state.request_id = request_id
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            self.logger.info(
                f"请求完成 - ID: {request_id}, "
                f"状态码: {response.status_code}, "
                f"处理时间: {process_time:.3f}s"
            )
            
            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录错误信息
            self.logger.error(
                f"请求失败 - ID: {request_id}, "
                f"错误: {str(e)}, "
                f"处理时间: {process_time:.3f}s",
                exc_info=True
            )
            
            # 重新抛出异常
            raise


class DetailedLoggingMiddleware(BaseHTTPMiddleware):
    """详细日志中间件"""
    
    def __init__(self, app, logger_name: str = "detailed_api", log_request_body: bool = False, log_response_body: bool = False):
        super().__init__(app)
        self.logger = get_logger(logger_name)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 获取请求详细信息
        client_info = {
            "ip": request.client.host if request.client else "unknown",
            "port": request.client.port if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "referer": request.headers.get("referer", "unknown"),
            "content_type": request.headers.get("content-type", "unknown"),
            "content_length": request.headers.get("content-length", "unknown")
        }
        
        # 记录请求详情
        request_info = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client": client_info
        }
        
        # 记录请求体（如果启用）
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    request_info["body_size"] = len(body)
                    # 只记录前1000个字符避免日志过大
                    request_info["body_preview"] = body.decode('utf-8')[:1000]
            except Exception as e:
                request_info["body_error"] = str(e)
        
        self.logger.info(f"详细请求信息: {request_info}")
        
        # 将请求ID添加到请求状态
        request.state.request_id = request_id
        request.state.start_time = start_time
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应详情
            response_info = {
                "request_id": request_id,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "process_time": process_time
            }
            
            # 记录响应体（如果启用且状态码表示成功）
            if self.log_response_body and 200 <= response.status_code < 300:
                try:
                    # 注意：这里需要小心处理，避免消费响应体
                    response_info["response_logged"] = "enabled"
                except Exception as e:
                    response_info["response_error"] = str(e)
            
            self.logger.info(f"详细响应信息: {response_info}")
            
            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            error_info = {
                "request_id": request_id,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "process_time": process_time
            }
            
            self.logger.error(f"详细错误信息: {error_info}", exc_info=True)
            raise


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """审计日志中间件"""
    
    def __init__(self, app, logger_name: str = "audit"):
        super().__init__(app)
        self.logger = get_logger(logger_name)
        # 需要审计的路径模式
        self.audit_paths = [
            "/system/reset",
            "/knowledge-graph/clear",
            "/config/update",
            "/knowledge-base/create",
            "/knowledge-base/delete"
        ]
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 检查是否需要审计
        if not any(pattern in request.url.path for pattern in self.audit_paths):
            return await call_next(request)
        
        request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
        start_time = time.time()
        
        # 审计信息
        audit_info = {
            "request_id": request_id,
            "timestamp": time.time(),
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "user_id": request.headers.get("x-user-id", "anonymous"),  # 假设用户ID在头部
            "session_id": request.headers.get("x-session-id", "unknown")
        }
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 记录审计日志
            audit_info.update({
                "status_code": response.status_code,
                "success": 200 <= response.status_code < 400,
                "process_time": time.time() - start_time
            })
            
            self.logger.info(f"审计日志: {audit_info}")
            
            return response
            
        except Exception as e:
            # 记录失败的审计日志
            audit_info.update({
                "success": False,
                "error": str(e),
                "process_time": time.time() - start_time
            })
            
            self.logger.error(f"审计日志（失败）: {audit_info}")
            raise


# 导出中间件
__all__ = [
    "LoggingMiddleware",
    "DetailedLoggingMiddleware", 
    "AuditLoggingMiddleware"
]
