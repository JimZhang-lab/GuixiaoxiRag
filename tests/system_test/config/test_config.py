"""
测试配置文件
集中管理所有测试相关的配置
"""

from pathlib import Path
from typing import Dict, List, Any

# 基础配置
BASE_CONFIG = {
    "base_url": "http://localhost:8002",
    "api_prefix": "/api/v1",
    "timeout": 60,  # 增加超时时间，因为文本插入很慢
    "max_retries": 3,
    "test_data_dir": "test_data",
    "temp_dir": "temp",
    "logs_dir": "logs"
}

# API端点配置
API_ENDPOINTS = {
    "qa": {
        "health": "/qa/health",
        "pairs": "/qa/pairs",
        "pairs_batch": "/qa/pairs/batch",
        "query": "/qa/query",
        "query_batch": "/qa/query/batch",
        "clear": "/qa/clear",
        "categories": "/qa/categories",
        "statistics": "/qa/statistics",
        "export": "/qa/export",
        "import": "/qa/import"
    },
    "document": {
        "insert_text": "/insert/text",
        "insert_texts": "/insert/texts",
        "insert_file": "/insert/file",
        "insert_files": "/insert/files",
        "insert_directory": "/insert/directory"
    },
    "query": {
        "query": "/query",
        "batch": "/query/batch",
        "modes": "/query/modes",
        "optimized": "/query/optimized"
    },
    "system": {
        "health": "/health",
        "status": "/system/status",
        "metrics": "/metrics",
        "logs": "/logs",
        "reset": "/system/reset",
        "config": "/service/config",
        "effective_config": "/service/effective-config",
        "update_config": "/service/config/update"
    },
    "knowledge_base": {
        "list": "/knowledge-bases",
        "create": "/knowledge-bases",
        "delete": "/knowledge-bases/{name}",
        "switch": "/knowledge-bases/switch",
        "current": "/knowledge-bases/current"
    },
    "knowledge_graph": {
        "query": "/knowledge-graph",
        "stats": "/knowledge-graph/stats",
        "clear": "/knowledge-graph/clear",
        "status": "/knowledge-graph/status",
        "convert": "/knowledge-graph/convert"
    },
    "intent": {
        "health": "/intent/health",
        "analyze": "/intent/analyze",
        "safety_check": "/intent/safety-check",
        "status": "/intent/status"
    }
}

# 测试数据配置
TEST_DATA = {
    "sample_qa_pairs": [
        {
            "question": "什么是人工智能？",
            "answer": "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
            "category": "AI基础",
            "confidence": 1.0,
            "keywords": ["人工智能", "AI", "计算机科学"],
            "source": "test_data"
        },
        {
            "question": "What is testing?",
            "answer": "Testing is the process of verifying software functionality",
            "category": "basic_test",
            "confidence": 0.9,
            "keywords": ["testing", "verification", "software"],
            "source": "test_data"
        }
    ],
    "sample_documents": [
        {
            "text": "人工智能技术正在快速发展，包括机器学习、深度学习、自然语言处理等多个领域。",
            "doc_id": "doc_001",
            "knowledge_base": "test_kb",
            "language": "中文"
        },
        {
            "text": "This is a test document for verifying text insertion functionality.",
            "doc_id": "doc_002",
            "knowledge_base": "test_kb",
            "language": "English"
        }
    ],
    "sample_queries": [
        {
            "query": "What is artificial intelligence?",
            "mode": "hybrid",
            "top_k": 5
        },
        {
            "query": "什么是机器学习？",
            "mode": "local",
            "top_k": 3
        }
    ]
}

# 测试套件配置
TEST_SUITES = {
    "basic": {
        "name": "基础功能测试",
        "description": "测试系统的基本功能",
        "tests": [
            "test_system_health",
            "test_qa_health",
            "test_create_qa_pair",
            "test_qa_query",
            "test_basic_query",
            "test_query_modes",
            "test_qa_statistics"
        ],
        "skip_slow": True
    },
    "full": {
        "name": "完整功能测试",
        "description": "测试所有功能包括慢速操作",
        "tests": [
            "test_system_health",
            "test_qa_health",
            "test_create_qa_pair",
            "test_qa_query",
            "test_insert_text",
            "test_basic_query",
            "test_query_modes",
            "test_qa_statistics",
            "test_file_upload"
        ],
        "skip_slow": False
    },
    "performance": {
        "name": "性能测试",
        "description": "测试系统性能和压力",
        "tests": [
            "test_concurrent_queries",
            "test_large_document_insert",
            "test_batch_operations"
        ],
        "skip_slow": False
    }
}

# 清理配置
CLEANUP_CONFIG = {
    "patterns_to_clean": [
        "logs/*.log",
        "logs/*.json",
        "logs/*.md",
        "temp/*",
        "test_data/*",
        "__pycache__/*",
        "*.pyc",
        ".pytest_cache/*"
    ],
    "directories_to_clean": [
        "logs",
        "temp",
        "test_data",
        "__pycache__",
        ".pytest_cache"
    ],
    "keep_directories": [
        "config",
        "fixtures", 
        "tests",
        "utils",
        "runners"
    ]
}

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "file_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "console_format": "%(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S"
}

# 性能配置
PERFORMANCE_CONFIG = {
    "concurrent_requests": 10,
    "request_interval": 0.1,
    "max_response_time": 30.0,
    "memory_limit_mb": 1024,
    "cpu_limit_percent": 80
}


class TestConfig:
    """测试配置管理类"""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(__file__).parent.parent
        self._config = BASE_CONFIG.copy()
        self._resolve_paths()
    
    def _resolve_paths(self):
        """解析相对路径为绝对路径"""
        for key in ["test_data_dir", "temp_dir", "logs_dir"]:
            if key in self._config:
                self._config[key] = str(self.base_dir / self._config[key])
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        self._config[key] = value
    
    def get_api_url(self, category: str, endpoint: str) -> str:
        """获取API端点的完整URL"""
        if category not in API_ENDPOINTS:
            raise ValueError(f"Unknown API category: {category}")
        
        if endpoint not in API_ENDPOINTS[category]:
            raise ValueError(f"Unknown endpoint: {endpoint} in category: {category}")
        
        endpoint_path = API_ENDPOINTS[category][endpoint]
        return f"{self._config['api_prefix']}{endpoint_path}"
    
    def get_test_suite(self, suite_name: str) -> Dict[str, Any]:
        """获取测试套件配置"""
        if suite_name not in TEST_SUITES:
            raise ValueError(f"Unknown test suite: {suite_name}")
        
        return TEST_SUITES[suite_name].copy()
    
    def get_test_data(self, data_type: str) -> Any:
        """获取测试数据"""
        if data_type not in TEST_DATA:
            raise ValueError(f"Unknown test data type: {data_type}")
        
        return TEST_DATA[data_type].copy()
    
    def get_cleanup_config(self) -> Dict[str, Any]:
        """获取清理配置"""
        return CLEANUP_CONFIG.copy()
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return LOGGING_CONFIG.copy()
    
    def get_performance_config(self) -> Dict[str, Any]:
        """获取性能配置"""
        return PERFORMANCE_CONFIG.copy()


# 全局配置实例
config = TestConfig()
