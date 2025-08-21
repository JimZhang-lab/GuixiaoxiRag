"""
性能测试
测试系统的性能指标，包括响应时间、吞吐量、并发处理能力等
"""

import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any, Tuple
from conftest import TestClient, TestUtils, API_ENDPOINTS


class PerformanceMetrics:
    """性能指标收集器"""
    
    def __init__(self):
        self.response_times = []
        self.success_count = 0
        self.error_count = 0
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """开始计时"""
        self.start_time = time.time()
    
    def end(self):
        """结束计时"""
        self.end_time = time.time()
    
    def add_response(self, response_time: float, success: bool):
        """添加响应记录"""
        self.response_times.append(response_time)
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.response_times:
            return {"error": "No data collected"}
        
        total_time = self.end_time - self.start_time if self.end_time and self.start_time else 0
        total_requests = len(self.response_times)
        
        return {
            "total_requests": total_requests,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_count / total_requests if total_requests > 0 else 0,
            "total_time": total_time,
            "requests_per_second": total_requests / total_time if total_time > 0 else 0,
            "avg_response_time": statistics.mean(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
            "median_response_time": statistics.median(self.response_times),
            "p95_response_time": self._percentile(self.response_times, 95),
            "p99_response_time": self._percentile(self.response_times, 99)
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


class TestPerformance:
    """性能测试类"""
    
    @pytest.mark.asyncio
    async def test_health_check_performance(self, test_client: TestClient, test_utils: TestUtils):
        """测试健康检查接口性能"""
        metrics = PerformanceMetrics()
        metrics.start()
        
        # 连续发送100个健康检查请求
        for _ in range(100):
            start_time = time.time()
            response = await test_client.get(API_ENDPOINTS["system"]["health"])
            end_time = time.time()
            
            response_time = end_time - start_time
            success = response.status_code == 200
            metrics.add_response(response_time, success)
        
        metrics.end()
        stats = metrics.get_stats()
        
        print(f"健康检查性能统计:")
        print(f"  总请求数: {stats['total_requests']}")
        print(f"  成功率: {stats['success_rate']:.2%}")
        print(f"  QPS: {stats['requests_per_second']:.2f}")
        print(f"  平均响应时间: {stats['avg_response_time']:.3f}s")
        print(f"  P95响应时间: {stats['p95_response_time']:.3f}s")
        print(f"  P99响应时间: {stats['p99_response_time']:.3f}s")
        
        # 性能断言
        assert stats['success_rate'] >= 0.95, f"成功率过低: {stats['success_rate']:.2%}"
        assert stats['avg_response_time'] <= 1.0, f"平均响应时间过长: {stats['avg_response_time']:.3f}s"
        assert stats['p95_response_time'] <= 2.0, f"P95响应时间过长: {stats['p95_response_time']:.3f}s"
    
    @pytest.mark.asyncio
    async def test_query_performance(self, test_client: TestClient, test_utils: TestUtils):
        """测试查询接口性能"""
        # 先插入一些测试数据
        test_doc = {
            "text": "人工智能是计算机科学的一个分支，致力于创建智能系统。AI包括机器学习、深度学习、自然语言处理等技术。",
            "knowledge_base": "test_kb",
            "language": "中文"
        }
        
        doc_response = await test_client.post(API_ENDPOINTS["document"]["insert_text"], json_data=test_doc)
        test_utils.assert_response_success(doc_response)
        
        # 等待文档处理
        await asyncio.sleep(2)
        
        # 测试查询性能
        metrics = PerformanceMetrics()
        metrics.start()
        
        queries = [
            "什么是人工智能？",
            "机器学习的应用？",
            "深度学习技术？",
            "自然语言处理？",
            "AI的发展趋势？"
        ]
        
        # 每个查询执行10次
        for query in queries:
            for _ in range(10):
                query_request = {
                    "query": query,
                    "mode": "hybrid",
                    "top_k": 5
                }
                
                start_time = time.time()
                response = await test_client.post(API_ENDPOINTS["query"]["query"], json_data=query_request)
                end_time = time.time()
                
                response_time = end_time - start_time
                success = response.status_code == 200
                metrics.add_response(response_time, success)
        
        metrics.end()
        stats = metrics.get_stats()
        
        print(f"查询性能统计:")
        print(f"  总请求数: {stats['total_requests']}")
        print(f"  成功率: {stats['success_rate']:.2%}")
        print(f"  QPS: {stats['requests_per_second']:.2f}")
        print(f"  平均响应时间: {stats['avg_response_time']:.3f}s")
        print(f"  P95响应时间: {stats['p95_response_time']:.3f}s")
        
        # 查询性能断言（相对宽松，因为涉及AI推理）
        assert stats['success_rate'] >= 0.8, f"查询成功率过低: {stats['success_rate']:.2%}"
        assert stats['avg_response_time'] <= 10.0, f"查询平均响应时间过长: {stats['avg_response_time']:.3f}s"
    
    @pytest.mark.asyncio
    async def test_concurrent_performance(self, test_client: TestClient, test_utils: TestUtils):
        """测试并发性能"""
        
        async def single_request():
            """单个请求"""
            start_time = time.time()
            response = await test_client.get(API_ENDPOINTS["system"]["health"])
            end_time = time.time()
            return end_time - start_time, response.status_code == 200
        
        # 测试不同并发级别
        concurrency_levels = [1, 5, 10, 20]
        
        for concurrency in concurrency_levels:
            print(f"\n测试并发级别: {concurrency}")
            
            metrics = PerformanceMetrics()
            metrics.start()
            
            # 创建并发任务
            tasks = [single_request() for _ in range(concurrency * 10)]  # 每个并发级别10个请求
            
            # 执行并发请求
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            metrics.end()
            
            # 收集结果
            for result in results:
                if isinstance(result, Exception):
                    metrics.add_response(0, False)
                else:
                    response_time, success = result
                    metrics.add_response(response_time, success)
            
            stats = metrics.get_stats()
            
            print(f"  并发{concurrency}: QPS={stats['requests_per_second']:.2f}, "
                  f"成功率={stats['success_rate']:.2%}, "
                  f"平均响应时间={stats['avg_response_time']:.3f}s")
            
            # 并发性能断言
            assert stats['success_rate'] >= 0.8, f"并发{concurrency}成功率过低: {stats['success_rate']:.2%}"
    
    @pytest.mark.asyncio
    async def test_batch_processing_performance(self, test_client: TestClient, test_utils: TestUtils):
        """测试批量处理性能"""
        
        # 测试批量查询性能
        queries = [f"测试查询{i}" for i in range(20)]
        
        # 单个查询的总时间
        single_start = time.time()
        for query in queries:
            query_request = {
                "query": query,
                "mode": "hybrid",
                "top_k": 3
            }
            await test_client.post(API_ENDPOINTS["query"]["query"], json_data=query_request)
        single_end = time.time()
        single_total_time = single_end - single_start
        
        # 批量查询时间
        batch_start = time.time()
        batch_request = {
            "queries": queries,
            "mode": "hybrid",
            "top_k": 3,
            "parallel": True
        }
        batch_response = await test_client.post(API_ENDPOINTS["query"]["batch"], json_data=batch_request)
        batch_end = time.time()
        batch_total_time = batch_end - batch_start
        
        print(f"批量处理性能对比:")
        print(f"  单个查询总时间: {single_total_time:.3f}s")
        print(f"  批量查询总时间: {batch_total_time:.3f}s")
        
        if batch_response.status_code == 200:
            speedup = single_total_time / batch_total_time
            print(f"  性能提升: {speedup:.2f}x")
            
            # 批量处理应该有性能提升
            assert speedup > 1.0, f"批量处理没有性能提升: {speedup:.2f}x"
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, test_client: TestClient, test_utils: TestUtils):
        """测试内存使用稳定性"""
        
        # 获取初始系统状态
        initial_response = await test_client.get(API_ENDPOINTS["system"]["metrics"])
        if initial_response.status_code != 200:
            pytest.skip("系统指标接口不可用")
        
        initial_data = initial_response.json().get("data", {})
        initial_memory = initial_data.get("memory_usage", 0)
        
        # 执行大量操作
        for i in range(100):
            # 插入文档
            doc_data = {
                "text": f"内存测试文档{i}，包含一些测试内容" * 10,  # 增加内容长度
                "doc_id": f"memory_test_{i}",
                "knowledge_base": "test_kb"
            }
            await test_client.post(API_ENDPOINTS["document"]["insert_text"], json_data=doc_data)
            
            # 执行查询
            if i % 10 == 0:
                query_request = {
                    "query": f"内存测试查询{i}",
                    "mode": "hybrid",
                    "top_k": 5
                }
                await test_client.post(API_ENDPOINTS["query"]["query"], json_data=query_request)
        
        # 获取最终系统状态
        final_response = await test_client.get(API_ENDPOINTS["system"]["metrics"])
        if final_response.status_code == 200:
            final_data = final_response.json().get("data", {})
            final_memory = final_data.get("memory_usage", 0)
            
            if initial_memory > 0 and final_memory > 0:
                memory_increase = (final_memory - initial_memory) / initial_memory
                print(f"内存使用变化: {memory_increase:.2%}")
                
                # 内存增长应该在合理范围内
                assert memory_increase < 2.0, f"内存增长过多: {memory_increase:.2%}"
    
    @pytest.mark.asyncio
    async def test_response_time_consistency(self, test_client: TestClient, test_utils: TestUtils):
        """测试响应时间一致性"""
        
        response_times = []
        
        # 连续发送相同请求，测试响应时间稳定性
        for _ in range(50):
            start_time = time.time()
            response = await test_client.get(API_ENDPOINTS["system"]["health"])
            end_time = time.time()
            
            if response.status_code == 200:
                response_times.append(end_time - start_time)
        
        if len(response_times) >= 10:
            avg_time = statistics.mean(response_times)
            std_dev = statistics.stdev(response_times)
            cv = std_dev / avg_time  # 变异系数
            
            print(f"响应时间一致性:")
            print(f"  平均响应时间: {avg_time:.3f}s")
            print(f"  标准差: {std_dev:.3f}s")
            print(f"  变异系数: {cv:.3f}")
            
            # 响应时间应该相对稳定
            assert cv < 1.0, f"响应时间变异过大: {cv:.3f}"


class TestStressTest:
    """压力测试类"""
    
    @pytest.mark.asyncio
    async def test_sustained_load(self, test_client: TestClient, test_utils: TestUtils):
        """测试持续负载"""
        
        duration = 30  # 30秒持续负载
        start_time = time.time()
        
        metrics = PerformanceMetrics()
        metrics.start()
        
        async def continuous_requests():
            """持续发送请求"""
            while time.time() - start_time < duration:
                request_start = time.time()
                try:
                    response = await test_client.get(API_ENDPOINTS["system"]["health"])
                    request_end = time.time()
                    
                    response_time = request_end - request_start
                    success = response.status_code == 200
                    metrics.add_response(response_time, success)
                    
                except Exception as e:
                    request_end = time.time()
                    response_time = request_end - request_start
                    metrics.add_response(response_time, False)
                
                # 短暂延迟避免过度负载
                await asyncio.sleep(0.01)
        
        # 启动多个并发任务
        tasks = [continuous_requests() for _ in range(5)]
        await asyncio.gather(*tasks)
        
        metrics.end()
        stats = metrics.get_stats()
        
        print(f"持续负载测试结果 ({duration}秒):")
        print(f"  总请求数: {stats['total_requests']}")
        print(f"  成功率: {stats['success_rate']:.2%}")
        print(f"  平均QPS: {stats['requests_per_second']:.2f}")
        print(f"  平均响应时间: {stats['avg_response_time']:.3f}s")
        
        # 持续负载下的性能要求
        assert stats['success_rate'] >= 0.9, f"持续负载下成功率过低: {stats['success_rate']:.2%}"
        assert stats['avg_response_time'] <= 2.0, f"持续负载下响应时间过长: {stats['avg_response_time']:.3f}s"
    
    @pytest.mark.asyncio
    async def test_peak_load_handling(self, test_client: TestClient, test_utils: TestUtils):
        """测试峰值负载处理"""
        
        # 突发大量并发请求
        concurrent_requests = 50
        
        async def burst_request():
            """突发请求"""
            start_time = time.time()
            try:
                response = await test_client.get(API_ENDPOINTS["system"]["health"])
                end_time = time.time()
                return end_time - start_time, response.status_code == 200
            except Exception:
                end_time = time.time()
                return end_time - start_time, False
        
        # 创建大量并发任务
        tasks = [burst_request() for _ in range(concurrent_requests)]
        
        burst_start = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        burst_end = time.time()
        
        # 统计结果
        success_count = 0
        total_response_time = 0
        valid_results = 0
        
        for result in results:
            if isinstance(result, Exception):
                continue
            
            response_time, success = result
            total_response_time += response_time
            valid_results += 1
            if success:
                success_count += 1
        
        if valid_results > 0:
            success_rate = success_count / valid_results
            avg_response_time = total_response_time / valid_results
            total_time = burst_end - burst_start
            qps = concurrent_requests / total_time
            
            print(f"峰值负载测试结果 ({concurrent_requests}并发):")
            print(f"  成功率: {success_rate:.2%}")
            print(f"  平均响应时间: {avg_response_time:.3f}s")
            print(f"  峰值QPS: {qps:.2f}")
            
            # 峰值负载下的最低要求
            assert success_rate >= 0.7, f"峰值负载下成功率过低: {success_rate:.2%}"
