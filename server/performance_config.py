"""
性能优化配置
"""
from typing import Dict, Any
from .config import settings


class PerformanceConfig:
    """性能优化配置类"""
    
    # 基础性能配置
    BASIC_CONFIG = {
        "embedding_dim": 1536,  # 降低embedding维度以提高速度
        "max_token_size": 4096,  # 减少token大小
        "max_async": 4,  # 限制并发数
        "chunk_size": 512,  # 优化chunk大小
    }
    
    # 高性能配置（适合生产环境）
    HIGH_PERFORMANCE_CONFIG = {
        "embedding_dim": 2560,  # 保持高质量
        "max_token_size": 8192,
        "max_async": 8,
        "chunk_size": 1024,
        "enable_cache": True,
        "cache_size": 1000,
    }
    
    # 快速测试配置
    FAST_TEST_CONFIG = {
        "embedding_dim": 768,   # 最小维度
        "max_token_size": 2048,
        "max_async": 2,
        "chunk_size": 256,
        "enable_cache": True,
    }
    
    @classmethod
    def get_config(cls, mode: str = "basic") -> Dict[str, Any]:
        """获取指定模式的配置"""
        configs = {
            "basic": cls.BASIC_CONFIG,
            "high_performance": cls.HIGH_PERFORMANCE_CONFIG,
            "fast_test": cls.FAST_TEST_CONFIG,
        }
        return configs.get(mode, cls.BASIC_CONFIG)
    
    @classmethod
    def apply_config(cls, mode: str = "basic") -> Dict[str, Any]:
        """应用性能配置"""
        config = cls.get_config(mode)
        
        # 更新设置
        for key, value in config.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        return config


# 查询性能优化配置
QUERY_OPTIMIZATION = {
    "local_mode": {
        "top_k": 10,
        "max_entity_tokens": 2000,
        "max_relation_tokens": 1000,
        "enable_rerank": True,
    },
    "global_mode": {
        "top_k": 15,
        "max_entity_tokens": 3000,
        "max_relation_tokens": 2000,
        "enable_rerank": True,
    },
    "hybrid_mode": {
        "top_k": 20,
        "max_entity_tokens": 4000,
        "max_relation_tokens": 3000,
        "enable_rerank": True,
    },
    "fast_mode": {
        "top_k": 5,
        "max_entity_tokens": 1000,
        "max_relation_tokens": 500,
        "enable_rerank": False,
    }
}


def get_optimized_query_params(mode: str, performance_level: str = "balanced") -> Dict[str, Any]:
    """获取优化的查询参数"""
    base_params = QUERY_OPTIMIZATION.get(f"{mode}_mode", QUERY_OPTIMIZATION["hybrid_mode"])
    
    if performance_level == "fast":
        # 快速模式：减少参数以提高速度
        return {
            **base_params,
            "top_k": max(5, base_params["top_k"] // 2),
            "max_entity_tokens": base_params["max_entity_tokens"] // 2,
            "max_relation_tokens": base_params["max_relation_tokens"] // 2,
            "enable_rerank": False,
        }
    elif performance_level == "quality":
        # 质量模式：增加参数以提高质量
        return {
            **base_params,
            "top_k": min(50, base_params["top_k"] * 2),
            "max_entity_tokens": base_params["max_entity_tokens"] * 2,
            "max_relation_tokens": base_params["max_relation_tokens"] * 2,
            "enable_rerank": True,
        }
    else:
        # 平衡模式
        return base_params


# 批处理优化配置
BATCH_PROCESSING_CONFIG = {
    "max_batch_size": 10,  # 最大批处理大小
    "batch_timeout": 30,   # 批处理超时时间（秒）
    "parallel_workers": 4,  # 并行工作线程数
    "chunk_overlap": 50,   # chunk重叠大小
}


# 缓存配置
CACHE_CONFIG = {
    "enable_llm_cache": True,
    "enable_embedding_cache": True,
    "cache_ttl": 3600,  # 缓存生存时间（秒）
    "max_cache_size": 1000,  # 最大缓存条目数
}


# 监控和日志配置
MONITORING_CONFIG = {
    "enable_performance_monitoring": True,
    "log_slow_requests": True,
    "slow_request_threshold": 10.0,  # 慢请求阈值（秒）
    "enable_metrics_collection": True,
    "metrics_interval": 60,  # 指标收集间隔（秒）
}
