"""
问答系统测试脚本
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


class QASystemTester:
    """问答系统测试器"""
    
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
                else:
                    self.log_test_result("健康检查", False, "问答系统状态异常", data)
            else:
                self.log_test_result("健康检查", False, f"HTTP状态码: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test_result("健康检查", False, f"请求失败: {str(e)}")
    
    def test_create_qa_pair(self):
        """测试创建问答对"""
        try:
            qa_data = {
                "question": "测试问题：什么是人工智能？",
                "answer": "人工智能（AI）是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统。",
                "category": "test",
                "confidence": 0.95,
                "keywords": ["人工智能", "AI", "测试"],
                "source": "test_script"
            }
            
            response = self.session.post(f"{self.api_base}/pairs", json=qa_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    qa_id = data.get("data", {}).get("qa_id")
                    self.log_test_result("创建问答对", True, f"问答对创建成功，ID: {qa_id}")
                    return qa_id
                else:
                    self.log_test_result("创建问答对", False, "问答对创建失败", data)
            else:
                self.log_test_result("创建问答对", False, f"HTTP状态码: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test_result("创建问答对", False, f"请求失败: {str(e)}")
        
        return None
    
    def test_batch_create_qa_pairs(self):
        """测试批量创建问答对"""
        try:
            qa_pairs = [
                {
                    "question": "什么是机器学习？",
                    "answer": "机器学习是人工智能的一个子集，它使计算机能够在没有明确编程的情况下学习和改进。",
                    "category": "test",
                    "confidence": 0.9,
                    "keywords": ["机器学习", "ML"],
                    "source": "test_batch"
                },
                {
                    "question": "什么是深度学习？",
                    "answer": "深度学习是机器学习的一个分支，使用神经网络来模拟人脑的学习过程。",
                    "category": "test",
                    "confidence": 0.9,
                    "keywords": ["深度学习", "神经网络"],
                    "source": "test_batch"
                }
            ]
            
            batch_data = {"qa_pairs": qa_pairs}
            response = self.session.post(f"{self.api_base}/pairs/batch", json=batch_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    added_count = data.get("data", {}).get("added_count", 0)
                    self.log_test_result("批量创建问答对", True, f"批量创建成功，添加了 {added_count} 个问答对")
                else:
                    self.log_test_result("批量创建问答对", False, "批量创建失败", data)
            else:
                self.log_test_result("批量创建问答对", False, f"HTTP状态码: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test_result("批量创建问答对", False, f"请求失败: {str(e)}")
    
    def test_query_qa(self):
        """测试问答查询"""
        try:
            test_queries = [
                "什么是人工智能？",
                "机器学习是什么？",
                "深度学习的概念",
                "AI的定义"
            ]
            
            for query in test_queries:
                query_data = {
                    "question": query,
                    "top_k": 3,
                    "min_similarity": 0.7
                }
                
                response = self.session.post(f"{self.api_base}/query", json=query_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        if data.get("found"):
                            similarity = data.get("similarity", 0)
                            answer = data.get("answer", "")[:100] + "..."
                            self.log_test_result(f"查询: {query}", True, 
                                               f"找到答案，相似度: {similarity:.3f}, 答案: {answer}")
                        else:
                            self.log_test_result(f"查询: {query}", True, "未找到匹配的答案")
                    else:
                        self.log_test_result(f"查询: {query}", False, "查询失败", data)
                else:
                    self.log_test_result(f"查询: {query}", False, f"HTTP状态码: {response.status_code}")
                    
        except Exception as e:
            self.log_test_result("问答查询", False, f"请求失败: {str(e)}")
    
    def test_batch_query(self):
        """测试批量查询"""
        try:
            queries = [
                "什么是AI？",
                "机器学习的应用",
                "深度学习算法"
            ]
            
            batch_data = {
                "questions": queries,
                "top_k": 2,
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
                    
                    self.log_test_result("批量查询", True, 
                                       f"批量查询完成: {successful_queries}/{total_queries} 成功，耗时 {total_time:.2f}秒")
                else:
                    self.log_test_result("批量查询", False, "批量查询失败", data)
            else:
                self.log_test_result("批量查询", False, f"HTTP状态码: {response.status_code}")
                
        except Exception as e:
            self.log_test_result("批量查询", False, f"请求失败: {str(e)}")
    
    def test_list_qa_pairs(self):
        """测试获取问答对列表"""
        try:
            params = {
                "page": 1,
                "page_size": 10,
                "category": "test"
            }
            
            response = self.session.get(f"{self.api_base}/pairs", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    list_data = data.get("data", {})
                    total = list_data.get("total", 0)
                    qa_pairs = list_data.get("qa_pairs", [])
                    
                    self.log_test_result("获取问答对列表", True, f"获取成功，共 {total} 条记录，当前页 {len(qa_pairs)} 条")
                else:
                    self.log_test_result("获取问答对列表", False, "获取失败", data)
            else:
                self.log_test_result("获取问答对列表", False, f"HTTP状态码: {response.status_code}")
                
        except Exception as e:
            self.log_test_result("获取问答对列表", False, f"请求失败: {str(e)}")
    
    def test_statistics(self):
        """测试获取统计信息"""
        try:
            response = self.session.get(f"{self.api_base}/statistics")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    stats = data.get("data", {})
                    total_pairs = stats.get("total_pairs", 0)
                    categories = stats.get("categories", {})
                    
                    self.log_test_result("获取统计信息", True, 
                                       f"统计信息获取成功，总问答对: {total_pairs}，分类: {len(categories)}")
                else:
                    self.log_test_result("获取统计信息", False, "获取失败", data)
            else:
                self.log_test_result("获取统计信息", False, f"HTTP状态码: {response.status_code}")
                
        except Exception as e:
            self.log_test_result("获取统计信息", False, f"请求失败: {str(e)}")
    
    def test_import_sample_data(self):
        """测试导入示例数据"""
        try:
            # 检查示例数据文件是否存在
            sample_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Q&A_Base", "sample_qa_pairs.json")
            
            if not os.path.exists(sample_file):
                self.log_test_result("导入示例数据", False, f"示例数据文件不存在: {sample_file}")
                return
            
            # 上传文件
            with open(sample_file, 'rb') as f:
                files = {'file': ('sample_qa_pairs.json', f, 'application/json')}
                data = {
                    'file_type': 'json',
                    'overwrite_existing': 'false',
                    'default_category': 'sample',
                    'default_source': 'sample_import'
                }
                
                response = self.session.post(f"{self.api_base}/import", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_test_result("导入示例数据", True, "示例数据导入成功")
                else:
                    self.log_test_result("导入示例数据", False, "导入失败", result)
            else:
                self.log_test_result("导入示例数据", False, f"HTTP状态码: {response.status_code}")
                
        except Exception as e:
            self.log_test_result("导入示例数据", False, f"请求失败: {str(e)}")
    
    def test_backup(self):
        """测试备份功能"""
        try:
            backup_data = {
                "include_vectors": True,
                "compress": True,
                "backup_name": f"test_backup_{int(time.time())}"
            }
            
            response = self.session.post(f"{self.api_base}/backup", json=backup_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    backup_info = data.get("data", {})
                    backup_file = backup_info.get("backup_file", "")
                    backup_size = backup_info.get("backup_size", 0)
                    
                    self.log_test_result("数据备份", True, 
                                       f"备份成功，文件: {os.path.basename(backup_file)}，大小: {backup_size} 字节")
                else:
                    self.log_test_result("数据备份", False, "备份失败", data)
            else:
                self.log_test_result("数据备份", False, f"HTTP状态码: {response.status_code}")
                
        except Exception as e:
            self.log_test_result("数据备份", False, f"请求失败: {str(e)}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始运行问答系统综合测试...")
        print("=" * 60)
        
        # 基础功能测试
        self.test_health_check()
        
        # 数据导入测试
        self.test_import_sample_data()
        
        # 问答对管理测试
        self.test_create_qa_pair()
        self.test_batch_create_qa_pairs()
        
        # 查询功能测试
        self.test_query_qa()
        self.test_batch_query()
        
        # 管理功能测试
        self.test_list_qa_pairs()
        self.test_statistics()
        
        # 备份功能测试
        self.test_backup()
        
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


def main():
    """主函数"""
    print("GuiXiaoXiRag 问答系统测试")
    print("请确保服务已启动在 http://localhost:8002")
    print()
    
    # 等待用户确认
    input("按回车键开始测试...")
    
    # 创建测试器并运行测试
    tester = QASystemTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
