"""
全局常量定义
"""
from typing import List, Dict, Any

# API版本
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

# 支持的查询模式
SUPPORTED_QUERY_MODES = [
    "local",
    "global", 
    "hybrid",
    "naive",
    "mix",
    "bypass"
]

# 查询模式描述
QUERY_MODE_DESCRIPTIONS = {
    "local": "本地模式 - 专注于上下文相关信息",
    "global": "全局模式 - 利用全局知识",
    "hybrid": "混合模式 - 结合本地和全局检索方法",
    "naive": "朴素模式 - 执行基本搜索，不使用高级技术",
    "mix": "混合模式 - 整合知识图谱和向量检索",
    "bypass": "绕过模式 - 直接返回结果"
}

# 默认查询模式
DEFAULT_QUERY_MODE = "hybrid"

# 推荐查询模式
RECOMMENDED_QUERY_MODES = ["hybrid", "mix", "local"]

# 支持的语言
SUPPORTED_LANGUAGES = [
    "中文", "英文", "English", "Chinese", 
    "zh", "en", "zh-CN", "en-US"
]

# 默认语言
DEFAULT_LANGUAGE = "中文"

# 支持的文件类型
SUPPORTED_FILE_TYPES = [
    ".txt", ".pdf", ".docx", ".doc", 
    ".md", ".json", ".xml", ".csv",
    ".py", ".js", ".java", ".cpp", 
    ".c", ".h", ".rst"
]

# 文件类型描述
FILE_TYPE_DESCRIPTIONS = {
    ".txt": "纯文本文件",
    ".pdf": "PDF文档",
    ".docx": "Word文档(新版)",
    ".doc": "Word文档(旧版)",
    ".md": "Markdown文档",
    ".json": "JSON数据文件",
    ".xml": "XML数据文件",
    ".csv": "CSV表格文件",
    ".py": "Python代码文件",
    ".js": "JavaScript代码文件",
    ".java": "Java代码文件",
    ".cpp": "C++代码文件",
    ".c": "C代码文件",
    ".h": "头文件",
    ".rst": "reStructuredText文档"
}

# 默认配置值
DEFAULT_CONFIG = {
    "top_k": 20,
    "max_entity_tokens": 4000,
    "max_relation_tokens": 3000,
    "max_total_tokens": 8192,
    "enable_rerank": True,
    "chunk_size": 1024,
    "chunk_overlap": 50,
    "embedding_dim": 1536,
    "max_file_size": 50 * 1024 * 1024,  # 50MB
    "cache_ttl": 3600,  # 1小时
    "max_concurrent_requests": 100
}

# HTTP状态码
HTTP_STATUS = {
    "OK": 200,
    "CREATED": 201,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "METHOD_NOT_ALLOWED": 405,
    "CONFLICT": 409,
    "PAYLOAD_TOO_LARGE": 413,
    "UNPROCESSABLE_ENTITY": 422,
    "INTERNAL_SERVER_ERROR": 500,
    "BAD_GATEWAY": 502,
    "SERVICE_UNAVAILABLE": 503
}

# 错误消息
ERROR_MESSAGES = {
    "INVALID_QUERY_MODE": "无效的查询模式",
    "EMPTY_QUERY": "查询内容不能为空",
    "FILE_TOO_LARGE": "文件大小超过限制",
    "UNSUPPORTED_FILE_TYPE": "不支持的文件类型",
    "KNOWLEDGE_BASE_NOT_FOUND": "知识库不存在",
    "SERVICE_NOT_INITIALIZED": "服务未初始化",
    "INVALID_LANGUAGE": "不支持的语言",
    "PROCESSING_FAILED": "处理失败",
    "NETWORK_ERROR": "网络连接错误",
    "TIMEOUT_ERROR": "请求超时",
    "PERMISSION_DENIED": "权限不足"
}

# 成功消息
SUCCESS_MESSAGES = {
    "OPERATION_SUCCESS": "操作成功",
    "INSERT_SUCCESS": "插入成功",
    "QUERY_SUCCESS": "查询成功",
    "UPDATE_SUCCESS": "更新成功",
    "DELETE_SUCCESS": "删除成功",
    "UPLOAD_SUCCESS": "上传成功",
    "INITIALIZATION_SUCCESS": "初始化成功",
    "RESET_SUCCESS": "重置成功"
}

# 日志级别
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# 性能配置模式
PERFORMANCE_MODES = {
    "fast": "快速模式",
    "balanced": "平衡模式", 
    "quality": "质量模式"
}

# 安全级别
SAFETY_LEVELS = {
    "safe": "安全",
    "suspicious": "可疑",
    "unsafe": "不安全",
    "illegal": "非法"
}

# 意图类型
INTENT_TYPES = {
    "knowledge_query": "知识查询",
    "factual_question": "事实性问题",
    "analytical_question": "分析性问题",
    "procedural_question": "程序性问题",
    "creative_request": "创意请求",
    "greeting": "问候",
    "unclear": "意图不明确",
    "illegal_content": "非法内容"
}

# 响应类型
RESPONSE_TYPES = [
    "Multiple Paragraphs",
    "Single Paragraph", 
    "Single Sentence",
    "List of Points",
    "JSON Format"
]

# 缓存键前缀
CACHE_PREFIXES = {
    "query": "query:",
    "embedding": "embedding:",
    "llm": "llm:",
    "knowledge_graph": "kg:",
    "document": "doc:"
}

# 系统状态
SYSTEM_STATUS = {
    "HEALTHY": "healthy",
    "DEGRADED": "degraded",
    "UNHEALTHY": "unhealthy",
    "INITIALIZING": "initializing",
    "SHUTTING_DOWN": "shutting_down"
}

# 知识图谱配置
KNOWLEDGE_GRAPH_CONFIG = {
    "max_nodes": 1000,
    "max_edges": 2000,
    "max_depth": 5,
    "default_layout": "spring",
    "node_size_field": "degree",
    "edge_width_field": "weight"
}

# 批处理配置
BATCH_CONFIG = {
    "max_batch_size": 50,
    "batch_timeout": 300,  # 5分钟
    "parallel_workers": 4,
    "retry_attempts": 3
}

# 监控配置
MONITORING_CONFIG = {
    "metrics_interval": 60,  # 秒
    "slow_request_threshold": 10.0,  # 秒
    "error_rate_threshold": 0.05,  # 5%
    "memory_threshold": 0.8,  # 80%
    "cpu_threshold": 0.8  # 80%
}
