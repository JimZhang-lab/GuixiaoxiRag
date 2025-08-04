"""
GuiXiaoXiRag FastAPI服务配置文件
"""
import os
from pathlib import Path
from typing import Optional, List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


def get_project_root() -> Path:
    """获取项目根目录"""
    current_file = Path(__file__).resolve()
    # 从 server/config.py 向上两级到达项目根目录
    return current_file.parent.parent


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    app_name: str = "GuiXiaoXiRag FastAPI Service"
    app_version: str = "1.0.0"

    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8002
    debug: bool = False
    workers: int = 1

    # GuiXiaoXiRag配置
    working_dir: str = "./knowledgeBase/default"

    # 大模型配置
    openai_api_base: str = "http://localhost:8100/v1"
    openai_embedding_api_base: str = "http://localhost:8200/v1"
    openai_chat_api_key: str = "your_api_key_here"
    openai_chat_model: str = "qwen14b"
    openai_embedding_model: str = "embedding_qwen"

    # Embedding配置
    embedding_dim: int = 1536
    max_token_size: int = 8192

    # 日志配置
    log_level: str = "INFO"
    log_dir: str = "./logs"

    # 文件上传配置
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: List[str] = [".txt", ".pdf", ".docx", ".doc", ".md", ".json", ".xml", ".csv"]
    upload_dir: str = "./uploads"

    # Streamlit配置
    streamlit_host: str = "0.0.0.0"
    streamlit_port: int = 8501
    streamlit_api_url: str = "http://localhost:8002"
    streamlit_timeout: int = 120

    # 性能配置
    enable_cache: bool = True
    cache_ttl: int = 3600
    max_concurrent_requests: int = 100

    # 安全配置
    cors_origins: List[str] = ["*"]
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]

    class Config:
        # 指定从项目根目录读取 .env 文件
        env_file = get_project_root() / ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # 忽略额外的字段，避免验证错误
        extra = "ignore"
        # 支持从多个位置读取环境文件
        env_files = [
            get_project_root() / ".env",
            get_project_root() / ".env.local",
            Path.cwd() / ".env"
        ]


# 全局配置实例
settings = Settings()

# 确保必要的目录存在
def ensure_directories():
    """确保必要的目录存在"""
    directories = [
        settings.working_dir,
        settings.log_dir,
        settings.upload_dir,
        Path(settings.working_dir).parent,  # knowledgeBase目录
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# 初始化目录
ensure_directories()

# 配置验证函数
def validate_config():
    """验证配置的有效性"""
    errors = []

    # 验证端口范围
    if not (1 <= settings.port <= 65535):
        errors.append(f"端口号无效: {settings.port}")

    if not (1 <= settings.streamlit_port <= 65535):
        errors.append(f"Streamlit端口号无效: {settings.streamlit_port}")

    # 验证API密钥
    if settings.openai_chat_api_key == "your_api_key_here":
        errors.append("请设置有效的OpenAI API密钥")

    # 验证目录路径
    try:
        Path(settings.working_dir).resolve()
        Path(settings.log_dir).resolve()
        Path(settings.upload_dir).resolve()
    except Exception as e:
        errors.append(f"目录路径无效: {e}")

    # 验证文件大小
    if settings.max_file_size <= 0:
        errors.append("文件大小限制必须大于0")

    if errors:
        print("⚠️  配置验证警告:")
        for error in errors:
            print(f"   - {error}")

    return len(errors) == 0

# 获取配置摘要
def get_config_summary():
    """获取配置摘要信息"""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "host": settings.host,
        "port": settings.port,
        "debug": settings.debug,
        "working_dir": settings.working_dir,
        "log_level": settings.log_level,
        "openai_chat_model": settings.openai_chat_model,
        "openai_embedding_model": settings.openai_embedding_model,
        "embedding_dim": settings.embedding_dim,
        "max_file_size_mb": settings.max_file_size // (1024 * 1024),
        "streamlit_port": settings.streamlit_port,
    }

# 导出常用配置
__all__ = ["settings", "ensure_directories", "validate_config", "get_config_summary", "get_project_root"]
