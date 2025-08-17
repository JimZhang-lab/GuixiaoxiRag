"""
性能优化配置
优化版本 - 更好的配置管理和性能调优
"""
from typing import Dict, Any
from .config import settings
from .constants import PERFORMANCE_MODES, DEFAULT_CONFIG


class PerformanceConfig:
    """性能优化配置类"""
    
    # 基础性能配置
    BASIC_CONFIG = {
        "embedding_dim": 1536,  # 降低embedding维度以提高速度
        "max_token_size": 4096,  # 减少token大小
        "max_async": 4,  # 限制并发数
        "chunk_size": 512,  # 优化chunk大小
        "enable_cache": True,
        "cache_size": 500,
    }
    
    # 高性能配置（适合生产环境）
    HIGH_PERFORMANCE_CONFIG = {
        "embedding_dim": 2560,  # 保持高质量
        "max_token_size": 8192,
        "max_async": 8,
        "chunk_size": 1024,
        "enable_cache": True,
        "cache_size": 1000,
        "enable_parallel_processing": True,
        "batch_size": 20,
    }
    
    # 快速测试配置
    FAST_TEST_CONFIG = {
        "embedding_dim": 768,   # 最小维度
        "max_token_size": 2048,
        "max_async": 2,
        "chunk_size": 256,
        "enable_cache": True,
        "cache_size": 100,
        "enable_parallel_processing": False,
    }
    
    # 内存优化配置
    MEMORY_OPTIMIZED_CONFIG = {
        "embedding_dim": 1024,
        "max_token_size": 4096,
        "max_async": 2,
        "chunk_size": 512,
        "enable_cache": False,  # 禁用缓存以节省内存
        "batch_size": 5,
        "enable_streaming": True,
    }
    
    @classmethod
    def get_config(cls, mode: str = "basic") -> Dict[str, Any]:
        """获取指定模式的配置"""
        configs = {
            "basic": cls.BASIC_CONFIG,
            "high_performance": cls.HIGH_PERFORMANCE_CONFIG,
            "fast_test": cls.FAST_TEST_CONFIG,
            "memory_optimized": cls.MEMORY_OPTIMIZED_CONFIG,
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
    
    @classmethod
    def get_recommended_config(cls, system_resources: Dict[str, Any] = None) -> str:
        """根据系统资源推荐配置模式"""
        if not system_resources:
            return "basic"
        
        memory_gb = system_resources.get("memory_gb", 8)
        cpu_cores = system_resources.get("cpu_cores", 4)
        
        if memory_gb >= 16 and cpu_cores >= 8:
            return "high_performance"
        elif memory_gb >= 8 and cpu_cores >= 4:
            return "basic"
        elif memory_gb < 4:
            return "memory_optimized"
        else:
            return "fast_test"


# 查询性能优化配置
QUERY_OPTIMIZATION = {
    "local_mode": {
        "top_k": 10,
        "max_entity_tokens": 2000,
        "max_relation_tokens": 1000,
        "enable_rerank": True,
        "timeout": 30,
    },
    "global_mode": {
        "top_k": 15,
        "max_entity_tokens": 3000,
        "max_relation_tokens": 2000,
        "enable_rerank": True,
        "timeout": 45,
    },
    "hybrid_mode": {
        "top_k": 20,
        "max_entity_tokens": 4000,
        "max_relation_tokens": 3000,
        "enable_rerank": True,
        "timeout": 60,
    },
    "naive_mode": {
        "top_k": 5,
        "max_entity_tokens": 1000,
        "max_relation_tokens": 500,
        "enable_rerank": False,
        "timeout": 15,
    },
    "mix_mode": {
        "top_k": 25,
        "max_entity_tokens": 5000,
        "max_relation_tokens": 4000,
        "enable_rerank": True,
        "timeout": 90,
    },
    "bypass_mode": {
        "top_k": 1,
        "max_entity_tokens": 100,
        "max_relation_tokens": 50,
        "enable_rerank": False,
        "timeout": 5,
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
            "timeout": base_params["timeout"] // 2,
        }
    elif performance_level == "quality":
        # 质量模式：增加参数以提高质量
        return {
            **base_params,
            "top_k": min(50, base_params["top_k"] * 2),
            "max_entity_tokens": base_params["max_entity_tokens"] * 2,
            "max_relation_tokens": base_params["max_relation_tokens"] * 2,
            "enable_rerank": True,
            "timeout": base_params["timeout"] * 2,
        }
    else:
        # 平衡模式
        return base_params


# 批处理优化配置
BATCH_PROCESSING_CONFIG = {
    "small_batch": {
        "max_batch_size": 5,
        "batch_timeout": 15,
        "parallel_workers": 2,
        "chunk_overlap": 25,
    },
    "medium_batch": {
        "max_batch_size": 10,
        "batch_timeout": 30,
        "parallel_workers": 4,
        "chunk_overlap": 50,
    },
    "large_batch": {
        "max_batch_size": 20,
        "batch_timeout": 60,
        "parallel_workers": 8,
        "chunk_overlap": 100,
    }
}


def get_batch_config(batch_size: int) -> Dict[str, Any]:
    """根据批处理大小获取优化配置"""
    if batch_size <= 5:
        return BATCH_PROCESSING_CONFIG["small_batch"]
    elif batch_size <= 15:
        return BATCH_PROCESSING_CONFIG["medium_batch"]
    else:
        return BATCH_PROCESSING_CONFIG["large_batch"]


# 缓存配置
CACHE_CONFIG = {
    "minimal": {
        "enable_llm_cache": False,
        "enable_embedding_cache": True,
        "cache_ttl": 1800,  # 30分钟
        "max_cache_size": 100,
    },
    "standard": {
        "enable_llm_cache": True,
        "enable_embedding_cache": True,
        "cache_ttl": 3600,  # 1小时
        "max_cache_size": 500,
    },
    "aggressive": {
        "enable_llm_cache": True,
        "enable_embedding_cache": True,
        "cache_ttl": 7200,  # 2小时
        "max_cache_size": 1000,
        "enable_persistent_cache": True,
    }
}


def get_cache_config(mode: str = "standard") -> Dict[str, Any]:
    """获取缓存配置"""
    return CACHE_CONFIG.get(mode, CACHE_CONFIG["standard"])


# 监控和日志配置
MONITORING_CONFIG = {
    "development": {
        "enable_performance_monitoring": True,
        "log_slow_requests": True,
        "slow_request_threshold": 5.0,
        "enable_metrics_collection": False,
        "metrics_interval": 300,  # 5分钟
        "log_level": "DEBUG",
    },
    "production": {
        "enable_performance_monitoring": True,
        "log_slow_requests": True,
        "slow_request_threshold": 10.0,
        "enable_metrics_collection": True,
        "metrics_interval": 60,  # 1分钟
        "log_level": "INFO",
    },
    "minimal": {
        "enable_performance_monitoring": False,
        "log_slow_requests": False,
        "enable_metrics_collection": False,
        "log_level": "WARNING",
    }
}


def get_monitoring_config(environment: str = "development") -> Dict[str, Any]:
    """获取监控配置"""
    return MONITORING_CONFIG.get(environment, MONITORING_CONFIG["development"])


# 自适应性能调优
class AdaptivePerformanceManager:
    """自适应性能管理器"""
    
    def __init__(self):
        self.current_mode = "basic"
        self.performance_history = []
        self.adjustment_threshold = 0.1  # 10%性能变化阈值
    
    def record_performance(self, response_time: float, memory_usage: float, cpu_usage: float):
        """记录性能指标"""
        self.performance_history.append({
            "response_time": response_time,
            "memory_usage": memory_usage,
            "cpu_usage": cpu_usage
        })
        
        # 保持最近100条记录
        if len(self.performance_history) > 100:
            self.performance_history.pop(0)
    
    def suggest_optimization(self) -> Dict[str, Any]:
        """建议性能优化"""
        if len(self.performance_history) < 10:
            return {"suggestion": "需要更多性能数据"}
        
        recent_metrics = self.performance_history[-10:]
        avg_response_time = sum(m["response_time"] for m in recent_metrics) / len(recent_metrics)
        avg_memory_usage = sum(m["memory_usage"] for m in recent_metrics) / len(recent_metrics)
        avg_cpu_usage = sum(m["cpu_usage"] for m in recent_metrics) / len(recent_metrics)
        
        suggestions = []
        
        if avg_response_time > 30:  # 响应时间超过30秒
            suggestions.append("考虑使用fast模式或减少top_k参数")
        
        if avg_memory_usage > 0.8:  # 内存使用超过80%
            suggestions.append("考虑使用memory_optimized配置")
        
        if avg_cpu_usage > 0.8:  # CPU使用超过80%
            suggestions.append("考虑减少并发处理数量")
        
        return {
            "current_performance": {
                "avg_response_time": avg_response_time,
                "avg_memory_usage": avg_memory_usage,
                "avg_cpu_usage": avg_cpu_usage
            },
            "suggestions": suggestions
        }


# 导出配置
__all__ = [
    "PerformanceConfig",
    "get_optimized_query_params",
    "get_batch_config",
    "get_cache_config",
    "get_monitoring_config",
    "AdaptivePerformanceManager",
    "QUERY_OPTIMIZATION",
    "BATCH_PROCESSING_CONFIG",
    "CACHE_CONFIG",
    "MONITORING_CONFIG"
]
