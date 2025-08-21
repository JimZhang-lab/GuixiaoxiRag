"""
测试工具类
提供通用的测试辅助功能
"""

import uuid
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests
from datetime import datetime


class TestUtils:
    """测试工具类"""
    
    @staticmethod
    def generate_test_id() -> str:
        """生成测试ID"""
        return f"test_{uuid.uuid4().hex[:8]}"
    
    @staticmethod
    def generate_timestamp() -> str:
        """生成时间戳"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @staticmethod
    def create_test_file(content: str, filename: str, directory: Path) -> Path:
        """创建测试文件"""
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / filename
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    @staticmethod
    def create_test_json_file(data: Dict[str, Any], filename: str, directory: Path) -> Path:
        """创建测试JSON文件"""
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return file_path
    
    @staticmethod
    def wait_for_service(base_url: str, endpoint: str = "/health", timeout: int = 30) -> bool:
        """等待服务可用"""
        url = f"{base_url}/api/v1{endpoint}"
        
        for _ in range(timeout):
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return True
            except:
                pass
            time.sleep(1)
        
        return False
    
    @staticmethod
    def assert_response_success(response: requests.Response, expected_status: int = 200):
        """断言响应成功"""
        assert response.status_code == expected_status, \
            f"Expected {expected_status}, got {response.status_code}: {response.text}"
        
        # 检查JSON响应中的success字段
        if response.headers.get("content-type", "").startswith("application/json"):
            try:
                data = response.json()
                if "success" in data:
                    assert data["success"] is True, f"Response not successful: {data}"
            except:
                pass  # 如果不是有效的JSON，跳过检查
    
    @staticmethod
    def assert_response_error(response: requests.Response, expected_status: int = None):
        """断言响应错误"""
        if expected_status:
            assert response.status_code == expected_status, \
                f"Expected {expected_status}, got {response.status_code}"
        else:
            assert response.status_code >= 400, \
                f"Expected error status, got {response.status_code}"
    
    @staticmethod
    def measure_time(func, *args, **kwargs) -> tuple:
        """测量函数执行时间"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        return result, duration
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """格式化持续时间"""
        if seconds < 1:
            return f"{seconds*1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.2f}s"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m{remaining_seconds:.1f}s"
    
    @staticmethod
    def format_size(bytes_size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f}{unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f}TB"
    
    @staticmethod
    def safe_json_loads(text: str) -> Optional[Dict[str, Any]]:
        """安全地解析JSON"""
        try:
            return json.loads(text)
        except:
            return None
    
    @staticmethod
    def extract_error_message(response: requests.Response) -> str:
        """从响应中提取错误消息"""
        try:
            data = response.json()
            if "message" in data:
                return data["message"]
            elif "error" in data:
                return data["error"]
            elif "detail" in data:
                return data["detail"]
        except:
            pass
        
        return response.text[:200] if response.text else f"HTTP {response.status_code}"
    
    @staticmethod
    def create_sample_qa_pair(category: str = "test") -> Dict[str, Any]:
        """创建示例问答对"""
        test_id = TestUtils.generate_test_id()
        return {
            "question": f"What is {test_id}?",
            "answer": f"{test_id} is a test question for validation purposes.",
            "category": category,
            "confidence": 0.9,
            "keywords": [test_id, "test", "validation"],
            "source": "test_utils"
        }
    
    @staticmethod
    def create_sample_document(language: str = "English") -> Dict[str, Any]:
        """创建示例文档"""
        test_id = TestUtils.generate_test_id()
        
        if language.lower() in ["chinese", "中文"]:
            text = f"这是一个测试文档 {test_id}，用于验证文档插入功能。"
            language = "中文"
        else:
            text = f"This is a test document {test_id} for verifying document insertion functionality."
            language = "English"
        
        return {
            "text": text,
            "doc_id": f"doc_{test_id}",
            "knowledge_base": "test_kb",
            "language": language
        }
    
    @staticmethod
    def create_sample_query(mode: str = "hybrid") -> Dict[str, Any]:
        """创建示例查询"""
        return {
            "query": "What is artificial intelligence?",
            "mode": mode,
            "top_k": 5
        }
    
    @staticmethod
    def validate_response_structure(response_data: Dict[str, Any], 
                                  required_fields: List[str]) -> bool:
        """验证响应结构"""
        for field in required_fields:
            if field not in response_data:
                return False
        return True
    
    @staticmethod
    def save_test_results(results: Dict[str, Any], 
                         output_dir: Path, 
                         filename: str = None) -> Path:
        """保存测试结果"""
        if filename is None:
            timestamp = TestUtils.generate_timestamp()
            filename = f"test_results_{timestamp}.json"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        result_file = output_dir / filename
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return result_file
    
    @staticmethod
    def load_test_results(file_path: Path) -> Optional[Dict[str, Any]]:
        """加载测试结果"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    @staticmethod
    def compare_test_results(current: Dict[str, Any], 
                           previous: Dict[str, Any]) -> Dict[str, Any]:
        """比较测试结果"""
        comparison = {
            "current_summary": current.get("summary", {}),
            "previous_summary": previous.get("summary", {}),
            "improvements": [],
            "regressions": []
        }
        
        current_summary = current.get("summary", {})
        previous_summary = previous.get("summary", {})
        
        # 比较成功率
        current_rate = current_summary.get("passed", 0) / max(current_summary.get("total", 1), 1)
        previous_rate = previous_summary.get("passed", 0) / max(previous_summary.get("total", 1), 1)
        
        if current_rate > previous_rate:
            comparison["improvements"].append(f"成功率提升: {previous_rate:.2%} -> {current_rate:.2%}")
        elif current_rate < previous_rate:
            comparison["regressions"].append(f"成功率下降: {previous_rate:.2%} -> {current_rate:.2%}")
        
        return comparison
