"""
Streamlit API 客户端
"""
import httpx
import asyncio
import streamlit as st
from typing import Optional, Dict, Any, List
import json

class StreamlitAPIClient:
    """Streamlit专用的API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.timeout = 120
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[Any, Any]]:
        """通用请求方法"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, url, **kwargs)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    st.error(f"请求失败: {response.status_code} - {response.text}")
                    return None
                    
        except httpx.ConnectError:
            st.error(f"连接失败: 请检查服务是否运行在 {self.base_url}")
            return None
        except httpx.TimeoutException:
            st.error("请求超时: 请稍后重试")
            return None
        except Exception as e:
            st.error(f"请求异常: {str(e)}")
            return None
    
    def request_sync(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[Any, Any]]:
        """同步请求方法（用于Streamlit）"""
        try:
            # 在Streamlit中运行异步代码
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._request(method, endpoint, **kwargs))
            loop.close()
            return result
        except Exception as e:
            st.error(f"请求执行失败: {str(e)}")
            return None
    
    # 系统管理方法
    def health_check(self) -> Optional[Dict]:
        """健康检查"""
        return self.request_sync("GET", "/health")
    
    def get_system_status(self) -> Optional[Dict]:
        """获取系统状态"""
        result = self.request_sync("GET", "/system/status")
        return result.get("data") if result and result.get("success") else None
    
    def reset_system(self) -> bool:
        """重置系统"""
        result = self.request_sync("POST", "/system/reset")
        return result and result.get("success", False)
    
    # 文档管理方法
    def insert_text(self, text: str, doc_id: str = None, knowledge_base: str = None, 
                   language: str = None, **kwargs) -> Optional[str]:
        """插入文本"""
        data = {"text": text, **kwargs}
        if doc_id:
            data["doc_id"] = doc_id
        if knowledge_base:
            data["knowledge_base"] = knowledge_base
        if language:
            data["language"] = language
        
        result = self.request_sync("POST", "/insert/text", json=data)
        if result and result.get("success"):
            return result["data"]["track_id"]
        return None
    
    def insert_texts(self, texts: List[str], doc_ids: List[str] = None, 
                    knowledge_base: str = None, language: str = None, **kwargs) -> Optional[str]:
        """批量插入文本"""
        data = {"texts": texts, **kwargs}
        if doc_ids:
            data["doc_ids"] = doc_ids
        if knowledge_base:
            data["knowledge_base"] = knowledge_base
        if language:
            data["language"] = language
        
        result = self.request_sync("POST", "/insert/texts", json=data)
        if result and result.get("success"):
            return result["data"]["track_id"]
        return None
    
    def upload_file(self, file_content: bytes, filename: str) -> Optional[str]:
        """上传文件"""
        files = {"file": (filename, file_content, "text/plain")}
        result = self.request_sync("POST", "/insert/file", files=files)
        if result and result.get("success"):
            return result["data"]["track_id"]
        return None
    
    def insert_directory(self, directory_path: str, knowledge_base: str = None, 
                        language: str = None) -> Optional[Dict]:
        """插入目录文件"""
        data = {"directory_path": directory_path}
        if knowledge_base:
            data["knowledge_base"] = knowledge_base
        if language:
            data["language"] = language
        
        result = self.request_sync("POST", "/insert/directory", json=data)
        return result.get("data") if result and result.get("success") else None
    
    # 查询方法
    def query(self, query: str, mode: str = "hybrid", top_k: int = 20, 
             knowledge_base: str = None, language: str = None, **kwargs) -> Optional[Dict]:
        """执行查询"""
        data = {"query": query, "mode": mode, "top_k": top_k, **kwargs}
        if knowledge_base:
            data["knowledge_base"] = knowledge_base
        if language:
            data["language"] = language
        
        result = self.request_sync("POST", "/query", json=data)
        return result.get("data") if result and result.get("success") else None
    
    def get_query_modes(self) -> Optional[Dict]:
        """获取查询模式"""
        result = self.request_sync("GET", "/query/modes")
        return result.get("data") if result and result.get("success") else None
    
    def batch_query(self, queries: List[str], mode: str = "hybrid", 
                   knowledge_base: str = None, language: str = None) -> Optional[List[Dict]]:
        """批量查询"""
        data = {"queries": queries, "mode": mode}
        if knowledge_base:
            data["knowledge_base"] = knowledge_base
        if language:
            data["language"] = language
        
        result = self.request_sync("POST", "/query/batch", json=data)
        return result.get("data", {}).get("results") if result and result.get("success") else None
    
    def optimized_query(self, query: str, mode: str = "hybrid", 
                       performance_level: str = "balanced") -> Optional[Dict]:
        """优化查询"""
        data = {
            "query": query,
            "mode": mode,
            "performance_level": performance_level
        }
        
        result = self.request_sync("POST", "/query/optimized", json=data)
        return result.get("data") if result and result.get("success") else None
    
    # 知识库管理方法
    def list_knowledge_bases(self) -> Optional[List[Dict]]:
        """列出知识库"""
        result = self.request_sync("GET", "/knowledge-bases")
        return result.get("data", {}).get("knowledge_bases") if result and result.get("success") else None
    
    def create_knowledge_base(self, name: str, description: str = "") -> bool:
        """创建知识库"""
        data = {"name": name, "description": description}
        result = self.request_sync("POST", "/knowledge-bases", json=data)
        return result and result.get("success", False)
    
    def delete_knowledge_base(self, name: str) -> bool:
        """删除知识库"""
        result = self.request_sync("DELETE", f"/knowledge-bases/{name}")
        return result and result.get("success", False)
    
    def switch_knowledge_base(self, name: str) -> bool:
        """切换知识库"""
        data = {"name": name}
        result = self.request_sync("POST", "/knowledge-bases/switch", json=data)
        return result and result.get("success", False)
    
    def export_knowledge_base(self, name: str) -> Optional[Dict]:
        """导出知识库"""
        result = self.request_sync("GET", f"/knowledge-bases/{name}/export")
        return result.get("data") if result and result.get("success") else None
    
    # 知识图谱方法
    def get_knowledge_graph(self, node_label: str, max_depth: int = 3,
                           max_nodes: int = 100) -> Optional[Dict]:
        """获取知识图谱"""
        data = {
            "node_label": node_label,
            "max_depth": max_depth,
            "max_nodes": max_nodes
        }
        result = self.request_sync("POST", "/knowledge-graph", json=data)
        return result.get("data") if result and result.get("success") else None

    # 知识图谱可视化方法
    def get_graph_status(self, knowledge_base: Optional[str] = None) -> Optional[Dict]:
        """获取知识图谱文件状态"""
        params = {}
        if knowledge_base:
            params["knowledge_base"] = knowledge_base
        result = self.request_sync("GET", "/knowledge-graph/status", params=params)
        return result.get("data") if result and result.get("success") else None

    def convert_graph_to_json(self, knowledge_base: Optional[str] = None) -> Optional[Dict]:
        """转换GraphML到JSON"""
        params = {}
        if knowledge_base:
            params["knowledge_base"] = knowledge_base
        result = self.request_sync("POST", "/knowledge-graph/convert", params=params)
        return result.get("data") if result and result.get("success") else None

    def get_graph_data(self, knowledge_base: Optional[str] = None,
                      format: str = "json") -> Optional[Dict]:
        """获取图谱数据"""
        data = {
            "knowledge_base": knowledge_base,
            "format": format
        }
        result = self.request_sync("POST", "/knowledge-graph/data", json=data)
        return result.get("data") if result and result.get("success") else None

    def visualize_knowledge_graph(self, knowledge_base: Optional[str] = None,
                                 max_nodes: int = 100, layout: str = "spring",
                                 node_size_field: str = "degree",
                                 edge_width_field: str = "weight") -> Optional[Dict]:
        """生成知识图谱可视化"""
        data = {
            "knowledge_base": knowledge_base,
            "max_nodes": max_nodes,
            "layout": layout,
            "node_size_field": node_size_field,
            "edge_width_field": edge_width_field
        }
        result = self.request_sync("POST", "/knowledge-graph/visualize", json=data)
        return result.get("data") if result and result.get("success") else None

    def list_graph_files(self, knowledge_base: Optional[str] = None) -> Optional[Dict]:
        """列出知识库中的图谱文件"""
        params = {}
        if knowledge_base:
            params["knowledge_base"] = knowledge_base
        result = self.request_sync("GET", "/knowledge-graph/files", params=params)
        return result.get("data") if result and result.get("success") else None
    
    def get_knowledge_graph_stats(self) -> Optional[Dict]:
        """获取知识图谱统计"""
        result = self.request_sync("GET", "/knowledge-graph/stats")
        return result.get("data") if result and result.get("success") else None
    
    def clear_knowledge_graph(self) -> bool:
        """清空知识图谱"""
        result = self.request_sync("DELETE", "/knowledge-graph/clear")
        return result and result.get("success", False)
    
    # 语言管理方法
    def get_supported_languages(self) -> Optional[Dict]:
        """获取支持的语言"""
        result = self.request_sync("GET", "/languages")
        return result.get("data") if result and result.get("success") else None
    
    def set_language(self, language: str) -> bool:
        """设置语言"""
        data = {"language": language}
        result = self.request_sync("POST", "/languages/set", json=data)
        return result and result.get("success", False)
    
    # 服务配置方法
    def get_service_config(self) -> Optional[Dict]:
        """获取服务配置"""
        result = self.request_sync("GET", "/service/config")
        return result.get("data") if result and result.get("success") else None
    
    def switch_service_kb(self, knowledge_base: str, language: str = None) -> bool:
        """切换服务知识库"""
        data = {"knowledge_base": knowledge_base}
        if language:
            data["language"] = language
        result = self.request_sync("POST", "/service/switch-kb", json=data)
        return result and result.get("success", False)
    
    # 性能配置方法
    def get_performance_configs(self) -> Optional[Dict]:
        """获取性能配置"""
        result = self.request_sync("GET", "/performance/configs")
        return result.get("data") if result and result.get("success") else None
    
    def optimize_performance(self, mode: str = "basic") -> bool:
        """应用性能优化"""
        result = self.request_sync("POST", f"/performance/optimize?mode={mode}")
        return result and result.get("success", False)
    
    # 监控方法
    def get_metrics(self) -> Optional[Dict]:
        """获取性能指标"""
        result = self.request_sync("GET", "/metrics")
        return result.get("data") if result and result.get("success") else None
    
    def get_logs(self, lines: int = 100) -> Optional[List[str]]:
        """获取系统日志"""
        result = self.request_sync("GET", f"/logs?lines={lines}")
        return result.get("data", {}).get("logs") if result and result.get("success") else None

    # 配置管理方法
    def get_effective_config(self) -> Optional[Dict]:
        """获取有效配置"""
        result = self.request_sync("GET", "/service/effective-config")
        return result.get("data") if result and result.get("success") else None

    def update_config(self, config_updates: Dict[str, Any]) -> Optional[Dict]:
        """更新配置"""
        result = self.request_sync("POST", "/service/config/update", json=config_updates)
        return result.get("data") if result and result.get("success") else None

    # 缓存管理方法
    def get_cache_stats(self) -> Optional[Dict]:
        """获取缓存统计信息"""
        result = self.request_sync("GET", "/cache/stats")
        return result.get("data") if result and result.get("success") else None

    def clear_all_cache(self) -> Optional[Dict]:
        """清理所有缓存"""
        result = self.request_sync("DELETE", "/cache/clear")
        return result.get("data") if result and result.get("success") else None

    def clear_specific_cache(self, cache_type: str) -> Optional[Dict]:
        """清理指定类型的缓存"""
        result = self.request_sync("DELETE", f"/cache/clear/{cache_type}")
        return result.get("data") if result and result.get("success") else None

    # 文件上传方法（支持知识库参数）
    def upload_file_with_kb(self, file_content: bytes, filename: str,
                           knowledge_base: Optional[str] = None,
                           language: Optional[str] = None,
                           track_id: Optional[str] = None) -> Optional[Dict]:
        """上传文件到指定知识库"""
        files = {"file": (filename, file_content)}
        data = {}
        if knowledge_base:
            data["knowledge_base"] = knowledge_base
        if language:
            data["language"] = language
        if track_id:
            data["track_id"] = track_id

        result = self.request_sync("POST", "/insert/file", files=files, data=data)
        return result.get("data") if result and result.get("success") else None
