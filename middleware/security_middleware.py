"""
安全中间件
"""
import time
import hashlib
from typing import Set, Dict, Any, Optional
from collections import defaultdict, deque
from fastapi import Request, Response, HTTPException
try:
    from fastapi.middleware.base import BaseHTTPMiddleware
except ImportError:
    from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint

from common.logging_utils import get_logger


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件（支持代理转发、分层限流、按用户限流）"""

    def __init__(
        self,
        app,
        max_request_size: int = 50 * 1024 * 1024,  # 50MB
        rate_limit_requests: int = 100,  # 每分钟请求数（默认层）
        rate_limit_window: int = 60,  # 时间窗口（秒）
        blocked_ips: Optional[Set[str]] = None,
        allowed_origins: Optional[Set[str]] = None,
        # 代理与用户标识
        enable_proxy_headers: bool = True,
        trusted_proxy_ips: Optional[list] = None,
        user_id_header: str = "x-user-id",
        client_id_header: str = "x-client-id",
        api_key_header: str = "x-api-key",
        authorization_header: str = "authorization",
        user_tier_header: str = "x-user-tier",
        # 分层限流
        rate_limit_tiers: Optional[Dict[str, int]] = None,
        rate_limit_default_tier: str = "default",
        min_interval_per_user: float = 0.0,
    ):
        super().__init__(app)
        self.logger = get_logger("security")
        self.max_request_size = max_request_size
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        self.blocked_ips = blocked_ips or set()
        self.allowed_origins = allowed_origins
        # 代理/头部配置
        self.enable_proxy_headers = enable_proxy_headers
        self.trusted_proxy_ips = trusted_proxy_ips or []
        self.user_id_header = user_id_header.lower()
        self.client_id_header = client_id_header.lower()
        self.api_key_header = api_key_header.lower()
        self.authorization_header = authorization_header.lower()
        self.user_tier_header = user_tier_header.lower()
        # 分层限流配置
        self.rate_limit_tiers = rate_limit_tiers or {"default": rate_limit_requests}
        self.rate_limit_default_tier = rate_limit_default_tier
        self.min_interval_per_user = min_interval_per_user

        # 速率限制跟踪（key -> 时间戳队列）
        self.request_counts = defaultdict(deque)
        # 用户最近一次请求时间
        self.last_request_time: Dict[str, float] = {}

        # 可疑活动跟踪
        self.suspicious_ips = defaultdict(int)
        self.failed_requests = defaultdict(deque)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = self._get_client_ip(request)
        rate_key = self._get_rate_limit_key(request) or client_ip

        # 1. IP黑名单检查（仍按IP黑名单）
        if client_ip in self.blocked_ips:
            self.logger.warning(f"阻止黑名单IP访问: {client_ip}")
            raise HTTPException(status_code=403, detail="访问被拒绝")

        # 2. 速率限制检查（支持按用户等级分层、以及同用户最小间隔）
        tier = self._get_user_tier(request)
        limit_per_min = self._get_rate_limit_for_tier(tier)
        if not self._check_rate_limit(rate_key, limit_per_min):
            self.logger.warning(f"实体 {rate_key} 触发速率限制 (tier={tier}, IP={client_ip})")
            raise HTTPException(status_code=429, detail="请求过于频繁")
        # 最小间隔检查
        if self.min_interval_per_user > 0:
            last_ts = self.last_request_time.get(rate_key, 0.0)
            now = time.time()
            if now - last_ts < self.min_interval_per_user:
                self.logger.warning(f"实体 {rate_key} 触发最小间隔限制: {now - last_ts:.3f}s < {self.min_interval_per_user}s")
                raise HTTPException(status_code=429, detail="请求间隔过短")
            self.last_request_time[rate_key] = now

        # 3. 请求大小检查
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            self.logger.warning(f"请求大小超限: {content_length} bytes from {client_ip}")
            raise HTTPException(status_code=413, detail="请求体过大")

        # 4. Origin检查（如果配置了）
        if self.allowed_origins:
            origin = request.headers.get("origin")
            if origin and origin not in self.allowed_origins:
                self.logger.warning(f"不允许的Origin: {origin} from {client_ip}")
                raise HTTPException(status_code=403, detail="不允许的来源")

        # 5. 检查可疑活动
        self._check_suspicious_activity(request, client_ip)

        try:
            response = await call_next(request)

            # 记录成功请求
            self._record_request(rate_key, True)

            # 添加安全头部（传递请求路径）
            self._add_security_headers(response, request.url.path)

            return response

        except HTTPException as e:
            # 记录失败请求
            self._record_request(rate_key, False)
            self._record_failed_request(rate_key, e.status_code)
            raise
        except Exception as e:
            # 记录异常
            self._record_request(rate_key, False)
            self._record_failed_request(rate_key, 500)
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址（支持受信任代理）"""
        # 如果启用代理头且来源在受信任代理列表，则使用代理头
        if self.enable_proxy_headers:
            # 获取直连对端（可能是代理）
            peer_ip = request.client.host if request.client else "unknown"
            if self._is_trusted_proxy(peer_ip):
                forwarded_for = request.headers.get("x-forwarded-for")
                if forwarded_for:
                    return forwarded_for.split(",")[0].strip()
                real_ip = request.headers.get("x-real-ip")
                if real_ip:
                    return real_ip
        # 回退：使用直连IP
        return request.client.host if request.client else "unknown"

    def _is_trusted_proxy(self, ip: str) -> bool:
        try:
            import ipaddress
            for cidr in self.trusted_proxy_ips:
                try:
                    if "/" in cidr:
                        if ipaddress.ip_address(ip) in ipaddress.ip_network(cidr, strict=False):
                            return True
                    else:
                        if ip == cidr:
                            return True
                except ValueError:
                    continue
        except Exception:
            pass
        return False

    def _check_rate_limit(self, key: str, limit_per_minute: int) -> bool:
        """检查速率限制：按给定限额计算（支持分层）"""
        current_time = time.time()
        requests = self.request_counts[key]
        window = self.rate_limit_window
        # 清理过期的请求记录
        while requests and requests[0] < current_time - window:
            requests.popleft()
        # 检查是否超过限制
        if len(requests) >= limit_per_minute:
            return False
        # 记录当前请求
        requests.append(current_time)
        return True

    def _get_rate_limit_key(self, request: Request) -> Optional[str]:
        """获取用于速率限制的键：优先用户，其次客户端/密钥；支持自定义头名"""
        # 用户/客户端标识头部（使用可配置的头名）
        headers = {k.lower(): v for k, v in request.headers.items()}
        user_id = headers.get(self.user_id_header)
        client_id = headers.get(self.client_id_header)
        api_key = headers.get(self.api_key_header)
        auth = headers.get(self.authorization_header)
        # 查询参数备选
        if not user_id:
            user_id = request.query_params.get("user_id")
        if not api_key:
            api_key = request.query_params.get("api_key")
        # 优先顺序：user_id > client_id > api_key > authorization
        for v in (user_id, client_id, api_key, auth):
            if v:
                digest = hashlib.sha256(v.encode("utf-8")).hexdigest()[:16]
                return f"user:{digest}"
        return None

    def _get_user_tier(self, request: Request) -> str:
        headers = {k.lower(): v for k, v in request.headers.items()}
        tier = headers.get(self.user_tier_header)
        return tier or self.rate_limit_default_tier

    def _get_rate_limit_for_tier(self, tier: str) -> int:
        return self.rate_limit_tiers.get(tier, self.rate_limit_tiers.get(self.rate_limit_default_tier, self.rate_limit_requests))

    
    def _check_suspicious_activity(self, request: Request, client_ip: str):
        """检查可疑活动"""
        suspicious_patterns = [
            # SQL注入模式
            "union select", "drop table", "insert into", "delete from",
            # XSS模式
            "<script", "javascript:", "onerror=", "onload=",
            # 路径遍历
            "../", "..\\", "/etc/passwd", "/windows/system32",
            # 命令注入
            "; cat ", "| cat ", "&& cat ", "|| cat "
        ]
        
        # 检查URL和查询参数
        full_url = str(request.url).lower()
        for pattern in suspicious_patterns:
            if pattern in full_url:
                self.suspicious_ips[client_ip] += 1
                self.logger.warning(
                    f"检测到可疑活动 - IP: {client_ip}, "
                    f"模式: {pattern}, URL: {request.url}"
                )
                
                # 如果可疑活动过多，临时阻止
                if self.suspicious_ips[client_ip] > 5:
                    self.blocked_ips.add(client_ip)
                    self.logger.error(f"IP {client_ip} 因可疑活动被临时阻止")
                    raise HTTPException(status_code=403, detail="检测到可疑活动")
    
    def _record_request(self, client_ip: str, success: bool):
        """记录请求"""
        # 这里可以扩展为更详细的请求记录
        pass
    
    def _record_failed_request(self, client_ip: str, status_code: int):
        """记录失败请求"""
        current_time = time.time()
        failed_requests = self.failed_requests[client_ip]
        
        # 清理过期记录
        while failed_requests and failed_requests[0] < current_time - 300:  # 5分钟窗口
            failed_requests.popleft()
        
        failed_requests.append(current_time)
        
        # 如果失败请求过多，标记为可疑
        if len(failed_requests) > 10:
            self.suspicious_ips[client_ip] += 1
            self.logger.warning(f"IP {client_ip} 失败请求过多: {len(failed_requests)}")
    
    def _add_security_headers(self, response: Response, request_path: str = ''):
        """添加安全头部"""
        # 为 Swagger UI 文档页面使用更宽松的 CSP 策略

        if request_path in ['/docs', '/redoc']:
            # Swagger UI 需要的 CSP 策略
            csp_policy = (
                "default-src 'self'; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fastapi.tiangolo.com; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https://fastapi.tiangolo.com https://cdn.jsdelivr.net; "
                "font-src 'self' https://cdn.jsdelivr.net; "
                "connect-src 'self'"
            )
        else:
            # 其他页面使用严格的 CSP 策略
            csp_policy = "default-src 'self'"

        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": csp_policy,
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        for header, value in security_headers.items():
            response.headers[header] = value
    
    def get_security_stats(self) -> Dict[str, Any]:
        """获取安全统计"""
        return {
            "blocked_ips": list(self.blocked_ips),
            "suspicious_ips": dict(self.suspicious_ips),
            "active_rate_limits": len(self.request_counts),
            "total_failed_requests": sum(len(reqs) for reqs in self.failed_requests.values())
        }
    
    def unblock_ip(self, ip: str):
        """解除IP阻止"""
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            self.logger.info(f"解除IP阻止: {ip}")
    
    def block_ip(self, ip: str):
        """阻止IP"""
        self.blocked_ips.add(ip)
        self.logger.info(f"阻止IP: {ip}")


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """认证中间件"""
    
    def __init__(self, app, protected_paths: Optional[Set[str]] = None, api_keys: Optional[Set[str]] = None):
        super().__init__(app)
        self.logger = get_logger("auth")
        self.protected_paths = protected_paths or {
            "/system/reset",
            "/config/update", 
            "/knowledge-graph/clear"
        }
        self.api_keys = api_keys or set()
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 检查是否需要认证
        if not any(path in request.url.path for path in self.protected_paths):
            return await call_next(request)
        
        # 检查API密钥
        api_key = request.headers.get("x-api-key") or request.query_params.get("api_key")
        
        if not api_key:
            self.logger.warning(f"缺少API密钥 - 路径: {request.url.path}")
            raise HTTPException(status_code=401, detail="需要API密钥")
        
        if self.api_keys and api_key not in self.api_keys:
            self.logger.warning(f"无效API密钥 - 路径: {request.url.path}")
            raise HTTPException(status_code=401, detail="无效的API密钥")
        
        # 记录认证成功
        self.logger.info(f"认证成功 - 路径: {request.url.path}")
        
        return await call_next(request)


class InputValidationMiddleware(BaseHTTPMiddleware):
    """输入验证中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = get_logger("input_validation")
        
        # 危险字符模式
        self.dangerous_patterns = [
            r"<script[^>]*>.*?</script>",  # XSS
            r"javascript:",  # JavaScript协议
            r"on\w+\s*=",  # 事件处理器
            r"union\s+select",  # SQL注入
            r"drop\s+table",  # SQL删除
            r"\.\./",  # 路径遍历
            r"eval\s*\(",  # 代码执行
            r"exec\s*\(",  # 代码执行
        ]
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 验证查询参数
        for key, value in request.query_params.items():
            if self._contains_dangerous_content(value):
                self.logger.warning(f"危险查询参数 - {key}: {value}")
                raise HTTPException(status_code=400, detail="检测到危险输入")
        
        # 验证请求体（如果是POST/PUT/PATCH）
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body and self._contains_dangerous_content(body.decode('utf-8', errors='ignore')):
                    self.logger.warning("危险请求体内容")
                    raise HTTPException(status_code=400, detail="检测到危险输入")
            except UnicodeDecodeError:
                # 如果无法解码，可能是二进制数据，跳过验证
                pass
        
        return await call_next(request)
    
    def _contains_dangerous_content(self, content: str) -> bool:
        """检查内容是否包含危险模式"""
        import re
        content_lower = content.lower()
        
        for pattern in self.dangerous_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return True
        
        return False


# 导出中间件
__all__ = [
    "SecurityMiddleware",
    "AuthenticationMiddleware",
    "InputValidationMiddleware"
]
