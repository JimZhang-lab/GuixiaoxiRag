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

    # 大模型配置 - 支持用户自定义，未配置时使用默认值
    openai_api_base: str = "http://localhost:8100/v1"
    openai_embedding_api_base: str = "http://localhost:8200/v1"
    openai_chat_api_key: str = "your_api_key_here"
    openai_embedding_api_key: str = "your_api_key_here"  # Embedding API密钥
    openai_chat_model: str = "qwen14b"
    openai_embedding_model: str = "embedding_qwen"

    # 可选的自定义配置
    custom_llm_provider: Optional[str] = None  # 自定义LLM提供商 (openai, azure, ollama, etc.)
    custom_embedding_provider: Optional[str] = None  # 自定义Embedding提供商
    azure_api_version: Optional[str] = None  # Azure API版本
    azure_deployment_name: Optional[str] = None  # Azure部署名称

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
    warnings = []

    # 验证端口范围
    if not (1 <= settings.port <= 65535):
        errors.append(f"端口号无效: {settings.port}")

    if not (1 <= settings.streamlit_port <= 65535):
        errors.append(f"Streamlit端口号无效: {settings.streamlit_port}")

    # 智能验证API配置
    if settings.openai_chat_api_key == "your_api_key_here":
        warnings.append("使用默认LLM API密钥，请在生产环境中设置有效的API密钥")

    if settings.openai_embedding_api_key == "your_api_key_here":
        warnings.append("使用默认Embedding API密钥，请在生产环境中设置有效的API密钥")

    # 验证API基础URL格式
    if not settings.openai_api_base.startswith(('http://', 'https://')):
        errors.append(f"LLM API基础URL格式无效: {settings.openai_api_base}")

    if not settings.openai_embedding_api_base.startswith(('http://', 'https://')):
        errors.append(f"Embedding API基础URL格式无效: {settings.openai_embedding_api_base}")

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

    # 输出验证结果
    if warnings:
        print("⚠️  配置警告:")
        for warning in warnings:
            print(f"   - {warning}")

    if errors:
        print("❌ 配置错误:")
        for error in errors:
            print(f"   - {error}")

    return len(errors) == 0

# 智能配置处理函数
def get_effective_config():
    """获取有效的配置信息，处理用户自定义和默认值"""
    config = {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "host": settings.host,
        "port": settings.port,
        "debug": settings.debug,
        "working_dir": settings.working_dir,
        "log_level": settings.log_level,

        # LLM配置
        "llm": {
            "api_base": settings.openai_api_base,
            "api_key": "***" if settings.openai_chat_api_key != "your_api_key_here" else "未配置",
            "model": settings.openai_chat_model,
            "provider": settings.custom_llm_provider or "openai",
        },

        # Embedding配置
        "embedding": {
            "api_base": settings.openai_embedding_api_base,
            "api_key": "***" if settings.openai_embedding_api_key != "your_api_key_here" else "未配置",
            "model": settings.openai_embedding_model,
            "dim": settings.embedding_dim,
            "provider": settings.custom_embedding_provider or "openai",
        },

        # 其他配置
        "max_file_size_mb": settings.max_file_size // (1024 * 1024),
        "streamlit_port": settings.streamlit_port,
        "max_token_size": settings.max_token_size,
    }

    # 添加Azure特定配置（如果配置了）
    if settings.azure_api_version:
        config["azure"] = {
            "api_version": settings.azure_api_version,
            "deployment_name": settings.azure_deployment_name,
        }

    return config

# 获取配置摘要（保持向后兼容）
def get_config_summary():
    """获取配置摘要信息"""
    effective_config = get_effective_config()
    return {
        "app_name": effective_config["app_name"],
        "version": effective_config["version"],
        "host": effective_config["host"],
        "port": effective_config["port"],
        "debug": effective_config["debug"],
        "working_dir": effective_config["working_dir"],
        "log_level": effective_config["log_level"],
        "openai_chat_model": effective_config["llm"]["model"],
        "openai_embedding_model": effective_config["embedding"]["model"],
        "embedding_dim": effective_config["embedding"]["dim"],
        "max_file_size_mb": effective_config["max_file_size_mb"],
        "streamlit_port": effective_config["streamlit_port"],
    }

# 导出常用配置
__all__ = ["settings", "ensure_directories", "validate_config", "get_config_summary", "get_effective_config", "get_project_root"]
