"""
FastAPI中间件
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


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    def __init__(self, app, logger_name: str = "api"):
        super().__init__(app)
        self.logger = logging.getLogger(logger_name)
    
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


class MetricsMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("metrics")
        self.request_count = 0
        self.total_time = 0.0
        self.error_count = 0
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # 更新统计信息
            process_time = time.time() - start_time
            self.request_count += 1
            self.total_time += process_time
            
            # 记录性能指标
            if process_time > 5.0:  # 超过5秒的请求
                self.logger.warning(
                    f"慢请求警告 - 路径: {request.url.path}, "
                    f"方法: {request.method}, "
                    f"处理时间: {process_time:.3f}s"
                )
            
            return response
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(
                f"请求错误 - 路径: {request.url.path}, "
                f"方法: {request.method}, "
                f"错误: {str(e)}"
            )
            raise
    
    def get_metrics(self) -> dict:
        """获取性能指标"""
        avg_time = self.total_time / self.request_count if self.request_count > 0 else 0
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "average_response_time": avg_time,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0
        }


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    def __init__(self, app, max_request_size: int = 50 * 1024 * 1024):
        super().__init__(app)
        self.max_request_size = max_request_size
        self.logger = logging.getLogger("security")
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 检查请求大小
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            self.logger.warning(
                f"请求过大被拒绝 - 大小: {content_length}, "
                f"最大允许: {self.max_request_size}, "
                f"客户端IP: {request.client.host if request.client else 'unknown'}"
            )
            from fastapi import HTTPException
            raise HTTPException(status_code=413, detail="请求体过大")
        
        response = await call_next(request)
        
        # 添加安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response


# 全局中间件实例
metrics_middleware_instance = None


def get_metrics() -> dict:
    """获取全局性能指标"""
    if metrics_middleware_instance:
        return metrics_middleware_instance.get_metrics()
    return {
        "total_requests": 0,
        "total_errors": 0,
        "average_response_time": 0,
        "error_rate": 0
    }
