"""
性能监控中间件
"""
import time
import logging
import asyncio
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from fastapi import Request, Response
try:
    from fastapi.middleware.base import BaseHTTPMiddleware
except ImportError:
    from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint

from common.logging_utils import get_logger


class MetricsMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = get_logger("metrics")
        self.request_count = 0
        self.total_time = 0.0
        self.error_count = 0
        self.response_times = deque(maxlen=1000)  # 保留最近1000次请求的响应时间
        self.status_codes = defaultdict(int)
        self.endpoint_metrics = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'error_count': 0,
            'avg_time': 0.0
        })
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        endpoint = f"{request.method} {request.url.path}"
        
        try:
            response = await call_next(request)
            
            # 更新统计信息
            process_time = time.time() - start_time
            self.request_count += 1
            self.total_time += process_time
            self.response_times.append(process_time)
            self.status_codes[response.status_code] += 1
            
            # 更新端点统计
            endpoint_stat = self.endpoint_metrics[endpoint]
            endpoint_stat['count'] += 1
            endpoint_stat['total_time'] += process_time
            endpoint_stat['avg_time'] = endpoint_stat['total_time'] / endpoint_stat['count']
            
            # 记录慢请求
            if process_time > 10.0:  # 超过10秒的请求
                self.logger.warning(
                    f"慢请求检测 - 端点: {endpoint}, "
                    f"处理时间: {process_time:.3f}s, "
                    f"状态码: {response.status_code}"
                )
            
            # 添加性能头部
            response.headers["X-Response-Time"] = str(process_time)
            response.headers["X-Request-Count"] = str(self.request_count)
            
            return response
            
        except Exception as e:
            # 更新错误统计
            process_time = time.time() - start_time
            self.error_count += 1
            self.endpoint_metrics[endpoint]['error_count'] += 1
            
            self.logger.error(
                f"请求处理异常 - 端点: {endpoint}, "
                f"处理时间: {process_time:.3f}s, "
                f"错误: {str(e)}"
            )
            
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        avg_response_time = self.total_time / self.request_count if self.request_count > 0 else 0
        error_rate = self.error_count / self.request_count if self.request_count > 0 else 0
        
        # 计算响应时间百分位数
        sorted_times = sorted(self.response_times)
        percentiles = {}
        if sorted_times:
            percentiles = {
                'p50': sorted_times[int(len(sorted_times) * 0.5)],
                'p90': sorted_times[int(len(sorted_times) * 0.9)],
                'p95': sorted_times[int(len(sorted_times) * 0.95)],
                'p99': sorted_times[int(len(sorted_times) * 0.99)]
            }
        
        return {
            'request_count': self.request_count,
            'error_count': self.error_count,
            'error_rate': error_rate,
            'avg_response_time': avg_response_time,
            'total_time': self.total_time,
            'status_codes': dict(self.status_codes),
            'response_time_percentiles': percentiles,
            'endpoint_metrics': dict(self.endpoint_metrics)
        }
    
    def reset_metrics(self):
        """重置指标"""
        self.request_count = 0
        self.total_time = 0.0
        self.error_count = 0
        self.response_times.clear()
        self.status_codes.clear()
        self.endpoint_metrics.clear()


class AdvancedMetricsMiddleware(BaseHTTPMiddleware):
    """高级性能监控中间件"""
    
    def __init__(self, app, collection_interval: int = 60):
        super().__init__(app)
        self.logger = get_logger("advanced_metrics")
        self.collection_interval = collection_interval
        self.metrics_history = deque(maxlen=1440)  # 保留24小时的数据（每分钟一个点）
        self.current_metrics = {
            'requests': 0,
            'errors': 0,
            'total_time': 0.0,
            'memory_usage': 0.0,
            'cpu_usage': 0.0
        }
        self.last_collection = time.time()
        
        # 启动后台任务收集系统指标
        asyncio.create_task(self._collect_system_metrics())
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # 更新当前指标
            process_time = time.time() - start_time
            self.current_metrics['requests'] += 1
            self.current_metrics['total_time'] += process_time
            
            # 检查是否需要收集指标
            if time.time() - self.last_collection >= self.collection_interval:
                await self._collect_metrics()
            
            return response
            
        except Exception as e:
            self.current_metrics['errors'] += 1
            raise
    
    async def _collect_system_metrics(self):
        """收集系统指标"""
        while True:
            try:
                import psutil
                
                # 获取系统资源使用情况
                self.current_metrics['memory_usage'] = psutil.virtual_memory().percent
                self.current_metrics['cpu_usage'] = psutil.cpu_percent()
                
            except ImportError:
                # 如果没有psutil，使用简单的指标
                pass
            except Exception as e:
                self.logger.error(f"收集系统指标失败: {e}")
            
            await asyncio.sleep(30)  # 每30秒收集一次系统指标
    
    async def _collect_metrics(self):
        """收集并存储指标"""
        current_time = time.time()
        
        # 计算平均响应时间
        avg_response_time = (
            self.current_metrics['total_time'] / self.current_metrics['requests']
            if self.current_metrics['requests'] > 0 else 0
        )
        
        # 计算错误率
        error_rate = (
            self.current_metrics['errors'] / self.current_metrics['requests']
            if self.current_metrics['requests'] > 0 else 0
        )
        
        # 存储指标快照
        metrics_snapshot = {
            'timestamp': current_time,
            'requests_per_minute': self.current_metrics['requests'],
            'errors_per_minute': self.current_metrics['errors'],
            'avg_response_time': avg_response_time,
            'error_rate': error_rate,
            'memory_usage': self.current_metrics['memory_usage'],
            'cpu_usage': self.current_metrics['cpu_usage']
        }
        
        self.metrics_history.append(metrics_snapshot)
        
        # 记录指标日志
        self.logger.info(f"指标收集: {metrics_snapshot}")
        
        # 重置当前指标
        self.current_metrics = {
            'requests': 0,
            'errors': 0,
            'total_time': 0.0,
            'memory_usage': self.current_metrics['memory_usage'],
            'cpu_usage': self.current_metrics['cpu_usage']
        }
        
        self.last_collection = current_time
    
    def get_metrics_history(self, hours: int = 1) -> list:
        """获取指标历史"""
        cutoff_time = time.time() - (hours * 3600)
        return [
            metric for metric in self.metrics_history
            if metric['timestamp'] >= cutoff_time
        ]
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """获取当前指标"""
        return self.current_metrics.copy()


class ResourceMonitoringMiddleware(BaseHTTPMiddleware):
    """资源监控中间件"""
    
    def __init__(self, app, memory_threshold: float = 0.8, cpu_threshold: float = 0.8):
        super().__init__(app)
        self.logger = get_logger("resource_monitor")
        self.memory_threshold = memory_threshold
        self.cpu_threshold = cpu_threshold
        self.alert_cooldown = 300  # 5分钟告警冷却
        self.last_memory_alert = 0
        self.last_cpu_alert = 0
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 检查资源使用情况
        await self._check_resources()
        
        # 处理请求
        response = await call_next(request)
        
        return response
    
    async def _check_resources(self):
        """检查系统资源"""
        try:
            import psutil
            
            current_time = time.time()
            
            # 检查内存使用
            memory_percent = psutil.virtual_memory().percent / 100
            if memory_percent > self.memory_threshold:
                if current_time - self.last_memory_alert > self.alert_cooldown:
                    self.logger.warning(
                        f"内存使用率过高: {memory_percent:.1%}, "
                        f"阈值: {self.memory_threshold:.1%}"
                    )
                    self.last_memory_alert = current_time
            
            # 检查CPU使用
            cpu_percent = psutil.cpu_percent() / 100
            if cpu_percent > self.cpu_threshold:
                if current_time - self.last_cpu_alert > self.alert_cooldown:
                    self.logger.warning(
                        f"CPU使用率过高: {cpu_percent:.1%}, "
                        f"阈值: {self.cpu_threshold:.1%}"
                    )
                    self.last_cpu_alert = current_time
                    
        except ImportError:
            # 如果没有psutil，跳过资源检查
            pass
        except Exception as e:
            self.logger.error(f"资源检查失败: {e}")


# 全局指标实例
metrics_middleware_instance: Optional[MetricsMiddleware] = None

def get_metrics() -> Dict[str, Any]:
    """获取全局指标"""
    if metrics_middleware_instance:
        return metrics_middleware_instance.get_metrics()
    return {}

def reset_metrics():
    """重置全局指标"""
    if metrics_middleware_instance:
        metrics_middleware_instance.reset_metrics()


# 导出中间件
__all__ = [
    "MetricsMiddleware",
    "AdvancedMetricsMiddleware",
    "ResourceMonitoringMiddleware",
    "get_metrics",
    "reset_metrics"
]
