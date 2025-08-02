#!/usr/bin/env python3
"""
GuiXiaoXiRag FastAPI 客户端工具
提供简单易用的API调用接口
"""
import asyncio
import httpx
import json
import time
from typing import Optional, List, Dict, Any
from pathlib import Path


class GuiXiaoXiRagClient:
    """GuiXiaoXiRag API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8002", timeout: int = 120):
        self.base_url = base_url
        self.timeout = timeout
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[Any, Any]]:
        """通用请求方法"""
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            try:
                response = await client.request(method, endpoint, **kwargs)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"❌ 请求失败: {response.status_code} - {response.text}")
                    return None
                    
            except Exception as e:
                print(f"❌ 请求异常: {str(e)}")
                return None
    
    # 系统管理方法
    async def health_check(self) -> bool:
        """健康检查"""
        result = await self._request("GET", "/health")
        if result:
            print(f"✅ 服务健康: {result.get('system', {}).get('status', 'unknown')}")
            return True
        return False
    
    async def get_system_status(self) -> Optional[Dict]:
        """获取系统状态"""
        result = await self._request("GET", "/system/status")
        if result and result.get("success"):
            return result["data"]
        return None
    
    # 文档管理方法
    async def insert_text(self, text: str, doc_id: str = None, knowledge_base: str = None, language: str = None, **kwargs) -> Optional[str]:
        """插入文本到指定知识库"""
        data = {"text": text, **kwargs}
        if doc_id:
            data["doc_id"] = doc_id
        if knowledge_base:
            data["knowledge_base"] = knowledge_base
        if language:
            data["language"] = language

        result = await self._request("POST", "/insert/text", json=data)
        if result and result.get("success"):
            track_id = result["data"]["track_id"]
            message = result["data"].get("message", "插入成功")
            print(f"✅ {message}")
            print(f"📋 跟踪ID: {track_id}")
            return track_id
        return None
    
    async def insert_texts(self, texts: List[str], doc_ids: List[str] = None, knowledge_base: str = None, language: str = None, **kwargs) -> Optional[str]:
        """批量插入文本到指定知识库"""
        data = {"texts": texts, **kwargs}
        if doc_ids:
            data["doc_ids"] = doc_ids
        if knowledge_base:
            data["knowledge_base"] = knowledge_base
        if language:
            data["language"] = language

        result = await self._request("POST", "/insert/texts", json=data)
        if result and result.get("success"):
            track_id = result["data"]["track_id"]
            message = result["data"].get("message", "批量插入成功")
            print(f"✅ {message}")
            print(f"📋 跟踪ID: {track_id}")
            return track_id
        return None
    
    async def upload_file(self, file_path: str) -> Optional[str]:
        """上传文件"""
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"❌ 文件不存在: {file_path}")
            return None
        
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            try:
                with open(file_path, "rb") as f:
                    files = {"file": (file_path.name, f, "text/plain")}
                    response = await client.post("/insert/file", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    track_id = result["data"]["track_id"]
                    print(f"✅ 文件上传成功: {file_path.name} -> {track_id}")
                    return track_id
                else:
                    print(f"❌ 文件上传失败: {response.status_code}")
                    return None
                    
            except Exception as e:
                print(f"❌ 文件上传异常: {str(e)}")
                return None
    
    # 查询方法
    async def query(self, query: str, mode: str = "hybrid", knowledge_base: str = None, language: str = None, **kwargs) -> Optional[str]:
        """执行查询"""
        data = {"query": query, "mode": mode, **kwargs}
        if knowledge_base:
            data["knowledge_base"] = knowledge_base
        if language:
            data["language"] = language

        result = await self._request("POST", "/query", json=data)
        if result and result.get("success"):
            answer = result["data"]["result"]
            kb = result["data"].get("knowledge_base", "default")
            lang = result["data"].get("language", "中文")
            print(f"✅ 查询成功")
            print(f"📁 知识库: {kb}")
            print(f"🌍 语言: {lang}")
            print(f"🔍 模式: {mode}")
            return answer
        return None
    
    async def optimized_query(self, query: str, mode: str = "hybrid", performance_level: str = "balanced") -> Optional[str]:
        """优化查询"""
        data = {
            "query": query,
            "mode": mode,
            "performance_level": performance_level
        }
        
        result = await self._request("POST", "/query/optimized", json=data)
        if result and result.get("success"):
            answer = result["data"]["result"]
            params = result["data"]["optimized_params"]
            print(f"✅ 优化查询成功 (级别: {performance_level})")
            print(f"📊 优化参数: {params}")
            return answer
        return None
    
    async def batch_query(self, queries: List[str], mode: str = "hybrid") -> Optional[List[Dict]]:
        """批量查询"""
        data = {"queries": queries, "mode": mode}
        
        result = await self._request("POST", "/query/batch", json=data)
        if result and result.get("success"):
            results = result["data"]["results"]
            print(f"✅ 批量查询成功: {len(results)}个结果")
            return results
        return None
    
    # 知识库管理方法
    async def list_knowledge_bases(self) -> Optional[List[Dict]]:
        """列出知识库"""
        result = await self._request("GET", "/knowledge-bases")
        if result and result.get("success"):
            kbs = result["data"]["knowledge_bases"]
            current = result["data"]["current"]
            print(f"📁 知识库列表 (当前: {current}):")
            for kb in kbs:
                print(f"  • {kb['name']}: {kb['document_count']}文档, {kb['node_count']}节点")
            return kbs
        return None
    
    async def create_knowledge_base(self, name: str, description: str = "") -> bool:
        """创建知识库"""
        data = {"name": name, "description": description}
        
        result = await self._request("POST", "/knowledge-bases", json=data)
        if result and result.get("success"):
            print(f"✅ 知识库创建成功: {name}")
            return True
        return False
    
    async def switch_knowledge_base(self, name: str) -> bool:
        """切换知识库"""
        data = {"name": name}
        
        result = await self._request("POST", "/knowledge-bases/switch", json=data)
        if result and result.get("success"):
            print(f"✅ 已切换到知识库: {name}")
            return True
        return False
    
    # 监控方法
    async def get_metrics(self) -> Optional[Dict]:
        """获取性能指标"""
        result = await self._request("GET", "/metrics")
        if result and result.get("success"):
            metrics = result["data"]
            print(f"📊 性能指标:")
            print(f"  • 总请求数: {metrics['total_requests']}")
            print(f"  • 错误数: {metrics['total_errors']}")
            print(f"  • 平均响应时间: {metrics['average_response_time']:.3f}秒")
            print(f"  • 错误率: {metrics['error_rate']:.2%}")
            return metrics
        return None
    
    async def get_knowledge_graph_stats(self) -> Optional[Dict]:
        """获取知识图谱统计"""
        result = await self._request("GET", "/knowledge-graph/stats")
        if result and result.get("success"):
            stats = result["data"]
            print(f"🕸️ 知识图谱统计:")
            print(f"  • 节点数: {stats['total_nodes']}")
            print(f"  • 边数: {stats['total_edges']}")
            return stats
        return None

    # 语言管理方法
    async def get_supported_languages(self) -> Optional[Dict]:
        """获取支持的语言列表"""
        result = await self._request("GET", "/languages")
        if result and result.get("success"):
            lang_info = result["data"]
            print(f"🌍 语言信息:")
            print(f"  • 当前语言: {lang_info['current_language']}")
            print(f"  • 支持的语言: {', '.join(lang_info['supported_languages'])}")
            return lang_info
        return None

    async def set_language(self, language: str) -> bool:
        """设置默认回答语言"""
        data = {"language": language}
        result = await self._request("POST", "/languages/set", json=data)
        if result and result.get("success"):
            print(f"✅ 语言已设置为: {language}")
            return True
        return False

    # 服务配置管理方法
    async def get_service_config(self) -> Optional[Dict]:
        """获取当前服务配置"""
        result = await self._request("GET", "/service/config")
        if result and result.get("success"):
            config = result["data"]
            print(f"⚙️ 服务配置:")
            print(f"  • 当前知识库: {config.get('knowledge_base', 'default')}")
            print(f"  • 当前语言: {config['language']}")
            print(f"  • 初始化状态: {config['initialized']}")
            print(f"  • 缓存实例数: {config['cached_instances']}")
            return config
        return None

    async def switch_knowledge_base(self, knowledge_base: str, language: str = None) -> bool:
        """切换服务使用的知识库和语言"""
        data = {"knowledge_base": knowledge_base}
        if language:
            data["language"] = language

        result = await self._request("POST", "/service/switch-kb", json=data)
        if result and result.get("success"):
            print(f"✅ 已切换到知识库: {knowledge_base}")
            if language:
                print(f"🌍 语言设置为: {language}")
            return True
        return False


# 使用示例
async def demo_usage():
    """使用示例"""
    client = GuiXiaoXiRagClient()
    
    print("🚀 GuiXiaoXiRag API客户端演示")
    print("=" * 50)
    
    # 1. 健康检查
    if not await client.health_check():
        print("❌ 服务不可用，请检查服务是否启动")
        return
    
    # 2. 查看系统状态
    status = await client.get_system_status()
    if status:
        print(f"📊 服务版本: {status['version']}")
    
    # 3. 查看知识库
    await client.list_knowledge_bases()
    
    # 4. 插入测试文档
    print(f"\n📝 插入测试文档...")
    await client.insert_text(
        text="这是一个API客户端测试文档，包含了关于GuiXiaoXiRag的基本信息。",
        doc_id="api_client_test"
    )
    
    # 5. 等待处理
    print(f"\n⏳ 等待数据处理...")
    await asyncio.sleep(5)
    
    # 6. 执行查询
    print(f"\n🔍 执行查询...")
    result = await client.query("API客户端测试文档包含什么内容？")
    if result:
        print(f"📝 查询结果: {result[:200]}...")
    
    # 7. 查看统计信息
    print(f"\n📊 查看统计信息...")
    await client.get_metrics()
    await client.get_knowledge_graph_stats()
    
    print(f"\n🎉 演示完成！")


if __name__ == "__main__":
    asyncio.run(demo_usage())
