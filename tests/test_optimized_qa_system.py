"""
优化后的问答系统测试脚本
"""

import asyncio
import json
import os
import sys
import time
from typing import List, Dict, Any

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OptimizedQASystemTester:
    """优化后的问答系统测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1/qa"
        self.session = requests.Session()
        self.test_results = []
    
    def log_test_result(self, test_name: str, success: bool, message: str, data: Any = None):
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
        
        if not success and data:
            print(f"   详细信息: {data}")
    
    def test_health_check(self):
        """测试健康检查"""
        try:
            response = self.session.get(f"{self.api_base}/health")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test_result("健康检查", True, "问答系统健康状态正常")
                    print(f"   总问答对数: {data.get('data', {}).get('total_qa_pairs', 0)}")
                    print(f"   相似度阈值: 0.98")
                else:
                    self.log_test_result("健康检查", False, "问答系统状态异常", data)
            else:
                self.log_test_result("健康检查", False, f"HTTP状态码: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test_result("健康检查", False, f"请求失败: {str(e)}")
    
    def test_high_precision_query(self):
        """测试高精度查询（相似度阈值0.98）"""
        try:
            test_queries = [
                {
                    "query": "什么是GuiXiaoXiRag？",
                    "expected_found": True,
                    "description": "精确匹配系统介绍"
                },
                {
                    "query": "GuiXiaoXiRag是什么？",
                    "expected_found": True,
                    "description": "语序变化的相似查询"
                },
                {
                    "query": "如何使用问答系统？",
                    "expected_found": True,
                    "description": "使用方法查询"
                },
                {
                    "query": "问答系统怎么用？",
                    "expected_found": True,
                    "description": "口语化表达"
                },
                {
                    "query": "完全不相关的问题关于天气",
                    "expected_found": False,
                    "description": "不相关查询应该不匹配"
                }
            ]
            
            for test_case in test_queries:
                query_data = {
                    "question": test_case["query"],
                    "top_k": 3,
                    "min_similarity": 0.98
                }
                
                response = self.session.post(f"{self.api_base}/query", json=query_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        found = data.get("found", False)
                        similarity = data.get("similarity", 0.0)
                        
                        if found == test_case["expected_found"]:
                            if found:
                                if similarity >= 0.98:
                                    self.log_test_result(
                                        f"高精度查询: {test_case['description']}", 
                                        True, 
                                        f"找到匹配，相似度: {similarity:.4f}"
                                    )
                                else:
                                    self.log_test_result(
                                        f"高精度查询: {test_case['description']}", 
                                        False, 
                                        f"相似度过低: {similarity:.4f} < 0.98"
                                    )
                            else:
                                self.log_test_result(
                                    f"高精度查询: {test_case['description']}", 
                                    True, 
                                    "正确识别为不匹配"
                                )
                        else:
                            self.log_test_result(
                                f"高精度查询: {test_case['description']}", 
                                False, 
                                f"期望 {test_case['expected_found']}，实际 {found}"
                            )
                    else:
                        self.log_test_result(
                            f"高精度查询: {test_case['description']}", 
                            False, 
                            "查询失败", 
                            data
                        )
                else:
                    self.log_test_result(
                        f"高精度查询: {test_case['description']}", 
                        False, 
                        f"HTTP状态码: {response.status_code}"
                    )
                    
        except Exception as e:
            self.log_test_result("高精度查询测试", False, f"请求失败: {str(e)}")
    
    def test_create_and_query_qa_pair(self):
        """测试创建和查询问答对"""
        try:
            # 创建一个新的问答对
            qa_data = {
                "question": "测试问题：向量化存储的优势是什么？",
                "answer": "向量化存储的优势包括：1) 高效的语义搜索；2) 支持模糊匹配；3) 可以处理同义词和近义词；4) 快速的相似度计算；5) 适合大规模数据检索。",
                "category": "test",
                "confidence": 0.95,
                "keywords": ["向量化", "存储", "优势", "语义搜索"],
                "source": "test_script"
            }
            
            response = self.session.post(f"{self.api_base}/pairs", json=qa_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    qa_id = data.get("data", {}).get("qa_id")
                    self.log_test_result("创建问答对", True, f"问答对创建成功，ID: {qa_id}")
                    
                    # 等待一下让向量化完成
                    time.sleep(2)
                    
                    # 测试查询刚创建的问答对
                    query_data = {
                        "question": "向量化存储有什么优势？",
                        "top_k": 1
                    }
                    
                    query_response = self.session.post(f"{self.api_base}/query", json=query_data)
                    
                    if query_response.status_code == 200:
                        query_result = query_response.json()
                        if query_result.get("success") and query_result.get("found"):
                            similarity = query_result.get("similarity", 0.0)
                            if similarity >= 0.98:
                                self.log_test_result(
                                    "查询新创建的问答对", 
                                    True, 
                                    f"成功找到匹配，相似度: {similarity:.4f}"
                                )
                            else:
                                self.log_test_result(
                                    "查询新创建的问答对", 
                                    False, 
                                    f"相似度过低: {similarity:.4f}"
                                )
                        else:
                            self.log_test_result(
                                "查询新创建的问答对", 
                                False, 
                                "未找到匹配的问答对"
                            )
                    else:
                        self.log_test_result(
                            "查询新创建的问答对", 
                            False, 
                            f"查询请求失败: {query_response.status_code}"
                        )
                else:
                    self.log_test_result("创建问答对", False, "问答对创建失败", data)
            else:
                self.log_test_result("创建问答对", False, f"HTTP状态码: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test_result("创建和查询问答对", False, f"请求失败: {str(e)}")
    
    def test_batch_query(self):
        """测试批量查询"""
        try:
            queries = [
                "什么是GuiXiaoXiRag？",
                "如何使用问答系统？",
                "问答系统支持哪些功能？"
            ]
            
            batch_data = {
                "questions": queries,
                "top_k": 1,
                "parallel": True,
                "timeout": 60
            }
            
            response = self.session.post(f"{self.api_base}/query/batch", json=batch_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    total_queries = data.get("total_queries", 0)
                    successful_queries = data.get("successful_queries", 0)
                    total_time = data.get("total_time", 0)
                    
                    # 检查高精度匹配
                    results = data.get("results", [])
                    high_precision_matches = 0
                    for result in results:
                        if result.get("found") and result.get("similarity", 0) >= 0.98:
                            high_precision_matches += 1
                    
                    self.log_test_result(
                        "批量查询", 
                        True, 
                        f"批量查询完成: {successful_queries}/{total_queries} 成功，{high_precision_matches} 个高精度匹配，耗时 {total_time:.2f}秒"
                    )
                else:
                    self.log_test_result("批量查询", False, "批量查询失败", data)
            else:
                self.log_test_result("批量查询", False, f"HTTP状态码: {response.status_code}")
                
        except Exception as e:
            self.log_test_result("批量查询", False, f"请求失败: {str(e)}")
    
    def test_statistics(self):
        """测试获取统计信息"""
        try:
            response = self.session.get(f"{self.api_base}/statistics")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    stats = data.get("data", {}).get("storage_stats", {})
                    total_pairs = stats.get("total_pairs", 0)
                    similarity_threshold = stats.get("similarity_threshold", 0)
                    categories = stats.get("categories", {})
                    
                    self.log_test_result(
                        "获取统计信息", 
                        True, 
                        f"统计信息获取成功，总问答对: {total_pairs}，相似度阈值: {similarity_threshold}，分类: {len(categories)}"
                    )
                    
                    # 验证相似度阈值是否为0.98
                    if similarity_threshold == 0.98:
                        self.log_test_result("相似度阈值验证", True, "相似度阈值正确设置为0.98")
                    else:
                        self.log_test_result("相似度阈值验证", False, f"相似度阈值错误: {similarity_threshold}")
                else:
                    self.log_test_result("获取统计信息", False, "获取失败", data)
            else:
                self.log_test_result("获取统计信息", False, f"HTTP状态码: {response.status_code}")
                
        except Exception as e:
            self.log_test_result("获取统计信息", False, f"请求失败: {str(e)}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始运行优化后的问答系统测试...")
        print("=" * 60)
        print("测试重点：0.98相似度阈值的高精度匹配")
        print("=" * 60)
        
        # 基础功能测试
        self.test_health_check()
        
        # 高精度查询测试
        self.test_high_precision_query()
        
        # 创建和查询测试
        self.test_create_and_query_qa_pair()
        
        # 批量查询测试
        self.test_batch_query()
        
        # 统计信息测试
        self.test_statistics()
        
        # 输出测试结果汇总
        self.print_test_summary()
    
    def print_test_summary(self):
        """输出测试结果汇总"""
        print("\n" + "=" * 60)
        print("测试结果汇总")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - successful_tests
        
        print(f"总测试数: {total_tests}")
        print(f"成功: {successful_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {(successful_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test_name']}: {result['message']}")
        
        print("\n测试完成！")
        print("注意：系统使用0.98的高相似度阈值，确保精确匹配")


def main():
    """主函数"""
    print("GuiXiaoXiRag 优化问答系统测试")
    print("相似度阈值: 0.98 (高精度匹配)")
    print("请确保服务已启动在 http://localhost:8002")
    print()
    
    # 等待用户确认
    input("按回车键开始测试...")
    
    # 创建测试器并运行测试
    tester = OptimizedQASystemTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
