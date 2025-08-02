"""
知识库管理器
"""
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from .config import settings
from .guixiaoxirag_service import GuiXiaoXiRagService


class KnowledgeBaseManager:
    """知识库管理器"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or "./knowledgeBase"
        self.logger = logging.getLogger(__name__)
        self.current_kb = "default"
        self._ensure_base_dir()
    
    def _ensure_base_dir(self):
        """确保基础目录存在"""
        os.makedirs(self.base_dir, exist_ok=True)
        
        # 创建默认知识库
        default_path = os.path.join(self.base_dir, "default")
        os.makedirs(default_path, exist_ok=True)
    
    def list_knowledge_bases(self) -> List[Dict[str, Any]]:
        """列出所有知识库"""
        knowledge_bases = []
        
        for item in os.listdir(self.base_dir):
            kb_path = os.path.join(self.base_dir, item)
            if os.path.isdir(kb_path):
                info = self._get_kb_info(item, kb_path)
                knowledge_bases.append(info)
        
        return knowledge_bases
    
    def _get_kb_info(self, name: str, path: str) -> Dict[str, Any]:
        """获取知识库信息"""
        try:
            # 获取创建时间
            created_at = datetime.fromtimestamp(os.path.getctime(path)).isoformat()
            
            # 计算大小
            size_mb = self._calculate_dir_size(path) / (1024 * 1024)
            
            # 统计文档数量
            doc_count = self._count_documents(path)
            
            # 统计图谱节点和边数量
            node_count, edge_count = self._count_graph_elements(path)
            
            return {
                "name": name,
                "path": path,
                "created_at": created_at,
                "document_count": doc_count,
                "node_count": node_count,
                "edge_count": edge_count,
                "size_mb": round(size_mb, 2)
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
                "size_mb": 0.0
            }
    
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
    
    def create_knowledge_base(self, name: str, description: str = None) -> Dict[str, Any]:
        """创建新的知识库"""
        if not name or not name.strip():
            raise ValueError("知识库名称不能为空")
        
        # 检查名称是否合法
        if not name.replace('_', '').replace('-', '').isalnum():
            raise ValueError("知识库名称只能包含字母、数字、下划线和连字符")
        
        kb_path = os.path.join(self.base_dir, name)
        
        if os.path.exists(kb_path):
            raise ValueError(f"知识库 '{name}' 已存在")
        
        try:
            # 创建目录
            os.makedirs(kb_path, exist_ok=True)
            
            # 创建元数据文件
            metadata = {
                "name": name,
                "description": description or "",
                "created_at": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            
            metadata_file = os.path.join(kb_path, "metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"创建知识库成功: {name}")
            return self._get_kb_info(name, kb_path)
            
        except Exception as e:
            # 清理失败的创建
            if os.path.exists(kb_path):
                shutil.rmtree(kb_path, ignore_errors=True)
            raise ValueError(f"创建知识库失败: {str(e)}")
    
    def delete_knowledge_base(self, name: str) -> bool:
        """删除知识库"""
        if name == "default":
            raise ValueError("不能删除默认知识库")
        
        kb_path = os.path.join(self.base_dir, name)
        
        if not os.path.exists(kb_path):
            raise ValueError(f"知识库 '{name}' 不存在")
        
        try:
            shutil.rmtree(kb_path)
            self.logger.info(f"删除知识库成功: {name}")
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
    
    def export_knowledge_base(self, name: str, format: str = "json") -> Dict[str, Any]:
        """导出知识库"""
        kb_path = os.path.join(self.base_dir, name)
        
        if not os.path.exists(kb_path):
            raise ValueError(f"知识库 '{name}' 不存在")
        
        try:
            export_data = {
                "metadata": self._get_kb_info(name, kb_path),
                "documents": self._export_documents(kb_path),
                "graph": self._export_graph(kb_path),
                "exported_at": datetime.now().isoformat()
            }
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"导出知识库失败 {name}: {e}")
            raise ValueError(f"导出知识库失败: {str(e)}")
    
    def _export_documents(self, kb_path: str) -> List[Dict[str, Any]]:
        """导出文档数据"""
        try:
            full_docs_file = os.path.join(kb_path, "kv_store_full_docs.json")
            if os.path.exists(full_docs_file):
                with open(full_docs_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"导出文档失败: {e}")
        return []
    
    def _export_graph(self, kb_path: str) -> Dict[str, Any]:
        """导出图谱数据"""
        try:
            graph_file = os.path.join(kb_path, "graph_chunk_entity_relation.graphml")
            if os.path.exists(graph_file):
                with open(graph_file, 'r', encoding='utf-8') as f:
                    return {"graphml": f.read()}
        except Exception as e:
            self.logger.error(f"导出图谱失败: {e}")
        return {}


# 全局知识库管理器实例
kb_manager = KnowledgeBaseManager()
