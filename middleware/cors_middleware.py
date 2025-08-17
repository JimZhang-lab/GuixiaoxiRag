"""
CORS中间件
"""
from typing import List, Set, Optional, Union
from fastapi import Request, Response
try:
    from fastapi.middleware.base import BaseHTTPMiddleware
except ImportError:
    from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint

from common.logging_utils import get_logger


class CORSMiddleware(BaseHTTPMiddleware):
    """自定义CORS中间件"""
    
    def __init__(
        self,
        app,
        allow_origins: Union[List[str], Set[str]] = None,
        allow_methods: Union[List[str], Set[str]] = None,
        allow_headers: Union[List[str], Set[str]] = None,
        allow_credentials: bool = False,
        expose_headers: Union[List[str], Set[str]] = None,
        max_age: int = 600,
        allow_origin_regex: Optional[str] = None
    ):
        super().__init__(app)
        self.logger = get_logger("cors")
        
        # 处理允许的源
        if allow_origins is None:
            self.allow_origins = {"*"}
        else:
            self.allow_origins = set(allow_origins) if isinstance(allow_origins, list) else allow_origins
        
        # 处理允许的方法
        if allow_methods is None:
            self.allow_methods = {"GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"}
        else:
            self.allow_methods = set(allow_methods) if isinstance(allow_methods, list) else allow_methods
        
        # 处理允许的头部
        if allow_headers is None:
            self.allow_headers = {
                "Accept", "Accept-Language", "Content-Language", "Content-Type",
                "Authorization", "X-Requested-With", "X-API-Key", "X-User-ID",
                "X-Session-ID", "X-Request-ID"
            }
        else:
            self.allow_headers = set(allow_headers) if isinstance(allow_headers, list) else allow_headers
        
        # 处理暴露的头部
        if expose_headers is None:
            self.expose_headers = {
                "X-Request-ID", "X-Process-Time", "X-Response-Time", "X-Request-Count"
            }
        else:
            self.expose_headers = set(expose_headers) if isinstance(expose_headers, list) else expose_headers
        
        self.allow_credentials = allow_credentials
        self.max_age = max_age
        self.allow_origin_regex = allow_origin_regex
        
        # 编译正则表达式（如果提供）
        self.origin_pattern = None
        if allow_origin_regex:
            import re
            self.origin_pattern = re.compile(allow_origin_regex)
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        origin = request.headers.get("origin")
        
        # 处理预检请求
        if request.method == "OPTIONS":
            return self._handle_preflight(request, origin)
        
        # 处理实际请求
        response = await call_next(request)
        
        # 添加CORS头部
        self._add_cors_headers(response, origin)
        
        return response
    
    def _handle_preflight(self, request: Request, origin: Optional[str]) -> Response:
        """处理预检请求"""
        response = Response()
        
        # 检查Origin
        if not self._is_origin_allowed(origin):
            self.logger.warning(f"CORS预检失败 - 不允许的Origin: {origin}")
            response.status_code = 403
            return response
        
        # 检查请求方法
        requested_method = request.headers.get("access-control-request-method")
        if requested_method and requested_method not in self.allow_methods:
            self.logger.warning(f"CORS预检失败 - 不允许的方法: {requested_method}")
            response.status_code = 403
            return response
        
        # 检查请求头部
        requested_headers = request.headers.get("access-control-request-headers")
        if requested_headers:
            requested_headers_set = {h.strip() for h in requested_headers.split(",")}
            if not requested_headers_set.issubset(self.allow_headers):
                self.logger.warning(f"CORS预检失败 - 不允许的头部: {requested_headers}")
                response.status_code = 403
                return response
        
        # 添加CORS头部
        self._add_cors_headers(response, origin)
        
        # 添加预检特定头部
        if requested_method:
            response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
        
        if requested_headers:
            response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
        
        response.headers["Access-Control-Max-Age"] = str(self.max_age)
        
        self.logger.debug(f"CORS预检成功 - Origin: {origin}")
        return response
    
    def _add_cors_headers(self, response: Response, origin: Optional[str]):
        """添加CORS头部到响应"""
        if self._is_origin_allowed(origin):
            if "*" in self.allow_origins and not self.allow_credentials:
                response.headers["Access-Control-Allow-Origin"] = "*"
            elif origin:
                response.headers["Access-Control-Allow-Origin"] = origin
        
        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        if self.expose_headers:
            response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)
        
        # 添加Vary头部以支持缓存
        vary_headers = []
        if "Access-Control-Allow-Origin" in response.headers and response.headers["Access-Control-Allow-Origin"] != "*":
            vary_headers.append("Origin")
        
        if vary_headers:
            existing_vary = response.headers.get("Vary", "")
            if existing_vary:
                vary_headers.insert(0, existing_vary)
            response.headers["Vary"] = ", ".join(vary_headers)
    
    def _is_origin_allowed(self, origin: Optional[str]) -> bool:
        """检查Origin是否被允许"""
        if not origin:
            return True  # 同源请求
        
        if "*" in self.allow_origins:
            return True
        
        if origin in self.allow_origins:
            return True
        
        # 检查正则表达式匹配
        if self.origin_pattern and self.origin_pattern.match(origin):
            return True
        
        return False
    
    def add_allowed_origin(self, origin: str):
        """动态添加允许的源"""
        self.allow_origins.add(origin)
        self.logger.info(f"添加允许的Origin: {origin}")
    
    def remove_allowed_origin(self, origin: str):
        """动态移除允许的源"""
        if origin in self.allow_origins:
            self.allow_origins.remove(origin)
            self.logger.info(f"移除允许的Origin: {origin}")
    
    def get_cors_config(self) -> dict:
        """获取CORS配置"""
        return {
            "allow_origins": list(self.allow_origins),
            "allow_methods": list(self.allow_methods),
            "allow_headers": list(self.allow_headers),
            "expose_headers": list(self.expose_headers),
            "allow_credentials": self.allow_credentials,
            "max_age": self.max_age,
            "allow_origin_regex": self.allow_origin_regex
        }


class DynamicCORSMiddleware(BaseHTTPMiddleware):
    """动态CORS中间件 - 支持运行时配置更新"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = get_logger("dynamic_cors")
        
        # 默认配置
        self.config = {
            "allow_origins": {"*"},
            "allow_methods": {"GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"},
            "allow_headers": {
                "Accept", "Accept-Language", "Content-Language", "Content-Type",
                "Authorization", "X-Requested-With", "X-API-Key"
            },
            "expose_headers": {"X-Request-ID", "X-Process-Time"},
            "allow_credentials": False,
            "max_age": 600
        }
        
        # 环境特定配置
        self.environment_configs = {
            "development": {
                "allow_origins": {"*"},
                "allow_credentials": True
            },
            "production": {
                "allow_origins": {"https://yourdomain.com", "https://api.yourdomain.com"},
                "allow_credentials": True
            },
            "testing": {
                "allow_origins": {"http://localhost:3000", "http://localhost:8080"},
                "allow_credentials": False
            }
        }
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        origin = request.headers.get("origin")
        
        # 处理预检请求
        if request.method == "OPTIONS":
            return self._handle_preflight(request, origin)
        
        # 处理实际请求
        response = await call_next(request)
        
        # 添加CORS头部
        self._add_cors_headers(response, origin)
        
        return response
    
    def _handle_preflight(self, request: Request, origin: Optional[str]) -> Response:
        """处理预检请求"""
        response = Response()
        
        if not self._is_origin_allowed(origin):
            response.status_code = 403
            return response
        
        # 添加预检头部
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.config["allow_methods"])
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.config["allow_headers"])
        response.headers["Access-Control-Max-Age"] = str(self.config["max_age"])
        
        self._add_cors_headers(response, origin)
        
        return response
    
    def _add_cors_headers(self, response: Response, origin: Optional[str]):
        """添加CORS头部"""
        if self._is_origin_allowed(origin):
            if "*" in self.config["allow_origins"] and not self.config["allow_credentials"]:
                response.headers["Access-Control-Allow-Origin"] = "*"
            elif origin:
                response.headers["Access-Control-Allow-Origin"] = origin
        
        if self.config["allow_credentials"]:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        if self.config["expose_headers"]:
            response.headers["Access-Control-Expose-Headers"] = ", ".join(self.config["expose_headers"])
    
    def _is_origin_allowed(self, origin: Optional[str]) -> bool:
        """检查Origin是否被允许"""
        if not origin:
            return True
        
        return "*" in self.config["allow_origins"] or origin in self.config["allow_origins"]
    
    def update_config(self, new_config: dict):
        """更新CORS配置"""
        for key, value in new_config.items():
            if key in self.config:
                if isinstance(value, list):
                    self.config[key] = set(value)
                else:
                    self.config[key] = value
        
        self.logger.info(f"CORS配置已更新: {new_config}")
    
    def set_environment(self, environment: str):
        """设置环境特定配置"""
        if environment in self.environment_configs:
            env_config = self.environment_configs[environment]
            self.update_config(env_config)
            self.logger.info(f"应用环境配置: {environment}")
        else:
            self.logger.warning(f"未知环境: {environment}")
    
    def get_config(self) -> dict:
        """获取当前配置"""
        return {
            key: list(value) if isinstance(value, set) else value
            for key, value in self.config.items()
        }


# 导出中间件
__all__ = [
    "CORSMiddleware",
    "DynamicCORSMiddleware"
]
