"""
简单同步测试 - 避免异步夹具问题
使用同步HTTP客户端进行测试
"""

import requests
import json
import time
from pathlib import Path


class TestSimpleSync:
    """简单同步测试类"""
    
    def __init__(self):
        self.base_url = "http://localhost:8002"
        self.api_prefix = "/api/v1"
        self.timeout = 30
    
    def get_url(self, endpoint: str) -> str:
        """获取完整的API URL"""
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        return f"{self.base_url}{self.api_prefix}{endpoint}"
    
    def test_system_health_check(self):
        """测试系统健康检查"""
        print("Testing system health check...")
        try:
            url = self.get_url("/health")
            response = requests.get(url, timeout=self.timeout)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✓ System health check passed")
                return True
            elif response.status_code == 404:
                print("! System health check endpoint not found")
                return False
            else:
                print(f"! System health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ System health check error: {e}")
            return False
    
    def test_qa_health_check(self):
        """测试QA健康检查"""
        print("Testing QA health check...")
        try:
            url = self.get_url("/qa/health")
            response = requests.get(url, timeout=self.timeout)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✓ QA health check passed")
                return True
            elif response.status_code == 404:
                print("! QA health check endpoint not found")
                return False
            else:
                print(f"! QA health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ QA health check error: {e}")
            return False
    
    def test_create_qa_pair(self):
        """测试创建问答对"""
        print("Testing QA pair creation...")
        try:
            url = self.get_url("/qa/pairs")
            data = {
                "question": "What is testing?",
                "answer": "Testing is the process of verifying software functionality",
                "category": "basic_test"
            }
            
            response = requests.post(url, json=data, timeout=self.timeout)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✓ QA pair creation passed")
                return True
            elif response.status_code == 404:
                print("! QA pair creation endpoint not found")
                return False
            else:
                print(f"! QA pair creation failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ QA pair creation error: {e}")
            return False
    
    def test_qa_query(self):
        """测试QA查询"""
        print("Testing QA query...")
        try:
            url = self.get_url("/qa/query")
            data = {
                "question": "What is testing",
                "top_k": 5
            }
            
            response = requests.post(url, json=data, timeout=self.timeout)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✓ QA query passed")
                return True
            elif response.status_code == 404:
                print("! QA query endpoint not found")
                return False
            else:
                print(f"! QA query failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ QA query error: {e}")
            return False
    
    def test_insert_text(self):
        """测试文本插入"""
        print("Testing text insertion...")
        try:
            url = self.get_url("/insert/text")
            data = {
                "text": "This is a test document for verifying text insertion functionality.",
                "doc_id": "test_doc_001",
                "knowledge_base": "test_kb",
                "language": "English"
            }
            
            response = requests.post(url, json=data, timeout=self.timeout)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✓ Text insertion passed")
                return True
            elif response.status_code == 404:
                print("! Text insertion endpoint not found")
                return False
            else:
                print(f"! Text insertion failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Text insertion error: {e}")
            return False
    
    def test_basic_query(self):
        """测试基本查询"""
        print("Testing basic query...")
        try:
            url = self.get_url("/query")
            data = {
                "query": "What is artificial intelligence?",
                "mode": "hybrid",
                "top_k": 5
            }
            
            response = requests.post(url, json=data, timeout=self.timeout)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✓ Basic query passed")
                return True
            elif response.status_code == 404:
                print("! Basic query endpoint not found")
                return False
            else:
                print(f"! Basic query failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Basic query error: {e}")
            return False
    
    def test_get_query_modes(self):
        """测试获取查询模式"""
        print("Testing get query modes...")
        try:
            url = self.get_url("/query/modes")
            response = requests.get(url, timeout=self.timeout)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✓ Get query modes passed")
                return True
            elif response.status_code == 404:
                print("! Get query modes endpoint not found")
                return False
            else:
                print(f"! Get query modes failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Get query modes error: {e}")
            return False
    
    def test_qa_statistics(self):
        """测试获取QA统计"""
        print("Testing QA statistics...")
        try:
            url = self.get_url("/qa/statistics")
            response = requests.get(url, timeout=self.timeout)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✓ QA statistics passed")
                return True
            elif response.status_code == 404:
                print("! QA statistics endpoint not found")
                return False
            else:
                print(f"! QA statistics failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ QA statistics error: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("Running Simple Sync Tests")
        print("=" * 60)
        
        tests = [
            ("System Health Check", self.test_system_health_check),
            ("QA Health Check", self.test_qa_health_check),
            ("Create QA Pair", self.test_create_qa_pair),
            ("QA Query", self.test_qa_query),
            ("Insert Text", self.test_insert_text),
            ("Basic Query", self.test_basic_query),
            ("Get Query Modes", self.test_get_query_modes),
            ("QA Statistics", self.test_qa_statistics)
        ]
        
        results = {}
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            try:
                result = test_func()
                results[test_name] = result
                if result:
                    passed += 1
            except Exception as e:
                print(f"✗ {test_name} exception: {e}")
                results[test_name] = False
        
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {passed/total:.2%}")
        
        print("\nDetailed Results:")
        for test_name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {test_name}: {status}")
        
        return results


def main():
    """主函数"""
    tester = TestSimpleSync()
    results = tester.run_all_tests()
    
    # 保存结果到文件
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    result_file = log_dir / f"simple_sync_test_{timestamp}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "test_type": "simple_sync",
            "results": results,
            "summary": {
                "total": len(results),
                "passed": sum(results.values()),
                "failed": len(results) - sum(results.values())
            }
        }, f, indent=2)
    
    print(f"\nResults saved to: {result_file}")


if __name__ == "__main__":
    main()
