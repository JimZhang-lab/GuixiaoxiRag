"""
日志工具函数
"""
import os
import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from .config import settings


def setup_logging(
    logger_name: Optional[str] = None,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None
):
    """设置日志配置"""
    # 使用配置中的日志级别
    level = log_level or settings.log_level
    
    # 确保日志目录存在
    os.makedirs(settings.log_dir, exist_ok=True)
    
    # 配置日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 创建格式化器
    formatter = logging.Formatter(log_format)
    
    # 获取或创建日志器
    if logger_name:
        logger = logging.getLogger(logger_name)
    else:
        logger = logging.getLogger()
    
    # 设置日志级别
    logger.setLevel(getattr(logging, level.upper()))
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 添加文件处理器
    if log_file:
        file_path = os.path.join(settings.log_dir, log_file)
    else:
        file_path = os.path.join(settings.log_dir, "guixiaoxirag_service.log")
    
    # 使用RotatingFileHandler避免日志文件过大，添加延迟参数避免文件锁定
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8',
            delay=True  # 延迟创建文件，避免启动时的文件锁定问题
        )
    except (OSError, PermissionError) as e:
        # 如果文件被锁定，使用控制台日志
        print(f"警告: 无法创建日志文件 {file_path}: {e}")
        print("将仅使用控制台日志")
        return logger
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志器"""
    return logging.getLogger(name)


def log_performance(logger: logging.Logger, operation: str, duration: float, **kwargs):
    """记录性能日志"""
    extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.info(f"性能监控 - 操作: {operation}, 耗时: {duration:.3f}s, {extra_info}")


def log_error_with_context(logger: logging.Logger, error: Exception, context: dict = None):
    """记录带上下文的错误日志"""
    context_info = ""
    if context:
        context_info = " ".join([f"{k}={v}" for k, v in context.items()])
    
    logger.error(f"错误发生 - {str(error)}, 上下文: {context_info}", exc_info=True)


def log_api_request(logger: logging.Logger, method: str, path: str, status_code: int, duration: float):
    """记录API请求日志"""
    logger.info(f"API请求 - {method} {path} - 状态码: {status_code}, 耗时: {duration:.3f}s")


def log_system_status(logger: logging.Logger, status: str, details: dict = None):
    """记录系统状态日志"""
    details_info = ""
    if details:
        details_info = " ".join([f"{k}={v}" for k, v in details.items()])
    
    logger.info(f"系统状态 - {status}, 详情: {details_info}")


class ContextualLogger:
    """带上下文的日志器"""
    
    def __init__(self, logger: logging.Logger, context: dict = None):
        self.logger = logger
        self.context = context or {}
    
    def _format_message(self, message: str) -> str:
        """格式化消息，添加上下文信息"""
        if self.context:
            context_str = " ".join([f"{k}={v}" for k, v in self.context.items()])
            return f"{message} [上下文: {context_str}]"
        return message
    
    def debug(self, message: str, **kwargs):
        """记录调试日志"""
        self.logger.debug(self._format_message(message), **kwargs)
    
    def info(self, message: str, **kwargs):
        """记录信息日志"""
        self.logger.info(self._format_message(message), **kwargs)
    
    def warning(self, message: str, **kwargs):
        """记录警告日志"""
        self.logger.warning(self._format_message(message), **kwargs)
    
    def error(self, message: str, **kwargs):
        """记录错误日志"""
        self.logger.error(self._format_message(message), **kwargs)
    
    def critical(self, message: str, **kwargs):
        """记录严重错误日志"""
        self.logger.critical(self._format_message(message), **kwargs)
    
    def add_context(self, **kwargs):
        """添加上下文信息"""
        self.context.update(kwargs)
    
    def remove_context(self, *keys):
        """移除上下文信息"""
        for key in keys:
            self.context.pop(key, None)


class LoggerManager:
    """日志管理器"""
    
    def __init__(self):
        self._loggers = {}
    
    def get_logger(self, name: str, context: dict = None) -> ContextualLogger:
        """获取带上下文的日志器"""
        if name not in self._loggers:
            self._loggers[name] = setup_logging(name)
        
        return ContextualLogger(self._loggers[name], context)
    
    def setup_api_logger(self) -> ContextualLogger:
        """设置API日志器"""
        return self.get_logger("api", {"component": "api"})
    
    def setup_service_logger(self) -> ContextualLogger:
        """设置服务日志器"""
        return self.get_logger("service", {"component": "service"})
    
    def setup_query_logger(self) -> ContextualLogger:
        """设置查询日志器"""
        return self.get_logger("query", {"component": "query"})
    
    def setup_knowledge_base_logger(self) -> ContextualLogger:
        """设置知识库日志器"""
        return self.get_logger("knowledge_base", {"component": "knowledge_base"})


# 全局日志管理器实例
logger_manager = LoggerManager()

# 导出常用函数
__all__ = [
    "setup_logging",
    "get_logger", 
    "log_performance",
    "log_error_with_context",
    "log_api_request",
    "log_system_status",
    "ContextualLogger",
    "LoggerManager",
    "logger_manager"
]
