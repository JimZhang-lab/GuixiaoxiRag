"""
测试日志管理器
提供统一的日志记录功能
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class TestLogger:
    """测试日志管理器"""
    
    def __init__(self, name: str = "SystemTest", log_dir: Optional[Path] = None):
        self.name = name
        self.log_dir = log_dir or Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # 创建logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 避免重复添加handler
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """设置日志处理器"""
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # 控制台格式（简化）
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # 文件处理器
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"test_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 文件格式（详细）
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # 添加处理器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
        self.log_file = log_file
    
    def set_verbose(self, verbose: bool = True):
        """设置详细模式"""
        level = logging.DEBUG if verbose else logging.INFO
        self.logger.setLevel(level)

        # 更新所有处理器级别
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                # 控制台处理器
                handler.setLevel(level)
                if verbose:
                    # 在详细模式下，控制台也显示更详细的格式
                    verbose_formatter = logging.Formatter(
                        '%(levelname)s - %(name)s - %(message)s'
                    )
                    handler.setFormatter(verbose_formatter)
            elif isinstance(handler, logging.FileHandler):
                # 文件处理器始终记录DEBUG级别
                handler.setLevel(logging.DEBUG)
    
    def info(self, message: str):
        """记录信息日志"""
        self.logger.info(message)
    
    def debug(self, message: str):
        """记录调试日志"""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """记录错误日志"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """记录严重错误日志"""
        self.logger.critical(message)
    
    def test_start(self, test_name: str):
        """记录测试开始"""
        self.info(f"🧪 开始测试: {test_name}")
    
    def test_pass(self, test_name: str, duration: float = None):
        """记录测试通过"""
        duration_str = f" ({duration:.2f}s)" if duration else ""
        self.info(f"✅ 测试通过: {test_name}{duration_str}")
    
    def test_fail(self, test_name: str, error: str = None, duration: float = None):
        """记录测试失败"""
        duration_str = f" ({duration:.2f}s)" if duration else ""
        error_str = f" - {error}" if error else ""
        self.error(f"❌ 测试失败: {test_name}{duration_str}{error_str}")
    
    def test_skip(self, test_name: str, reason: str = None):
        """记录测试跳过"""
        reason_str = f" - {reason}" if reason else ""
        self.warning(f"⏭️ 测试跳过: {test_name}{reason_str}")
    
    def section(self, title: str):
        """记录章节标题"""
        separator = "=" * 60
        self.info(separator)
        self.info(title)
        self.info(separator)
    
    def subsection(self, title: str):
        """记录子章节标题"""
        separator = "-" * 40
        self.info(separator)
        self.info(title)
        self.info(separator)
    
    def progress(self, current: int, total: int, item: str = ""):
        """记录进度"""
        percentage = (current / total) * 100 if total > 0 else 0
        item_str = f" - {item}" if item else ""
        self.info(f"📋 进度: {current}/{total} ({percentage:.1f}%){item_str}")
    
    def summary(self, total: int, passed: int, failed: int, skipped: int = 0):
        """记录测试摘要"""
        self.section("📊 测试摘要")
        self.info(f"总测试数: {total}")
        self.info(f"通过: {passed}")
        self.info(f"失败: {failed}")
        if skipped > 0:
            self.info(f"跳过: {skipped}")
        
        success_rate = (passed / total) * 100 if total > 0 else 0
        self.info(f"成功率: {success_rate:.1f}%")
        
        if failed == 0:
            self.info("🎉 所有测试通过！")
        elif passed > 0:
            self.info("✅ 部分测试通过")
        else:
            self.error("❌ 所有测试失败")
    
    def get_log_file(self) -> Path:
        """获取日志文件路径"""
        return getattr(self, 'log_file', None)


# 创建默认logger实例
default_logger = TestLogger()
