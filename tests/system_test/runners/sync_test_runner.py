"""
同步测试运行器
使用requests库进行HTTP测试，避免异步配置问题
"""

import requests
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys
import os

# 添加配置路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.test_config import config, API_ENDPOINTS
from utils.test_logger import TestLogger
from utils.test_utils import TestUtils


class SyncTestRunner:
    """同步测试运行器"""
    
    def __init__(self, 
                 base_url: str = "http://localhost:8002",
                 timeout: int = 60,
                 output_dir: str = "logs",
                 skip_text_insert: bool = False):
        self.base_url = base_url
        self.api_prefix = "/api/v1"
        self.timeout = timeout
        self.skip_text_insert = skip_text_insert
        
        # 设置输出目录
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化日志和工具
        self.logger = TestLogger("SyncTestRunner", self.output_dir)
        self.utils = TestUtils()
        
        # 测试结果
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def get_url(self, endpoint: str) -> str:
        """获取完整的API URL"""
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        return f"{self.base_url}{self.api_prefix}{endpoint}"
    
    def test_system_health_check(self) -> Dict[str, Any]:
        """测试系统健康检查"""
        test_name = "System Health Check"
        self.logger.test_start(test_name)
        self.logger.debug(f"开始执行 {test_name}")

        try:
            # 构建请求URL
            url = self.get_url(API_ENDPOINTS["system"]["health"])
            self.logger.debug(f"请求URL: {url}")
            self.logger.debug(f"超时设置: {self.timeout}秒")

            # 发送请求
            start_time = time.time()
            self.logger.debug("发送GET请求...")
            response = requests.get(url, timeout=self.timeout)
            duration = time.time() - start_time

            # 记录响应信息
            self.logger.debug(f"响应状态码: {response.status_code}")
            self.logger.debug(f"响应头: {dict(response.headers)}")
            self.logger.debug(f"响应时间: {duration:.3f}秒")
            self.logger.debug(f"响应大小: {len(response.content)}字节")

            if response.status_code == 200:
                try:
                    data = response.json()
                    self.logger.debug(f"响应数据: {data}")

                    # 验证响应结构
                    if "status" in data:
                        self.logger.debug(f"系统状态: {data['status']}")
                    if "system" in data:
                        system_info = data["system"]
                        self.logger.debug(f"服务名称: {system_info.get('service_name', 'N/A')}")
                        self.logger.debug(f"版本: {system_info.get('version', 'N/A')}")
                        self.logger.debug(f"运行时间: {system_info.get('uptime', 'N/A')}秒")
                        self.logger.debug(f"工作目录: {system_info.get('working_dir', 'N/A')}")

                    self.logger.test_pass(test_name, duration)
                    return {
                        "success": True,
                        "duration": duration,
                        "status_code": response.status_code,
                        "data": data
                    }
                except json.JSONDecodeError as e:
                    self.logger.debug(f"JSON解析失败: {e}")
                    self.logger.debug(f"原始响应: {response.text[:500]}")
                    error_msg = f"JSON解析失败: {e}"
                    self.logger.test_fail(test_name, error_msg, duration)
                    return {
                        "success": False,
                        "duration": duration,
                        "status_code": response.status_code,
                        "error": error_msg
                    }
            else:
                error_msg = f"HTTP {response.status_code}"
                self.logger.debug(f"请求失败: {error_msg}")
                self.logger.debug(f"错误响应: {response.text[:500]}")
                self.logger.test_fail(test_name, error_msg, duration)
                return {
                    "success": False,
                    "duration": duration,
                    "status_code": response.status_code,
                    "error": error_msg
                }

        except requests.exceptions.Timeout as e:
            self.logger.debug(f"请求超时: {e}")
            self.logger.test_fail(test_name, f"请求超时: {e}")
            return {
                "success": False,
                "error": f"请求超时: {e}"
            }
        except requests.exceptions.ConnectionError as e:
            self.logger.debug(f"连接错误: {e}")
            self.logger.test_fail(test_name, f"连接错误: {e}")
            return {
                "success": False,
                "error": f"连接错误: {e}"
            }
        except Exception as e:
            self.logger.debug(f"未知异常: {e}")
            self.logger.debug(f"异常类型: {type(e).__name__}")
            import traceback
            self.logger.debug(f"异常堆栈: {traceback.format_exc()}")
            self.logger.test_fail(test_name, str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_qa_health_check(self) -> Dict[str, Any]:
        """测试QA健康检查"""
        test_name = "QA Health Check"
        self.logger.test_start(test_name)
        self.logger.debug(f"开始执行 {test_name}")

        try:
            # 构建请求URL
            url = self.get_url(API_ENDPOINTS["qa"]["health"])
            self.logger.debug(f"请求URL: {url}")
            self.logger.debug(f"超时设置: {self.timeout}秒")

            # 发送请求
            start_time = time.time()
            self.logger.debug("发送GET请求到QA健康检查端点...")
            response = requests.get(url, timeout=self.timeout)
            duration = time.time() - start_time

            # 记录响应信息
            self.logger.debug(f"响应状态码: {response.status_code}")
            self.logger.debug(f"响应头: {dict(response.headers)}")
            self.logger.debug(f"响应时间: {duration:.3f}秒")
            self.logger.debug(f"响应大小: {len(response.content)}字节")

            if response.status_code == 200:
                try:
                    data = response.json()
                    self.logger.debug(f"QA健康检查响应: {data}")

                    # 验证QA系统状态
                    if "success" in data:
                        self.logger.debug(f"QA系统成功状态: {data['success']}")
                    if "data" in data:
                        qa_data = data["data"]
                        self.logger.debug(f"QA存储状态: {qa_data.get('qa_storage_status', 'N/A')}")
                        self.logger.debug(f"嵌入状态: {qa_data.get('embedding_status', 'N/A')}")
                        self.logger.debug(f"问答对总数: {qa_data.get('total_qa_pairs', 'N/A')}")
                        self.logger.debug(f"平均响应时间: {qa_data.get('avg_response_time', 'N/A')}秒")
                        self.logger.debug(f"错误率: {qa_data.get('error_rate', 'N/A')}")

                    self.logger.test_pass(test_name, duration)
                    return {
                        "success": True,
                        "duration": duration,
                        "status_code": response.status_code,
                        "data": data
                    }
                except json.JSONDecodeError as e:
                    self.logger.debug(f"JSON解析失败: {e}")
                    self.logger.debug(f"原始响应: {response.text[:500]}")
                    error_msg = f"JSON解析失败: {e}"
                    self.logger.test_fail(test_name, error_msg, duration)
                    return {
                        "success": False,
                        "duration": duration,
                        "status_code": response.status_code,
                        "error": error_msg
                    }
            else:
                error_msg = f"HTTP {response.status_code}"
                self.logger.debug(f"QA健康检查失败: {error_msg}")
                self.logger.debug(f"错误响应: {response.text[:500]}")
                self.logger.test_fail(test_name, error_msg, duration)
                return {
                    "success": False,
                    "duration": duration,
                    "status_code": response.status_code,
                    "error": error_msg
                }

        except requests.exceptions.Timeout as e:
            self.logger.debug(f"QA健康检查请求超时: {e}")
            self.logger.test_fail(test_name, f"请求超时: {e}")
            return {
                "success": False,
                "error": f"请求超时: {e}"
            }
        except requests.exceptions.ConnectionError as e:
            self.logger.debug(f"QA健康检查连接错误: {e}")
            self.logger.test_fail(test_name, f"连接错误: {e}")
            return {
                "success": False,
                "error": f"连接错误: {e}"
            }
        except Exception as e:
            self.logger.debug(f"QA健康检查未知异常: {e}")
            self.logger.debug(f"异常类型: {type(e).__name__}")
            import traceback
            self.logger.debug(f"异常堆栈: {traceback.format_exc()}")
            self.logger.test_fail(test_name, str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_create_qa_pair(self) -> Dict[str, Any]:
        """测试创建问答对"""
        test_name = "Create QA Pair"
        self.logger.test_start(test_name)
        self.logger.debug(f"开始执行 {test_name}")

        try:
            # 构建请求URL
            url = self.get_url(API_ENDPOINTS["qa"]["pairs"])
            self.logger.debug(f"请求URL: {url}")

            # 生成测试问答对
            qa_pair = self.utils.create_sample_qa_pair("sync_test")
            self.logger.debug(f"生成的问答对: {qa_pair}")
            self.logger.debug(f"问题: {qa_pair['question']}")
            self.logger.debug(f"答案: {qa_pair['answer']}")
            self.logger.debug(f"分类: {qa_pair['category']}")
            self.logger.debug(f"置信度: {qa_pair['confidence']}")

            # 准备请求
            headers = {"Content-Type": "application/json"}
            self.logger.debug(f"请求头: {headers}")
            self.logger.debug(f"请求体大小: {len(str(qa_pair))}字符")

            # 发送请求
            start_time = time.time()
            self.logger.debug("发送POST请求创建问答对...")
            response = requests.post(url, json=qa_pair, headers=headers, timeout=self.timeout)
            duration = time.time() - start_time

            # 记录响应信息
            self.logger.debug(f"响应状态码: {response.status_code}")
            self.logger.debug(f"响应头: {dict(response.headers)}")
            self.logger.debug(f"响应时间: {duration:.3f}秒")
            self.logger.debug(f"响应大小: {len(response.content)}字节")

            if response.status_code == 200:
                try:
                    data = response.json()
                    self.logger.debug(f"创建问答对响应: {data}")

                    # 验证响应结构
                    if "success" in data:
                        self.logger.debug(f"创建成功状态: {data['success']}")
                    if "data" in data and "qa_id" in data["data"]:
                        qa_id = data["data"]["qa_id"]
                        self.logger.debug(f"生成的问答对ID: {qa_id}")
                    if "message" in data:
                        self.logger.debug(f"响应消息: {data['message']}")

                    self.logger.test_pass(test_name, duration)
                    return {
                        "success": True,
                        "duration": duration,
                        "status_code": response.status_code,
                        "data": data,
                        "qa_pair": qa_pair
                    }
                except json.JSONDecodeError as e:
                    self.logger.debug(f"JSON解析失败: {e}")
                    self.logger.debug(f"原始响应: {response.text[:500]}")
                    error_msg = f"JSON解析失败: {e}"
                    self.logger.test_fail(test_name, error_msg, duration)
                    return {
                        "success": False,
                        "duration": duration,
                        "status_code": response.status_code,
                        "error": error_msg
                    }
            else:
                error_msg = self.utils.extract_error_message(response)
                self.logger.debug(f"创建问答对失败: {error_msg}")
                self.logger.debug(f"错误响应: {response.text[:500]}")
                self.logger.test_fail(test_name, error_msg, duration)
                return {
                    "success": False,
                    "duration": duration,
                    "status_code": response.status_code,
                    "error": error_msg
                }

        except requests.exceptions.Timeout as e:
            self.logger.debug(f"创建问答对请求超时: {e}")
            self.logger.test_fail(test_name, f"请求超时: {e}")
            return {
                "success": False,
                "error": f"请求超时: {e}"
            }
        except requests.exceptions.ConnectionError as e:
            self.logger.debug(f"创建问答对连接错误: {e}")
            self.logger.test_fail(test_name, f"连接错误: {e}")
            return {
                "success": False,
                "error": f"连接错误: {e}"
            }
        except Exception as e:
            self.logger.debug(f"创建问答对未知异常: {e}")
            self.logger.debug(f"异常类型: {type(e).__name__}")
            import traceback
            self.logger.debug(f"异常堆栈: {traceback.format_exc()}")
            self.logger.test_fail(test_name, str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_qa_query(self) -> Dict[str, Any]:
        """测试QA查询"""
        test_name = "QA Query"
        self.logger.test_start(test_name)
        self.logger.debug(f"开始执行 {test_name}")

        try:
            # 构建请求URL
            url = self.get_url(API_ENDPOINTS["qa"]["query"])
            self.logger.debug(f"请求URL: {url}")

            # 准备查询数据
            query_data = {
                "question": "What is testing",
                "top_k": 5
            }
            self.logger.debug(f"查询数据: {query_data}")
            self.logger.debug(f"查询问题: {query_data['question']}")
            self.logger.debug(f"返回结果数量: {query_data['top_k']}")

            # 准备请求
            headers = {"Content-Type": "application/json"}
            self.logger.debug(f"请求头: {headers}")

            # 发送请求
            start_time = time.time()
            self.logger.debug("发送POST请求进行QA查询...")
            response = requests.post(url, json=query_data, headers=headers, timeout=self.timeout)
            duration = time.time() - start_time

            # 记录响应信息
            self.logger.debug(f"响应状态码: {response.status_code}")
            self.logger.debug(f"响应头: {dict(response.headers)}")
            self.logger.debug(f"响应时间: {duration:.3f}秒")
            self.logger.debug(f"响应大小: {len(response.content)}字节")

            if response.status_code == 200:
                try:
                    data = response.json()
                    self.logger.debug(f"QA查询响应: {data}")

                    # 验证查询结果
                    if "success" in data:
                        self.logger.debug(f"查询成功状态: {data['success']}")
                    if "found" in data:
                        self.logger.debug(f"是否找到匹配: {data['found']}")
                    if "answer" in data:
                        self.logger.debug(f"答案: {data['answer']}")
                    if "similarity" in data:
                        self.logger.debug(f"相似度: {data['similarity']}")
                    if "confidence" in data:
                        self.logger.debug(f"置信度: {data['confidence']}")
                    if "response_time" in data:
                        self.logger.debug(f"服务器响应时间: {data['response_time']}秒")
                    if "all_results" in data:
                        results_count = len(data["all_results"])
                        self.logger.debug(f"所有结果数量: {results_count}")
                        for i, result in enumerate(data["all_results"][:3]):  # 只显示前3个
                            self.logger.debug(f"结果{i+1}: 相似度={result.get('similarity', 'N/A')}, 问题={result.get('question', 'N/A')[:50]}...")

                    self.logger.test_pass(test_name, duration)
                    return {
                        "success": True,
                        "duration": duration,
                        "status_code": response.status_code,
                        "data": data
                    }
                except json.JSONDecodeError as e:
                    self.logger.debug(f"JSON解析失败: {e}")
                    self.logger.debug(f"原始响应: {response.text[:500]}")
                    error_msg = f"JSON解析失败: {e}"
                    self.logger.test_fail(test_name, error_msg, duration)
                    return {
                        "success": False,
                        "duration": duration,
                        "status_code": response.status_code,
                        "error": error_msg
                    }
            else:
                error_msg = self.utils.extract_error_message(response)
                self.logger.debug(f"QA查询失败: {error_msg}")
                self.logger.debug(f"错误响应: {response.text[:500]}")
                self.logger.test_fail(test_name, error_msg, duration)
                return {
                    "success": False,
                    "duration": duration,
                    "status_code": response.status_code,
                    "error": error_msg
                }

        except requests.exceptions.Timeout as e:
            self.logger.debug(f"QA查询请求超时: {e}")
            self.logger.test_fail(test_name, f"请求超时: {e}")
            return {
                "success": False,
                "error": f"请求超时: {e}"
            }
        except requests.exceptions.ConnectionError as e:
            self.logger.debug(f"QA查询连接错误: {e}")
            self.logger.test_fail(test_name, f"连接错误: {e}")
            return {
                "success": False,
                "error": f"连接错误: {e}"
            }
        except Exception as e:
            self.logger.debug(f"QA查询未知异常: {e}")
            self.logger.debug(f"异常类型: {type(e).__name__}")
            import traceback
            self.logger.debug(f"异常堆栈: {traceback.format_exc()}")
            self.logger.test_fail(test_name, str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_insert_text(self) -> Dict[str, Any]:
        """测试文本插入"""
        test_name = "Insert Text"

        if self.skip_text_insert:
            self.logger.test_skip(test_name, "跳过慢速文本插入测试")
            self.logger.debug("文本插入测试被跳过，因为设置了 skip_text_insert=True")
            return {
                "success": True,
                "skipped": True,
                "reason": "跳过慢速文本插入测试"
            }

        self.logger.test_start(test_name)
        self.logger.debug(f"开始执行 {test_name}")
        self.logger.debug("注意: 文本插入操作通常需要较长时间（30-60秒）")

        try:
            # 构建请求URL
            url = self.get_url(API_ENDPOINTS["document"]["insert_text"])
            self.logger.debug(f"请求URL: {url}")

            # 生成测试文档
            document = self.utils.create_sample_document("English")
            self.logger.debug(f"生成的文档: {document}")
            self.logger.debug(f"文档ID: {document['doc_id']}")
            self.logger.debug(f"文档语言: {document['language']}")
            self.logger.debug(f"知识库: {document['knowledge_base']}")
            self.logger.debug(f"文档内容长度: {len(document['text'])}字符")
            self.logger.debug(f"文档内容: {document['text'][:100]}...")

            # 准备请求
            headers = {"Content-Type": "application/json"}
            self.logger.debug(f"请求头: {headers}")
            extended_timeout = self.timeout * 2
            self.logger.debug(f"扩展超时时间: {extended_timeout}秒（原超时时间的2倍）")

            # 发送请求
            start_time = time.time()
            self.logger.debug("发送POST请求进行文本插入...")
            self.logger.debug("开始计时，文本插入可能需要较长时间...")

            response = requests.post(url, json=document, headers=headers, timeout=extended_timeout)
            duration = time.time() - start_time

            # 记录响应信息
            self.logger.debug(f"文本插入完成，总耗时: {duration:.3f}秒")
            self.logger.debug(f"响应状态码: {response.status_code}")
            self.logger.debug(f"响应头: {dict(response.headers)}")
            self.logger.debug(f"响应大小: {len(response.content)}字节")

            if response.status_code == 200:
                try:
                    data = response.json()
                    self.logger.debug(f"文本插入响应: {data}")

                    # 验证插入结果
                    if "success" in data:
                        self.logger.debug(f"插入成功状态: {data['success']}")
                    if "message" in data:
                        self.logger.debug(f"响应消息: {data['message']}")
                    if "data" in data:
                        insert_data = data["data"]
                        if "doc_id" in insert_data:
                            self.logger.debug(f"插入的文档ID: {insert_data['doc_id']}")
                        if "chunks_created" in insert_data:
                            self.logger.debug(f"创建的文档块数量: {insert_data['chunks_created']}")
                        if "processing_time" in insert_data:
                            self.logger.debug(f"服务器处理时间: {insert_data['processing_time']}秒")

                    self.logger.test_pass(test_name, duration)
                    return {
                        "success": True,
                        "duration": duration,
                        "status_code": response.status_code,
                        "data": data
                    }
                except json.JSONDecodeError as e:
                    self.logger.debug(f"JSON解析失败: {e}")
                    self.logger.debug(f"原始响应: {response.text[:500]}")
                    error_msg = f"JSON解析失败: {e}"
                    self.logger.test_fail(test_name, error_msg, duration)
                    return {
                        "success": False,
                        "duration": duration,
                        "status_code": response.status_code,
                        "error": error_msg
                    }
            else:
                error_msg = self.utils.extract_error_message(response)
                self.logger.debug(f"文本插入失败: {error_msg}")
                self.logger.debug(f"错误响应: {response.text[:500]}")
                self.logger.test_fail(test_name, error_msg, duration)
                return {
                    "success": False,
                    "duration": duration,
                    "status_code": response.status_code,
                    "error": error_msg
                }

        except requests.exceptions.Timeout as e:
            duration = time.time() - start_time if 'start_time' in locals() else 0
            self.logger.debug(f"文本插入请求超时: {e}")
            self.logger.debug(f"超时时间: {extended_timeout}秒，实际耗时: {duration:.3f}秒")
            self.logger.debug("文本插入操作通常需要较长时间，可以考虑增加超时时间或跳过此测试")
            self.logger.test_fail(test_name, f"请求超时: {e}")
            return {
                "success": False,
                "error": f"请求超时: {e}",
                "duration": duration
            }
        except requests.exceptions.ConnectionError as e:
            self.logger.debug(f"文本插入连接错误: {e}")
            self.logger.test_fail(test_name, f"连接错误: {e}")
            return {
                "success": False,
                "error": f"连接错误: {e}"
            }
        except Exception as e:
            self.logger.debug(f"文本插入未知异常: {e}")
            self.logger.debug(f"异常类型: {type(e).__name__}")
            import traceback
            self.logger.debug(f"异常堆栈: {traceback.format_exc()}")
            self.logger.test_fail(test_name, str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_basic_query(self) -> Dict[str, Any]:
        """测试基本查询"""
        test_name = "Basic Query"
        self.logger.test_start(test_name)
        self.logger.debug(f"开始执行 {test_name}")

        try:
            # 构建请求URL
            url = self.get_url(API_ENDPOINTS["query"]["query"])
            self.logger.debug(f"请求URL: {url}")

            # 生成查询数据
            query_data = self.utils.create_sample_query("hybrid")
            self.logger.debug(f"查询数据: {query_data}")
            self.logger.debug(f"查询内容: {query_data['query']}")
            self.logger.debug(f"查询模式: {query_data['mode']}")
            self.logger.debug(f"返回结果数量: {query_data['top_k']}")

            # 准备请求
            headers = {"Content-Type": "application/json"}
            self.logger.debug(f"请求头: {headers}")

            # 发送请求
            start_time = time.time()
            self.logger.debug("发送POST请求进行基本查询...")
            response = requests.post(url, json=query_data, headers=headers, timeout=self.timeout)
            duration = time.time() - start_time

            # 记录响应信息
            self.logger.debug(f"响应状态码: {response.status_code}")
            self.logger.debug(f"响应头: {dict(response.headers)}")
            self.logger.debug(f"响应时间: {duration:.3f}秒")
            self.logger.debug(f"响应大小: {len(response.content)}字节")

            if response.status_code == 200:
                try:
                    data = response.json()
                    self.logger.debug(f"基本查询响应结构: {list(data.keys())}")

                    # 验证查询结果
                    if "success" in data:
                        self.logger.debug(f"查询成功状态: {data['success']}")
                    if "message" in data:
                        self.logger.debug(f"响应消息: {data['message']}")
                    if "data" in data:
                        query_result = data["data"]
                        if "result" in query_result:
                            result_text = query_result["result"]
                            self.logger.debug(f"查询结果长度: {len(result_text)}字符")
                            self.logger.debug(f"查询结果预览: {result_text[:200]}...")
                        if "mode" in query_result:
                            self.logger.debug(f"使用的查询模式: {query_result['mode']}")
                        if "query" in query_result:
                            self.logger.debug(f"查询问题: {query_result['query']}")
                        if "response_time" in query_result:
                            self.logger.debug(f"服务器响应时间: {query_result['response_time']}秒")
                        if "context_sources" in query_result:
                            sources = query_result["context_sources"]
                            if sources:
                                self.logger.debug(f"上下文源数量: {len(sources)}")
                            else:
                                self.logger.debug("无上下文源")

                    self.logger.test_pass(test_name, duration)
                    return {
                        "success": True,
                        "duration": duration,
                        "status_code": response.status_code,
                        "data": data
                    }
                except json.JSONDecodeError as e:
                    self.logger.debug(f"JSON解析失败: {e}")
                    self.logger.debug(f"原始响应: {response.text[:500]}")
                    error_msg = f"JSON解析失败: {e}"
                    self.logger.test_fail(test_name, error_msg, duration)
                    return {
                        "success": False,
                        "duration": duration,
                        "status_code": response.status_code,
                        "error": error_msg
                    }
            else:
                error_msg = self.utils.extract_error_message(response)
                self.logger.debug(f"基本查询失败: {error_msg}")
                self.logger.debug(f"错误响应: {response.text[:500]}")
                self.logger.test_fail(test_name, error_msg, duration)
                return {
                    "success": False,
                    "duration": duration,
                    "status_code": response.status_code,
                    "error": error_msg
                }

        except requests.exceptions.Timeout as e:
            self.logger.debug(f"基本查询请求超时: {e}")
            self.logger.test_fail(test_name, f"请求超时: {e}")
            return {
                "success": False,
                "error": f"请求超时: {e}"
            }
        except requests.exceptions.ConnectionError as e:
            self.logger.debug(f"基本查询连接错误: {e}")
            self.logger.test_fail(test_name, f"连接错误: {e}")
            return {
                "success": False,
                "error": f"连接错误: {e}"
            }
        except Exception as e:
            self.logger.debug(f"基本查询未知异常: {e}")
            self.logger.debug(f"异常类型: {type(e).__name__}")
            import traceback
            self.logger.debug(f"异常堆栈: {traceback.format_exc()}")
            self.logger.test_fail(test_name, str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_get_query_modes(self) -> Dict[str, Any]:
        """测试获取查询模式"""
        test_name = "Get Query Modes"
        self.logger.test_start(test_name)
        self.logger.debug(f"开始执行 {test_name}")

        try:
            # 构建请求URL
            url = self.get_url(API_ENDPOINTS["query"]["modes"])
            self.logger.debug(f"请求URL: {url}")

            # 发送请求
            start_time = time.time()
            self.logger.debug("发送GET请求获取查询模式...")
            response = requests.get(url, timeout=self.timeout)
            duration = time.time() - start_time

            # 记录响应信息
            self.logger.debug(f"响应状态码: {response.status_code}")
            self.logger.debug(f"响应头: {dict(response.headers)}")
            self.logger.debug(f"响应时间: {duration:.3f}秒")
            self.logger.debug(f"响应大小: {len(response.content)}字节")

            if response.status_code == 200:
                try:
                    data = response.json()
                    self.logger.debug(f"查询模式响应: {data}")

                    # 验证查询模式
                    if "success" in data:
                        self.logger.debug(f"获取成功状态: {data['success']}")
                    if "data" in data:
                        modes_data = data["data"]
                        if "modes" in modes_data:
                            modes = modes_data["modes"]
                            self.logger.debug(f"可用查询模式数量: {len(modes)}")
                            for mode_name, mode_desc in modes.items():
                                self.logger.debug(f"模式 '{mode_name}': {mode_desc}")
                        if "default" in modes_data:
                            self.logger.debug(f"默认查询模式: {modes_data['default']}")
                        if "recommended" in modes_data:
                            recommended = modes_data["recommended"]
                            self.logger.debug(f"推荐查询模式: {recommended}")

                    self.logger.test_pass(test_name, duration)
                    return {
                        "success": True,
                        "duration": duration,
                        "status_code": response.status_code,
                        "data": data
                    }
                except json.JSONDecodeError as e:
                    self.logger.debug(f"JSON解析失败: {e}")
                    self.logger.debug(f"原始响应: {response.text[:500]}")
                    error_msg = f"JSON解析失败: {e}"
                    self.logger.test_fail(test_name, error_msg, duration)
                    return {
                        "success": False,
                        "duration": duration,
                        "status_code": response.status_code,
                        "error": error_msg
                    }
            else:
                error_msg = self.utils.extract_error_message(response)
                self.logger.debug(f"获取查询模式失败: {error_msg}")
                self.logger.debug(f"错误响应: {response.text[:500]}")
                self.logger.test_fail(test_name, error_msg, duration)
                return {
                    "success": False,
                    "duration": duration,
                    "status_code": response.status_code,
                    "error": error_msg
                }

        except requests.exceptions.Timeout as e:
            self.logger.debug(f"获取查询模式请求超时: {e}")
            self.logger.test_fail(test_name, f"请求超时: {e}")
            return {
                "success": False,
                "error": f"请求超时: {e}"
            }
        except requests.exceptions.ConnectionError as e:
            self.logger.debug(f"获取查询模式连接错误: {e}")
            self.logger.test_fail(test_name, f"连接错误: {e}")
            return {
                "success": False,
                "error": f"连接错误: {e}"
            }
        except Exception as e:
            self.logger.debug(f"获取查询模式未知异常: {e}")
            self.logger.debug(f"异常类型: {type(e).__name__}")
            import traceback
            self.logger.debug(f"异常堆栈: {traceback.format_exc()}")
            self.logger.test_fail(test_name, str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_delete_category(self) -> Dict[str, Any]:
        """测试删除分类功能（包括文件夹删除）"""
        test_name = "Delete Category"
        self.logger.test_start(test_name)
        self.logger.debug(f"开始执行 {test_name}")

        try:
            # 首先创建一个测试分类的问答对
            create_url = self.get_url(API_ENDPOINTS["qa"]["pairs"])
            test_category = f"test_delete_{int(time.time())}"

            qa_data = self.utils.create_sample_qa_pair()
            qa_data["category"] = test_category

            self.logger.debug(f"创建测试分类问答对: {test_category}")
            self.logger.debug(f"问答对数据: {qa_data}")

            # 创建问答对
            headers = {"Content-Type": "application/json"}
            create_response = requests.post(create_url, json=qa_data, headers=headers, timeout=self.timeout)

            if create_response.status_code != 200:
                self.logger.debug(f"创建问答对失败: {create_response.text}")
                return {
                    "success": False,
                    "error": f"创建测试问答对失败: {create_response.status_code}",
                    "skipped": True,
                    "reason": "无法创建测试数据"
                }

            create_result = create_response.json()
            if not create_result.get("success"):
                self.logger.debug(f"创建问答对失败: {create_result}")
                return {
                    "success": False,
                    "error": f"创建测试问答对失败: {create_result.get('message')}",
                    "skipped": True,
                    "reason": "无法创建测试数据"
                }

            qa_id = create_result["data"]["qa_id"]
            self.logger.debug(f"成功创建测试问答对: {qa_id}")

            # 等待一下确保数据已保存
            time.sleep(1)

            # 现在删除分类
            delete_url = self.get_url(API_ENDPOINTS["qa"]["delete_category"].format(category=test_category))
            self.logger.debug(f"删除分类URL: {delete_url}")

            start_time = time.time()
            self.logger.debug(f"发送DELETE请求删除分类: {test_category}")
            response = requests.delete(delete_url, timeout=self.timeout)
            duration = time.time() - start_time

            # 记录响应信息
            self.logger.debug(f"响应状态码: {response.status_code}")
            self.logger.debug(f"响应头: {dict(response.headers)}")
            self.logger.debug(f"响应时间: {duration:.3f}秒")
            self.logger.debug(f"响应大小: {len(response.content)}字节")

            if response.status_code == 200:
                try:
                    data = response.json()
                    self.logger.debug(f"删除分类响应: {data}")

                    # 验证删除结果
                    if "success" in data:
                        self.logger.debug(f"删除成功状态: {data['success']}")
                    if "message" in data:
                        self.logger.debug(f"删除消息: {data['message']}")
                    if "data" in data:
                        delete_data = data["data"]
                        if "deleted_count" in delete_data:
                            self.logger.debug(f"删除的问答对数量: {delete_data['deleted_count']}")
                        if "category" in delete_data:
                            self.logger.debug(f"删除的分类: {delete_data['category']}")
                        if "folder_deleted" in delete_data:
                            folder_deleted = delete_data["folder_deleted"]
                            self.logger.debug(f"文件夹是否删除: {folder_deleted}")
                            if folder_deleted:
                                self.logger.debug("✅ 分类文件夹已成功删除")
                            else:
                                self.logger.debug("⚠️ 分类文件夹删除失败或不存在")

                    if data.get("success"):
                        self.logger.test_pass(test_name, duration)
                        return {
                            "success": True,
                            "duration": duration,
                            "status_code": response.status_code,
                            "data": data,
                            "test_category": test_category,
                            "created_qa_id": qa_id
                        }
                    else:
                        error_msg = data.get("message", "删除分类失败")
                        self.logger.debug(f"删除分类失败: {error_msg}")
                        self.logger.test_fail(test_name, error_msg, duration)
                        return {
                            "success": False,
                            "duration": duration,
                            "status_code": response.status_code,
                            "error": error_msg,
                            "test_category": test_category
                        }

                except json.JSONDecodeError as e:
                    self.logger.debug(f"JSON解析失败: {e}")
                    self.logger.debug(f"原始响应: {response.text[:500]}")
                    error_msg = f"JSON解析失败: {e}"
                    self.logger.test_fail(test_name, error_msg, duration)
                    return {
                        "success": False,
                        "duration": duration,
                        "status_code": response.status_code,
                        "error": error_msg
                    }
            else:
                error_msg = self.utils.extract_error_message(response)
                self.logger.debug(f"删除分类失败: {error_msg}")
                self.logger.debug(f"错误响应: {response.text[:500]}")
                self.logger.test_fail(test_name, error_msg, duration)
                return {
                    "success": False,
                    "duration": duration,
                    "status_code": response.status_code,
                    "error": error_msg,
                    "test_category": test_category
                }

        except requests.exceptions.Timeout as e:
            self.logger.debug(f"删除分类请求超时: {e}")
            self.logger.test_fail(test_name, f"请求超时: {e}")
            return {
                "success": False,
                "error": f"请求超时: {e}"
            }
        except requests.exceptions.ConnectionError as e:
            self.logger.debug(f"删除分类连接错误: {e}")
            self.logger.test_fail(test_name, f"连接错误: {e}")
            return {
                "success": False,
                "error": f"连接错误: {e}"
            }
        except Exception as e:
            self.logger.debug(f"删除分类未知异常: {e}")
            self.logger.debug(f"异常类型: {type(e).__name__}")
            import traceback
            self.logger.debug(f"异常堆栈: {traceback.format_exc()}")
            self.logger.test_fail(test_name, str(e))
            return {
                "success": False,
                "error": str(e)
            }

    def test_concurrency_control(self) -> Dict[str, Any]:
        """测试并发控制功能"""
        test_name = "Concurrency Control"
        self.logger.test_start(test_name)
        self.logger.debug(f"开始执行 {test_name}")

        try:
            import threading
            import concurrent.futures

            # 创建测试分类
            test_category = f"concurrency_test_{int(time.time())}"
            self.logger.debug(f"并发测试分类: {test_category}")

            # 准备并发操作
            create_url = self.get_url(API_ENDPOINTS["qa"]["pairs"])
            delete_url = self.get_url(API_ENDPOINTS["qa"]["delete_category"].format(category=test_category))

            results = []
            start_time = time.time()

            def create_qa_pair(index):
                """创建问答对的线程函数"""
                qa_data = {
                    "question": f"Concurrent test question {index}",
                    "answer": f"Concurrent test answer {index}",
                    "category": test_category,
                    "confidence": 0.9,
                    "keywords": [f"concurrent{index}"],
                    "source": "concurrency_test"
                }

                try:
                    response = requests.post(create_url, json=qa_data, headers={"Content-Type": "application/json"}, timeout=self.timeout)
                    if response.status_code == 200:
                        result = response.json()
                        return {
                            "operation": "create",
                            "index": index,
                            "success": result.get("success", False),
                            "qa_id": result.get("data", {}).get("qa_id"),
                            "thread_id": threading.current_thread().ident
                        }
                    else:
                        return {
                            "operation": "create",
                            "index": index,
                            "success": False,
                            "error": f"HTTP {response.status_code}",
                            "thread_id": threading.current_thread().ident
                        }
                except Exception as e:
                    return {
                        "operation": "create",
                        "index": index,
                        "success": False,
                        "error": str(e),
                        "thread_id": threading.current_thread().ident
                    }

            def delete_category():
                """删除分类的线程函数"""
                try:
                    response = requests.delete(delete_url, timeout=self.timeout)
                    if response.status_code == 200:
                        result = response.json()
                        return {
                            "operation": "delete",
                            "success": result.get("success", False),
                            "deleted_count": result.get("data", {}).get("deleted_count", 0),
                            "thread_id": threading.current_thread().ident
                        }
                    else:
                        return {
                            "operation": "delete",
                            "success": False,
                            "error": f"HTTP {response.status_code}",
                            "thread_id": threading.current_thread().ident
                        }
                except Exception as e:
                    return {
                        "operation": "delete",
                        "success": False,
                        "error": str(e),
                        "thread_id": threading.current_thread().ident
                    }

            # 使用线程池执行并发操作
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                futures = []

                # 提交创建任务
                for i in range(5):
                    future = executor.submit(create_qa_pair, i)
                    futures.append(future)

                # 提交删除任务
                for i in range(2):
                    future = executor.submit(delete_category)
                    futures.append(future)

                # 收集结果
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                        self.logger.debug(f"并发操作结果: {result}")
                    except Exception as e:
                        self.logger.debug(f"并发操作异常: {e}")
                        results.append({
                            "operation": "unknown",
                            "success": False,
                            "error": str(e)
                        })

            duration = time.time() - start_time

            # 分析结果
            create_results = [r for r in results if r["operation"] == "create"]
            delete_results = [r for r in results if r["operation"] == "delete"]

            create_success = len([r for r in create_results if r["success"]])
            delete_success = len([r for r in delete_results if r["success"]])

            self.logger.debug(f"并发测试结果:")
            self.logger.debug(f"  创建操作: {create_success}/{len(create_results)} 成功")
            self.logger.debug(f"  删除操作: {delete_success}/{len(delete_results)} 成功")
            self.logger.debug(f"  总耗时: {duration:.3f}秒")

            # 验证并发控制是否有效
            # 如果并发控制正常，应该不会出现数据竞争问题
            total_operations = len(results)
            successful_operations = len([r for r in results if r["success"]])

            if successful_operations > 0:
                self.logger.test_pass(test_name, duration)
                return {
                    "success": True,
                    "duration": duration,
                    "total_operations": total_operations,
                    "successful_operations": successful_operations,
                    "create_success": create_success,
                    "create_total": len(create_results),
                    "delete_success": delete_success,
                    "delete_total": len(delete_results),
                    "concurrency_results": results
                }
            else:
                error_msg = "所有并发操作都失败了"
                self.logger.test_fail(test_name, error_msg, duration)
                return {
                    "success": False,
                    "duration": duration,
                    "error": error_msg,
                    "concurrency_results": results
                }

        except ImportError as e:
            self.logger.debug(f"并发测试依赖缺失: {e}")
            self.logger.test_skip(test_name, "缺少并发测试依赖")
            return {
                "success": False,
                "skipped": True,
                "reason": f"缺少并发测试依赖: {e}"
            }
        except Exception as e:
            self.logger.debug(f"并发测试未知异常: {e}")
            self.logger.debug(f"异常类型: {type(e).__name__}")
            import traceback
            self.logger.debug(f"异常堆栈: {traceback.format_exc()}")
            self.logger.test_fail(test_name, str(e))
            return {
                "success": False,
                "error": str(e)
            }

    def test_qa_statistics(self) -> Dict[str, Any]:
        """测试QA统计"""
        test_name = "QA Statistics"
        self.logger.test_start(test_name)
        self.logger.debug(f"开始执行 {test_name}")

        try:
            # 构建请求URL
            url = self.get_url(API_ENDPOINTS["qa"]["statistics"])
            self.logger.debug(f"请求URL: {url}")

            # 发送请求
            start_time = time.time()
            self.logger.debug("发送GET请求获取QA统计信息...")
            response = requests.get(url, timeout=self.timeout)
            duration = time.time() - start_time

            # 记录响应信息
            self.logger.debug(f"响应状态码: {response.status_code}")
            self.logger.debug(f"响应头: {dict(response.headers)}")
            self.logger.debug(f"响应时间: {duration:.3f}秒")
            self.logger.debug(f"响应大小: {len(response.content)}字节")

            if response.status_code == 200:
                try:
                    data = response.json()
                    self.logger.debug(f"QA统计响应: {data}")

                    # 验证统计信息
                    if "success" in data:
                        self.logger.debug(f"获取成功状态: {data['success']}")
                    if "data" in data:
                        stats_data = data["data"]
                        if "total_pairs" in stats_data:
                            self.logger.debug(f"问答对总数: {stats_data['total_pairs']}")
                        if "categories" in stats_data:
                            categories = stats_data["categories"]
                            self.logger.debug(f"分类数量: {len(categories)}")
                            for category, count in categories.items():
                                self.logger.debug(f"分类 '{category}': {count}个问答对")
                        if "average_confidence" in stats_data:
                            self.logger.debug(f"平均置信度: {stats_data['average_confidence']:.3f}")
                        if "similarity_threshold" in stats_data:
                            self.logger.debug(f"相似度阈值: {stats_data['similarity_threshold']}")
                        if "vector_index_size" in stats_data:
                            self.logger.debug(f"向量索引大小: {stats_data['vector_index_size']}")
                        if "embedding_dim" in stats_data:
                            self.logger.debug(f"嵌入维度: {stats_data['embedding_dim']}")
                        if "query_stats" in stats_data:
                            query_stats = stats_data["query_stats"]
                            self.logger.debug(f"查询统计: 总查询={query_stats.get('total_queries', 0)}, "
                                            f"成功查询={query_stats.get('successful_queries', 0)}, "
                                            f"平均响应时间={query_stats.get('avg_response_time', 0)}秒")

                    self.logger.test_pass(test_name, duration)
                    return {
                        "success": True,
                        "duration": duration,
                        "status_code": response.status_code,
                        "data": data
                    }
                except json.JSONDecodeError as e:
                    self.logger.debug(f"JSON解析失败: {e}")
                    self.logger.debug(f"原始响应: {response.text[:500]}")
                    error_msg = f"JSON解析失败: {e}"
                    self.logger.test_fail(test_name, error_msg, duration)
                    return {
                        "success": False,
                        "duration": duration,
                        "status_code": response.status_code,
                        "error": error_msg
                    }
            else:
                error_msg = self.utils.extract_error_message(response)
                self.logger.debug(f"获取QA统计失败: {error_msg}")
                self.logger.debug(f"错误响应: {response.text[:500]}")
                self.logger.test_fail(test_name, error_msg, duration)
                return {
                    "success": False,
                    "duration": duration,
                    "status_code": response.status_code,
                    "error": error_msg
                }

        except requests.exceptions.Timeout as e:
            self.logger.debug(f"获取QA统计请求超时: {e}")
            self.logger.test_fail(test_name, f"请求超时: {e}")
            return {
                "success": False,
                "error": f"请求超时: {e}"
            }
        except requests.exceptions.ConnectionError as e:
            self.logger.debug(f"获取QA统计连接错误: {e}")
            self.logger.test_fail(test_name, f"连接错误: {e}")
            return {
                "success": False,
                "error": f"连接错误: {e}"
            }
        except Exception as e:
            self.logger.debug(f"获取QA统计未知异常: {e}")
            self.logger.debug(f"异常类型: {type(e).__name__}")
            import traceback
            self.logger.debug(f"异常堆栈: {traceback.format_exc()}")
            self.logger.test_fail(test_name, str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        self.logger.section("🚀 开始运行同步测试套件")
        self.logger.debug("初始化测试运行器...")
        self.logger.debug(f"基础URL: {self.base_url}")
        self.logger.debug(f"API前缀: {self.api_prefix}")
        self.logger.debug(f"超时设置: {self.timeout}秒")
        self.logger.debug(f"跳过文本插入: {self.skip_text_insert}")
        self.logger.debug(f"输出目录: {self.output_dir}")

        # 检查服务可用性
        self.logger.debug("检查服务可用性...")
        if not self.utils.wait_for_service(self.base_url):
            self.logger.error("❌ 服务不可用，无法运行测试")
            self.logger.debug(f"尝试连接的URL: {self.base_url}/api/v1/health")
            return {
                "success": False,
                "error": "服务不可用",
                "base_url": self.base_url
            }

        self.logger.debug("✅ 服务可用性检查通过")
        self.start_time = time.time()
        self.logger.debug(f"测试开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time))}")

        # 定义测试列表
        tests = [
            ("system_health", self.test_system_health_check, "系统健康检查"),
            ("qa_health", self.test_qa_health_check, "QA系统健康检查"),
            ("create_qa_pair", self.test_create_qa_pair, "创建问答对"),
            ("qa_query", self.test_qa_query, "QA查询"),
            ("delete_category", self.test_delete_category, "删除分类"),
            ("concurrency_test", self.test_concurrency_control, "并发控制测试"),
            ("insert_text", self.test_insert_text, "文本插入"),
            ("basic_query", self.test_basic_query, "基本查询"),
            ("query_modes", self.test_get_query_modes, "获取查询模式"),
            ("qa_statistics", self.test_qa_statistics, "QA统计信息")
        ]

        self.logger.debug(f"计划执行 {len(tests)} 个测试")
        for i, (test_key, _, test_desc) in enumerate(tests, 1):
            self.logger.debug(f"测试 {i}: {test_key} - {test_desc}")

        # 运行测试
        for i, (test_key, test_func, test_desc) in enumerate(tests, 1):
            self.logger.progress(i, len(tests), test_key)
            self.logger.debug(f"准备执行测试: {test_key} - {test_desc}")

            test_start_time = time.time()
            try:
                result = test_func()
                test_duration = time.time() - test_start_time
                self.results[test_key] = result

                # 记录测试结果详情
                if result.get("success", False):
                    self.logger.debug(f"测试 {test_key} 成功完成，耗时: {test_duration:.3f}秒")
                elif result.get("skipped", False):
                    self.logger.debug(f"测试 {test_key} 被跳过: {result.get('reason', '未知原因')}")
                else:
                    self.logger.debug(f"测试 {test_key} 失败，耗时: {test_duration:.3f}秒，错误: {result.get('error', '未知错误')}")

            except Exception as e:
                test_duration = time.time() - test_start_time
                self.logger.error(f"测试 {test_key} 执行异常: {e}")
                self.logger.debug(f"异常详情: {type(e).__name__}: {e}")
                import traceback
                self.logger.debug(f"异常堆栈: {traceback.format_exc()}")

                self.results[test_key] = {
                    "success": False,
                    "error": str(e),
                    "duration": test_duration,
                    "exception_type": type(e).__name__
                }

        self.end_time = time.time()
        total_duration = self.end_time - self.start_time
        self.logger.debug(f"测试结束时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.end_time))}")
        self.logger.debug(f"总测试耗时: {total_duration:.3f}秒")

        # 生成摘要
        self.logger.debug("生成测试摘要...")
        summary = self._generate_summary()
        self.logger.debug(f"测试摘要: {summary}")

        # 保存结果
        self.logger.debug("准备保存测试结果...")
        final_results = {
            "timestamp": self.utils.generate_timestamp(),
            "test_type": "sync_http_test",
            "base_url": self.base_url,
            "timeout": self.timeout,
            "skip_text_insert": self.skip_text_insert,
            "duration": total_duration,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "summary": summary,
            "results": self.results,
            "test_environment": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": os.getcwd()
            }
        }

        # 保存到文件
        result_file = self.utils.save_test_results(
            final_results,
            self.output_dir,
            f"sync_test_{self.utils.generate_timestamp()}.json"
        )

        self.logger.info(f"📄 测试结果已保存: {result_file}")
        self.logger.debug(f"结果文件大小: {result_file.stat().st_size}字节")

        # 输出摘要
        self.logger.summary(
            summary["total"],
            summary["passed"],
            summary["failed"],
            summary["skipped"]
        )

        self.logger.debug("测试套件执行完成")
        return final_results
    
    def _generate_summary(self) -> Dict[str, Any]:
        """生成测试摘要"""
        total = len(self.results)
        passed = sum(1 for r in self.results.values() if r.get("success", False))
        skipped = sum(1 for r in self.results.values() if r.get("skipped", False))
        failed = total - passed - skipped
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "success_rate": passed / total if total > 0 else 0
        }
