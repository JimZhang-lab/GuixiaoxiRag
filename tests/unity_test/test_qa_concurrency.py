#!/usr/bin/env python3
"""
QA系统并发控制测试
验证多用户同时删除和创建操作的安全性
"""

import asyncio
import json
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any


class QAConcurrencyTester:
    """QA并发控制测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        
    def create_qa_pair(self, category: str, index: int) -> Dict[str, Any]:
        """创建问答对"""
        qa_data = {
            "question": f"What is test question {index} in {category}?",
            "answer": f"This is test answer {index} for category {category}.",
            "category": category,
            "confidence": 0.9,
            "keywords": [f"test{index}", category],
            "source": "concurrency_test"
        }
        
        try:
            response = requests.post(f"{self.api_base}/qa/pairs", json=qa_data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": result.get("success", False),
                    "qa_id": result.get("data", {}).get("qa_id"),
                    "category": category,
                    "index": index,
                    "thread_id": threading.current_thread().ident
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "category": category,
                    "index": index,
                    "thread_id": threading.current_thread().ident
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "category": category,
                "index": index,
                "thread_id": threading.current_thread().ident
            }
    
    def delete_category(self, category: str) -> Dict[str, Any]:
        """删除分类"""
        try:
            response = requests.delete(f"{self.api_base}/qa/categories/{category}", timeout=30)
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": result.get("success", False),
                    "deleted_count": result.get("data", {}).get("deleted_count", 0),
                    "folder_deleted": result.get("data", {}).get("folder_deleted", False),
                    "category": category,
                    "thread_id": threading.current_thread().ident
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "category": category,
                    "thread_id": threading.current_thread().ident
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "category": category,
                "thread_id": threading.current_thread().ident
            }
    
    def query_qa(self, question: str, category: str = None) -> Dict[str, Any]:
        """查询问答"""
        try:
            params = {"question": question}
            if category:
                params["category"] = category
                
            response = requests.post(f"{self.api_base}/qa/query", json=params, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": result.get("success", False),
                    "found": result.get("found", False),
                    "question": question,
                    "category": category,
                    "thread_id": threading.current_thread().ident
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "question": question,
                    "category": category,
                    "thread_id": threading.current_thread().ident
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "question": question,
                "category": category,
                "thread_id": threading.current_thread().ident
            }
    
    def test_concurrent_create_delete(self, category: str, num_creates: int = 5, num_deletes: int = 2):
        """测试并发创建和删除操作"""
        print(f"\n🧪 测试并发创建和删除 - 分类: {category}")
        
        tasks = []
        
        # 创建任务
        for i in range(num_creates):
            tasks.append(("create", category, i))
        
        # 删除任务
        for i in range(num_deletes):
            tasks.append(("delete", category, i))
        
        results = []
        start_time = time.time()
        
        # 使用线程池并发执行
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_task = {}
            
            for task_type, cat, index in tasks:
                if task_type == "create":
                    future = executor.submit(self.create_qa_pair, cat, index)
                else:  # delete
                    future = executor.submit(self.delete_category, cat)
                future_to_task[future] = (task_type, cat, index)
            
            # 收集结果
            for future in as_completed(future_to_task):
                task_type, cat, index = future_to_task[future]
                try:
                    result = future.result()
                    result["task_type"] = task_type
                    results.append(result)
                    
                    if result["success"]:
                        print(f"✅ {task_type.upper()} 成功: {cat} (线程: {result['thread_id']})")
                    else:
                        print(f"❌ {task_type.upper()} 失败: {cat} - {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"❌ 任务异常: {task_type} {cat} - {e}")
        
        duration = time.time() - start_time
        
        # 分析结果
        create_results = [r for r in results if r["task_type"] == "create"]
        delete_results = [r for r in results if r["task_type"] == "delete"]
        
        create_success = len([r for r in create_results if r["success"]])
        delete_success = len([r for r in delete_results if r["success"]])
        
        print(f"\n📊 测试结果:")
        print(f"   总耗时: {duration:.2f}秒")
        print(f"   创建操作: {create_success}/{len(create_results)} 成功")
        print(f"   删除操作: {delete_success}/{len(delete_results)} 成功")
        
        return {
            "category": category,
            "duration": duration,
            "create_success": create_success,
            "create_total": len(create_results),
            "delete_success": delete_success,
            "delete_total": len(delete_results),
            "results": results
        }
    
    def test_concurrent_queries(self, categories: List[str], num_queries_per_category: int = 3):
        """测试并发查询操作"""
        print(f"\n🔍 测试并发查询 - 分类: {categories}")
        
        tasks = []
        for category in categories:
            for i in range(num_queries_per_category):
                tasks.append((category, f"test question {i}"))
        
        results = []
        start_time = time.time()
        
        # 使用线程池并发执行查询
        with ThreadPoolExecutor(max_workers=15) as executor:
            future_to_task = {}
            
            for category, question in tasks:
                future = executor.submit(self.query_qa, question, category)
                future_to_task[future] = (category, question)
            
            # 收集结果
            for future in as_completed(future_to_task):
                category, question = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result["success"]:
                        status = "找到" if result["found"] else "未找到"
                        print(f"✅ 查询成功: {category} - {status} (线程: {result['thread_id']})")
                    else:
                        print(f"❌ 查询失败: {category} - {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"❌ 查询异常: {category} - {e}")
        
        duration = time.time() - start_time
        success_count = len([r for r in results if r["success"]])
        
        print(f"\n📊 查询测试结果:")
        print(f"   总耗时: {duration:.2f}秒")
        print(f"   成功查询: {success_count}/{len(results)}")
        
        return {
            "duration": duration,
            "success_count": success_count,
            "total_queries": len(results),
            "results": results
        }
    
    def run_all_tests(self):
        """运行所有并发测试"""
        print("=" * 60)
        print("🧪 QA系统并发控制测试套件")
        print("=" * 60)
        
        # 检查服务可用性
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code != 200:
                print("❌ 服务不可用，请确保GuixiaoxiRag服务正在运行")
                return
        except Exception as e:
            print(f"❌ 无法连接到服务: {e}")
            return
        
        test_results = []
        
        # 测试1: 单个分类的并发创建和删除
        result1 = self.test_concurrent_create_delete("concurrent_test_1", 8, 3)
        test_results.append(result1)
        
        # 测试2: 多个分类的并发操作
        result2 = self.test_concurrent_create_delete("concurrent_test_2", 5, 2)
        test_results.append(result2)
        
        # 测试3: 并发查询
        result3 = self.test_concurrent_queries(["concurrent_test_1", "concurrent_test_2", "general"], 4)
        test_results.append(result3)
        
        # 总结
        print("\n" + "=" * 60)
        print("📊 并发测试总结")
        print("=" * 60)
        
        total_operations = sum(r.get("create_total", 0) + r.get("delete_total", 0) + r.get("total_queries", 0) for r in test_results)
        total_success = sum(r.get("create_success", 0) + r.get("delete_success", 0) + r.get("success_count", 0) for r in test_results)
        
        print(f"总操作数: {total_operations}")
        print(f"成功操作: {total_success}")
        print(f"成功率: {total_success/total_operations*100:.1f}%")
        
        return test_results


def main():
    """主函数"""
    tester = QAConcurrencyTester()
    results = tester.run_all_tests()
    
    # 保存结果
    timestamp = int(time.time())
    with open(f"logs/concurrency_test_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 测试结果已保存: logs/concurrency_test_{timestamp}.json")


if __name__ == "__main__":
    main()
