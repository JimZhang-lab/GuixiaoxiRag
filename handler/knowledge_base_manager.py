"""
知识库管理器
优化版本 - 更好的错误处理、性能监控和配置管理
"""
import os
import json
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from common.config import settings
from common.logging_utils import logger_manager
from common.utils import format_file_size, generate_unique_id
from common.file_utils import ensure_directory


class KnowledgeBaseManager:
    """知识库管理器"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or "./knowledgeBase"
        self.logger = logger_manager.setup_knowledge_base_logger()
        self.current_kb = "default"
        self._ensure_base_dir()
        self._kb_cache = {}  # 缓存知识库信息
        self._cache_ttl = 300  # 缓存5分钟
    
    def _ensure_base_dir(self):
        """确保基础目录存在"""
        ensure_directory(self.base_dir)
        
        # 创建默认知识库
        default_path = os.path.join(self.base_dir, "default")
        ensure_directory(default_path)
        
        # 创建默认知识库的元数据（如果不存在）
        metadata_file = os.path.join(default_path, "metadata.json")
        if not os.path.exists(metadata_file):
            self._create_metadata_file(default_path, "default", "默认知识库")
    
    def _create_metadata_file(self, kb_path: str, name: str, description: str = ""):
        """创建元数据文件"""
        metadata = {
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "language": "中文",
            "status": "active",
            "tags": [],
            "config": {
                "chunk_size": 1024,
                "chunk_overlap": 50,
                "enable_auto_update": True
            }
        }
        
        metadata_file = os.path.join(kb_path, "metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def list_knowledge_bases(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """列出所有知识库"""
        cache_key = "kb_list"
        current_time = time.time()
        
        # 检查缓存
        if use_cache and cache_key in self._kb_cache:
            cache_data = self._kb_cache[cache_key]
            if current_time - cache_data["timestamp"] < self._cache_ttl:
                return cache_data["data"]
        
        knowledge_bases = []
        
        try:
            for item in os.listdir(self.base_dir):
                kb_path = os.path.join(self.base_dir, item)
                if os.path.isdir(kb_path):
                    info = self._get_kb_info(item, kb_path)
                    knowledge_bases.append(info)
            
            # 按创建时间排序
            knowledge_bases.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            # 更新缓存
            self._kb_cache[cache_key] = {
                "data": knowledge_bases,
                "timestamp": current_time
            }
            
        except Exception as e:
            self.logger.error(f"列出知识库失败: {e}")
            raise ValueError(f"列出知识库失败: {str(e)}")
        
        return knowledge_bases
    
    def _get_kb_info(self, name: str, path: str) -> Dict[str, Any]:
        """获取知识库信息"""
        try:
            # 读取元数据
            metadata = self._read_metadata(path)
            
            # 获取创建时间
            created_at = metadata.get("created_at")
            if not created_at:
                created_at = datetime.fromtimestamp(os.path.getctime(path)).isoformat()
            
            # 计算大小
            size_bytes = self._calculate_dir_size(path)
            size_mb = size_bytes / (1024 * 1024)
            
            # 统计文档数量
            doc_count = self._count_documents(path)
            
            # 统计图谱节点和边数量
            node_count, edge_count = self._count_graph_elements(path)
            
            # 获取状态
            status = self._get_kb_status(path)
            
            return {
                "name": name,
                "path": path,
                "created_at": created_at,
                "document_count": doc_count,
                "node_count": node_count,
                "edge_count": edge_count,
                "size_mb": round(size_mb, 2),
                "size_formatted": format_file_size(size_bytes),
                "description": metadata.get("description", ""),
                "language": metadata.get("language", "中文"),
                "status": status,
                "tags": metadata.get("tags", []),
                "version": metadata.get("version", "1.0.0")
            }
        except Exception as e:
            self.logger.error(f"获取知识库信息失败 {name}: {e}")
            return {
                "name": name,
                "path": path,
                "created_at": "unknown",
                "document_count": 0,
                "node_count": 0,
                "edge_count": 0,
                "size_mb": 0.0,
                "size_formatted": "0B",
                "description": "",
                "language": "中文",
                "status": "error",
                "tags": [],
                "version": "1.0.0"
            }
    
    def _read_metadata(self, kb_path: str) -> Dict[str, Any]:
        """读取知识库元数据"""
        metadata_file = os.path.join(kb_path, "metadata.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"读取元数据失败: {e}")
        return {}
    
    def _calculate_dir_size(self, path: str) -> int:
        """计算目录大小"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        except Exception as e:
            self.logger.error(f"计算目录大小失败 {path}: {e}")
        return total_size
    
    def _count_documents(self, path: str) -> int:
        """统计文档数量"""
        try:
            full_docs_file = os.path.join(path, "kv_store_full_docs.json")
            if os.path.exists(full_docs_file):
                with open(full_docs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return len(data)
        except Exception as e:
            self.logger.error(f"统计文档数量失败 {path}: {e}")
        return 0
    
    def _count_graph_elements(self, path: str) -> tuple:
        """统计图谱节点和边数量"""
        try:
            graph_file = os.path.join(path, "graph_chunk_entity_relation.graphml")
            if os.path.exists(graph_file):
                # 简单的XML解析来统计节点和边
                with open(graph_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    node_count = content.count('<node ')
                    edge_count = content.count('<edge ')
                    return node_count, edge_count
        except Exception as e:
            self.logger.error(f"统计图谱元素失败 {path}: {e}")
        return 0, 0
    
    def _get_kb_status(self, path: str) -> str:
        """获取知识库状态"""
        try:
            # 检查必要文件是否存在
            required_files = ["kv_store_full_docs.json"]
            for file_name in required_files:
                file_path = os.path.join(path, file_name)
                if not os.path.exists(file_path):
                    return "incomplete"
            
            # 检查是否有图谱文件
            graph_file = os.path.join(path, "graph_chunk_entity_relation.graphml")
            if os.path.exists(graph_file):
                return "ready"
            else:
                return "building"
                
        except Exception:
            return "error"
    
    def create_knowledge_base(
        self, 
        name: str, 
        description: str = None, 
        language: str = "中文",
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """创建新的知识库"""
        if not name or not name.strip():
            raise ValueError("知识库名称不能为空")
        
        # 检查名称是否合法
        if not name.replace('_', '').replace('-', '').isalnum():
            raise ValueError("知识库名称只能包含字母、数字、下划线和连字符")
        
        if len(name) > 50:
            raise ValueError("知识库名称不能超过50个字符")
        
        kb_path = os.path.join(self.base_dir, name)
        
        if os.path.exists(kb_path):
            raise ValueError(f"知识库 '{name}' 已存在")
        
        try:
            # 创建目录
            ensure_directory(kb_path)
            
            # 创建元数据文件
            metadata = {
                "name": name,
                "description": description or "",
                "created_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "language": language,
                "status": "active",
                "tags": [],
                "config": config or {
                    "chunk_size": 1024,
                    "chunk_overlap": 50,
                    "enable_auto_update": True
                },
                "created_by": "system",
                "id": generate_unique_id()
            }
            
            metadata_file = os.path.join(kb_path, "metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 清除缓存
            self._clear_cache()
            
            self.logger.info(f"创建知识库成功: {name}")
            return self._get_kb_info(name, kb_path)
            
        except Exception as e:
            # 清理失败的创建
            if os.path.exists(kb_path):
                shutil.rmtree(kb_path, ignore_errors=True)
            self.logger.error(f"创建知识库失败 {name}: {e}")
            raise ValueError(f"创建知识库失败: {str(e)}")
    
    def delete_knowledge_base(self, name: str, force: bool = False) -> bool:
        """删除知识库"""
        if name == "default" and not force:
            raise ValueError("不能删除默认知识库")
        
        kb_path = os.path.join(self.base_dir, name)
        
        if not os.path.exists(kb_path):
            raise ValueError(f"知识库 '{name}' 不存在")
        
        try:
            # 创建备份（可选）
            backup_path = f"{kb_path}_backup_{int(time.time())}"
            shutil.move(kb_path, backup_path)
            
            # 清除缓存
            self._clear_cache()
            
            self.logger.info(f"删除知识库成功: {name} (备份至: {backup_path})")
            return True
            
        except Exception as e:
            self.logger.error(f"删除知识库失败 {name}: {e}")
            raise ValueError(f"删除知识库失败: {str(e)}")
    
    def switch_knowledge_base(self, name: str) -> str:
        """切换当前知识库"""
        kb_path = os.path.join(self.base_dir, name)
        
        if not os.path.exists(kb_path):
            raise ValueError(f"知识库 '{name}' 不存在")
        
        self.current_kb = name
        self.logger.info(f"切换到知识库: {name}")
        return kb_path
    
    def get_current_kb_path(self) -> str:
        """获取当前知识库路径"""
        return os.path.join(self.base_dir, self.current_kb)
    
    def get_current_kb_info(self) -> Dict[str, Any]:
        """获取当前知识库信息"""
        kb_path = self.get_current_kb_path()
        return self._get_kb_info(self.current_kb, kb_path)
    
    def _clear_cache(self):
        """清除缓存"""
        self._kb_cache.clear()
        self.logger.debug("知识库缓存已清除")


# 全局知识库管理器实例
kb_manager = KnowledgeBaseManager()
