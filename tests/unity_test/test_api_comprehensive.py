#!/usr/bin/env python3
"""
GuiXiaoXiRag API 综合测试脚本
测试所有主要API端点的功能
"""
import asyncio
import json
import time
import requests
from typing import Dict, Any, List

# 服务配置
BASE_URL = "http://localhost:8002"
API_BASE = f"{BASE_URL}/api/v1"

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str, data: Any = None):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": time.time(),
            "data": data
        }
        self.test_results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        
    def test_health_check(self):
        """测试健康检查"""
        try:
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("健康检查", True, "服务健康状态正常", data)
                return True
            else:
                self.log_test("健康检查", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("健康检查", False, f"请求失败: {str(e)}")
            return False
    
    def test_root_endpoint(self):
        """测试根端点"""
        try:
            response = self.session.get(BASE_URL)
            if response.status_code == 200:
                data = response.json()
                self.log_test("根端点", True, "根端点响应正常", data)
                return True
            else:
                self.log_test("根端点", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("根端点", False, f"请求失败: {str(e)}")
            return False
    
    def test_query_api(self):
        """测试查询API"""
        test_queries = [
            {"query": "什么是人工智能？", "mode": "hybrid"},
            {"query": "机器学习的基本概念", "mode": "local"},
            {"query": "深度学习算法", "mode": "global"},
            {"query": "神经网络", "mode": "naive"}
        ]
        
        success_count = 0
        for i, query_data in enumerate(test_queries):
            try:
                response = self.session.post(
                    f"{API_BASE}/query",
                    json=query_data,
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_test(f"查询API-{i+1}", True, f"查询成功: {query_data['query'][:20]}...")
                        success_count += 1
                    else:
                        self.log_test(f"查询API-{i+1}", False, f"查询失败: {data.get('message')}")
                else:
                    self.log_test(f"查询API-{i+1}", False, f"状态码: {response.status_code}")
            except Exception as e:
                self.log_test(f"查询API-{i+1}", False, f"请求失败: {str(e)}")
        
        return success_count == len(test_queries)
    
    def test_knowledge_base_api(self):
        """测试知识库管理API"""
        try:
            # 获取知识库列表
            response = self.session.get(f"{API_BASE}/knowledge-bases")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    kb_count = len(data.get("data", {}).get("knowledge_bases", []))
                    self.log_test("知识库列表", True, f"获取到 {kb_count} 个知识库")
                    return True
                else:
                    self.log_test("知识库列表", False, f"获取失败: {data.get('message')}")
                    return False
            else:
                self.log_test("知识库列表", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("知识库列表", False, f"请求失败: {str(e)}")
            return False
    
    def test_knowledge_graph_api(self):
        """测试知识图谱API"""
        try:
            # 获取知识图谱统计
            response = self.session.get(f"{API_BASE}/knowledge-graph/stats")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    stats = data.get("data", {})
                    node_count = stats.get("node_count", 0)
                    edge_count = stats.get("edge_count", 0)
                    self.log_test("知识图谱统计", True, f"节点: {node_count}, 边: {edge_count}")
                    return True
                else:
                    self.log_test("知识图谱统计", False, f"获取失败: {data.get('message')}")
                    return False
            else:
                self.log_test("知识图谱统计", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("知识图谱统计", False, f"请求失败: {str(e)}")
            return False
    
    def test_system_api(self):
        """测试系统管理API"""
        try:
            # 获取系统状态
            response = self.session.get(f"{API_BASE}/system/status")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("系统状态", True, "系统状态获取成功")
                    return True
                else:
                    self.log_test("系统状态", False, f"获取失败: {data.get('message')}")
                    return False
            else:
                self.log_test("系统状态", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("系统状态", False, f"请求失败: {str(e)}")
            return False
    
    def test_query_modes(self):
        """测试所有查询模式"""
        modes = ["local", "global", "hybrid", "naive", "mix", "bypass"]
        success_count = 0
        
        for mode in modes:
            try:
                response = self.session.post(
                    f"{API_BASE}/query",
                    json={"query": "测试查询", "mode": mode},
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_test(f"查询模式-{mode}", True, f"{mode}模式查询成功")
                        success_count += 1
                    else:
                        self.log_test(f"查询模式-{mode}", False, f"查询失败: {data.get('message')}")
                else:
                    self.log_test(f"查询模式-{mode}", False, f"状态码: {response.status_code}")
            except Exception as e:
                self.log_test(f"查询模式-{mode}", False, f"请求失败: {str(e)}")
        
        return success_count == len(modes)
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始GuiXiaoXiRag API综合测试")
        print("=" * 50)
        
        # 基础测试
        self.test_root_endpoint()
        self.test_health_check()
        
        # 核心功能测试
        self.test_query_api()
        self.test_query_modes()
        self.test_knowledge_base_api()
        self.test_knowledge_graph_api()
        self.test_system_api()
        
        # 统计结果
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        
        print("\n" + "=" * 50)
        print(f"📊 测试完成: {successful_tests}/{total_tests} 通过")
        print(f"成功率: {successful_tests/total_tests*100:.1f}%")
        
        # 保存测试结果
        with open("test_results.json", "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        return successful_tests == total_tests


if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
