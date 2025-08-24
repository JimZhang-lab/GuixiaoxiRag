"""
QA系统并发控制管理器
基于shared_storage.py的设计，为QA系统提供专门的并发控制
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
import threading

logger = logging.getLogger(__name__)


class QAConcurrencyManager:
    """QA系统并发控制管理器"""
    
    # 类级别的锁注册表
    _category_locks: Dict[str, asyncio.Lock] = {}
    _global_locks: Dict[str, asyncio.Lock] = {}
    _lock_stats: Dict[str, Any] = {
        "category_locks_created": 0,
        "global_locks_created": 0,
        "lock_acquisitions": 0,
        "lock_releases": 0,
        "lock_timeouts": 0,
        "lock_errors": 0
    }
    _stats_lock = threading.Lock()
    
    @classmethod
    def _update_stats(cls, stat_name: str, increment: int = 1):
        """更新统计信息"""
        with cls._stats_lock:
            cls._lock_stats[stat_name] = cls._lock_stats.get(stat_name, 0) + increment
    
    @classmethod
    def get_lock_stats(cls) -> Dict[str, Any]:
        """获取锁统计信息"""
        with cls._stats_lock:
            return cls._lock_stats.copy()
    
    @classmethod
    def _get_category_lock_key(cls, category: str, operation: str) -> str:
        """生成分类锁的键"""
        return f"category:{category}:{operation}"
    
    @classmethod
    def _get_or_create_category_lock(cls, category: str, operation: str) -> asyncio.Lock:
        """获取或创建分类锁"""
        lock_key = cls._get_category_lock_key(category, operation)
        
        if lock_key not in cls._category_locks:
            cls._category_locks[lock_key] = asyncio.Lock()
            cls._update_stats("category_locks_created")
            
        return cls._category_locks[lock_key]
    
    @classmethod
    def _get_or_create_global_lock(cls, operation: str) -> asyncio.Lock:
        """获取或创建全局锁"""
        if operation not in cls._global_locks:
            cls._global_locks[operation] = asyncio.Lock()
            cls._update_stats("global_locks_created")
            
        return cls._global_locks[operation]
    
    @classmethod
    @asynccontextmanager
    async def get_category_lock(cls, category: str, operation: str, enable_logging: bool = False):
        """
        获取分类级锁
        
        Args:
            category: 分类名称
            operation: 操作类型 (create, delete, query, update)
            enable_logging: 是否启用日志
        """
        lock = cls._get_or_create_category_lock(category, operation)
        lock_key = cls._get_category_lock_key(category, operation)
        
        if enable_logging:
            logger.debug(f"QA Lock: Acquiring category lock '{lock_key}'")
        
        try:
            cls._update_stats("lock_acquisitions")
            await lock.acquire()
            
            if enable_logging:
                logger.debug(f"QA Lock: Category lock '{lock_key}' acquired")
            
            yield lock
            
        except asyncio.TimeoutError:
            cls._update_stats("lock_timeouts")
            if enable_logging:
                logger.warning(f"QA Lock: Timeout acquiring category lock '{lock_key}'")
            raise
        except Exception as e:
            cls._update_stats("lock_errors")
            if enable_logging:
                logger.error(f"QA Lock: Error with category lock '{lock_key}': {e}")
            raise
        finally:
            try:
                lock.release()
                cls._update_stats("lock_releases")
                
                if enable_logging:
                    logger.debug(f"QA Lock: Category lock '{lock_key}' released")
            except Exception as e:
                cls._update_stats("lock_errors")
                if enable_logging:
                    logger.error(f"QA Lock: Error releasing category lock '{lock_key}': {e}")
    
    @classmethod
    @asynccontextmanager
    async def get_global_qa_lock(cls, operation: str, enable_logging: bool = False):
        """
        获取全局QA锁
        
        Args:
            operation: 操作类型 (create_category, cleanup, maintenance)
            enable_logging: 是否启用日志
        """
        lock = cls._get_or_create_global_lock(operation)
        
        if enable_logging:
            logger.debug(f"QA Lock: Acquiring global lock '{operation}'")
        
        try:
            cls._update_stats("lock_acquisitions")
            await lock.acquire()
            
            if enable_logging:
                logger.debug(f"QA Lock: Global lock '{operation}' acquired")
            
            yield lock
            
        except asyncio.TimeoutError:
            cls._update_stats("lock_timeouts")
            if enable_logging:
                logger.warning(f"QA Lock: Timeout acquiring global lock '{operation}'")
            raise
        except Exception as e:
            cls._update_stats("lock_errors")
            if enable_logging:
                logger.error(f"QA Lock: Error with global lock '{operation}': {e}")
            raise
        finally:
            try:
                lock.release()
                cls._update_stats("lock_releases")
                
                if enable_logging:
                    logger.debug(f"QA Lock: Global lock '{operation}' released")
            except Exception as e:
                cls._update_stats("lock_errors")
                if enable_logging:
                    logger.error(f"QA Lock: Error releasing global lock '{operation}': {e}")
    
    @classmethod
    @asynccontextmanager
    async def get_multiple_category_locks(cls, categories: List[str], operation: str, enable_logging: bool = False):
        """
        获取多个分类的锁（按字母顺序排序以避免死锁）
        
        Args:
            categories: 分类名称列表
            operation: 操作类型
            enable_logging: 是否启用日志
        """
        # 按字母顺序排序以避免死锁
        sorted_categories = sorted(set(categories))
        locks = []
        acquired_locks = []
        
        if enable_logging:
            logger.debug(f"QA Lock: Acquiring multiple category locks for {sorted_categories} ({operation})")
        
        try:
            # 按顺序获取所有锁
            for category in sorted_categories:
                lock = cls._get_or_create_category_lock(category, operation)
                locks.append((category, lock))
            
            # 按顺序获取锁
            for category, lock in locks:
                cls._update_stats("lock_acquisitions")
                await lock.acquire()
                acquired_locks.append((category, lock))
                
                if enable_logging:
                    logger.debug(f"QA Lock: Acquired lock for category '{category}'")
            
            if enable_logging:
                logger.debug(f"QA Lock: All category locks acquired for {sorted_categories}")
            
            yield acquired_locks
            
        except Exception as e:
            cls._update_stats("lock_errors")
            if enable_logging:
                logger.error(f"QA Lock: Error acquiring multiple category locks: {e}")
            raise
        finally:
            # 按相反顺序释放锁
            for category, lock in reversed(acquired_locks):
                try:
                    lock.release()
                    cls._update_stats("lock_releases")
                    
                    if enable_logging:
                        logger.debug(f"QA Lock: Released lock for category '{category}'")
                except Exception as e:
                    cls._update_stats("lock_errors")
                    if enable_logging:
                        logger.error(f"QA Lock: Error releasing lock for category '{category}': {e}")
    
    @classmethod
    def cleanup_unused_locks(cls, max_age_seconds: float = 3600) -> int:
        """
        清理未使用的锁
        
        Args:
            max_age_seconds: 锁的最大存活时间（秒）
            
        Returns:
            清理的锁数量
        """
        cleaned_count = 0
        current_time = time.time()
        
        # 清理分类锁（简化版本，实际实现可能需要更复杂的跟踪机制）
        category_locks_to_remove = []
        for lock_key, lock in cls._category_locks.items():
            if not lock.locked():
                category_locks_to_remove.append(lock_key)
        
        for lock_key in category_locks_to_remove:
            del cls._category_locks[lock_key]
            cleaned_count += 1
        
        # 清理全局锁
        global_locks_to_remove = []
        for operation, lock in cls._global_locks.items():
            if not lock.locked():
                global_locks_to_remove.append(operation)
        
        for operation in global_locks_to_remove:
            del cls._global_locks[operation]
            cleaned_count += 1
        
        if cleaned_count > 0:
            logger.debug(f"QA Lock: Cleaned up {cleaned_count} unused locks")
        
        return cleaned_count
    
    @classmethod
    def reset_stats(cls):
        """重置统计信息"""
        with cls._stats_lock:
            cls._lock_stats = {
                "category_locks_created": 0,
                "global_locks_created": 0,
                "lock_acquisitions": 0,
                "lock_releases": 0,
                "lock_timeouts": 0,
                "lock_errors": 0
            }
    
    @classmethod
    def get_active_locks_info(cls) -> Dict[str, Any]:
        """获取活跃锁的信息"""
        return {
            "category_locks": {
                "total": len(cls._category_locks),
                "locked": sum(1 for lock in cls._category_locks.values() if lock.locked()),
                "keys": list(cls._category_locks.keys())
            },
            "global_locks": {
                "total": len(cls._global_locks),
                "locked": sum(1 for lock in cls._global_locks.values() if lock.locked()),
                "operations": list(cls._global_locks.keys())
            }
        }
