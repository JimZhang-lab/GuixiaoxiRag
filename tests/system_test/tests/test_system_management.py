"""
系统管理测试
测试系统管理的所有功能，包括健康检查、配置管理、性能监控等
"""

import pytest
import asyncio
import json
from typing import Dict, Any
from conftest import TestClient, TestUtils, API_ENDPOINTS


class TestSystemManagement:
    """系统管理测试类"""
    
    @pytest.mark.asyncio
    async def test_system_health_check(self, test_client: TestClient, test_utils: TestUtils):
        """测试系统健康检查"""
        response = await test_client.get(API_ENDPOINTS["system"]["health"])
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy", "initializing", "shutting_down"]
        assert "timestamp" in data
        
        if "system" in data:
            system_info = data["system"]
            # 检查系统信息字段
            expected_fields = ["cpu_usage", "memory_usage", "disk_usage"]
            for field in expected_fields:
                if field in system_info:
                    assert isinstance(system_info[field], (int, float))
    
    @pytest.mark.asyncio
    async def test_system_status(self, test_client: TestClient, test_utils: TestUtils):
        """测试系统状态获取"""
        response = await test_client.get(API_ENDPOINTS["system"]["status"])
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "data" in data
        status_data = data["data"]
        
        # 检查基本状态信息
        expected_fields = ["uptime", "version", "environment"]
        for field in expected_fields:
            if field in status_data:
                assert status_data[field] is not None
    
    @pytest.mark.asyncio
    async def test_system_metrics(self, test_client: TestClient, test_utils: TestUtils):
        """测试系统指标获取"""
        response = await test_client.get(API_ENDPOINTS["system"]["metrics"])
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "data" in data
        metrics_data = data["data"]
        
        # 检查指标数据
        if "performance" in metrics_data:
            perf_data = metrics_data["performance"]
            metric_fields = ["response_time", "throughput", "error_rate"]
            for field in metric_fields:
                if field in perf_data:
                    assert isinstance(perf_data[field], (int, float))
    
    @pytest.mark.asyncio
    async def test_get_logs(self, test_client: TestClient, test_utils: TestUtils):
        """测试获取系统日志"""
        # 测试基本日志获取
        response = await test_client.get(API_ENDPOINTS["system"]["logs"])
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "data" in data
        
        # 测试带参数的日志获取
        params = {
            "level": "INFO",
            "limit": 100,
            "start_time": "2024-01-01T00:00:00Z"
        }
        response = await test_client.get(API_ENDPOINTS["system"]["logs"], params=params)
        test_utils.assert_response_success(response)
    
    @pytest.mark.asyncio
    async def test_get_service_config(self, test_client: TestClient, test_utils: TestUtils):
        """测试获取服务配置"""
        response = await test_client.get(API_ENDPOINTS["system"]["config"])
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "data" in data
        config_data = data["data"]
        
        # 配置应该是字典格式
        assert isinstance(config_data, dict)
    
    @pytest.mark.asyncio
    async def test_get_effective_config(self, test_client: TestClient, test_utils: TestUtils):
        """测试获取有效配置"""
        response = await test_client.get(API_ENDPOINTS["system"]["effective_config"])
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "data" in data
        config_data = data["data"]
        
        # 有效配置应该包含实际使用的配置值
        assert isinstance(config_data, dict)
    
    @pytest.mark.asyncio
    async def test_update_config(self, test_client: TestClient, test_utils: TestUtils):
        """测试更新配置"""
        # 先获取当前配置
        get_response = await test_client.get(API_ENDPOINTS["system"]["config"])
        test_utils.assert_response_success(get_response)
        
        current_config = get_response.json()["data"]
        
        # 准备更新配置（只更新安全的配置项）
        update_config = {
            "log_level": "INFO",
            "max_query_length": 2000,
            "enable_debug": False
        }
        
        response = await test_client.put(API_ENDPOINTS["system"]["update_config"], json_data=update_config)
        # 配置更新可能需要特殊权限
        assert response.status_code in [200, 403, 501]
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
    
    @pytest.mark.asyncio
    async def test_system_reset_validation(self, test_client: TestClient, test_utils: TestUtils):
        """测试系统重置参数验证（不实际执行重置）"""
        # 测试缺少确认参数
        reset_request = {
            "backup_data": True,
            "reset_config": False
        }
        
        response = await test_client.post(API_ENDPOINTS["system"]["reset"], json_data=reset_request)
        test_utils.assert_response_error(response, 400)
        
        # 测试错误的确认参数
        reset_request = {
            "confirm": False,
            "backup_data": True
        }
        
        response = await test_client.post(API_ENDPOINTS["system"]["reset"], json_data=reset_request)
        test_utils.assert_response_error(response, 400)
    
    @pytest.mark.asyncio
    async def test_system_monitoring_endpoints(self, test_client: TestClient, test_utils: TestUtils):
        """测试系统监控相关端点"""
        monitoring_endpoints = [
            "/health",
            "/system/status", 
            "/metrics"
        ]
        
        for endpoint in monitoring_endpoints:
            response = await test_client.get(endpoint)
            # 监控端点应该始终可用
            assert response.status_code in [200, 404], f"Monitoring endpoint {endpoint} failed"
            
            if response.status_code == 200:
                # 检查响应格式
                content_type = response.headers.get("content-type", "")
                assert "application/json" in content_type
    
    @pytest.mark.asyncio
    async def test_service_dependencies_check(self, test_client: TestClient, test_utils: TestUtils):
        """测试服务依赖检查"""
        response = await test_client.get(API_ENDPOINTS["system"]["health"])
        test_utils.assert_response_success(response)
        
        data = response.json()
        
        if "dependencies" in data:
            deps = data["dependencies"]
            assert isinstance(deps, dict)
            
            # 检查常见的依赖服务
            common_deps = ["database", "llm_service", "embedding_service", "vector_db"]
            for dep in common_deps:
                if dep in deps:
                    assert deps[dep] in ["healthy", "degraded", "unhealthy"]
    
    @pytest.mark.asyncio
    async def test_performance_metrics_collection(self, test_client: TestClient, test_utils: TestUtils):
        """测试性能指标收集"""
        # 执行一些操作来生成指标
        test_operations = [
            ("GET", API_ENDPOINTS["system"]["health"]),
            ("GET", API_ENDPOINTS["system"]["status"]),
            ("GET", API_ENDPOINTS["system"]["metrics"])
        ]
        
        for method, endpoint in test_operations:
            if method == "GET":
                await test_client.get(endpoint)
        
        # 获取指标
        response = await test_client.get(API_ENDPOINTS["system"]["metrics"])
        test_utils.assert_response_success(response)
        
        data = response.json()
        metrics_data = data["data"]
        
        # 检查是否有请求计数等指标
        if "requests" in metrics_data:
            requests_data = metrics_data["requests"]
            assert isinstance(requests_data, dict)


class TestSystemSecurity:
    """系统安全测试"""
    
    @pytest.mark.asyncio
    async def test_config_access_control(self, test_client: TestClient, test_utils: TestUtils):
        """测试配置访问控制"""
        # 尝试访问敏感配置
        response = await test_client.get(API_ENDPOINTS["system"]["config"])
        
        if response.status_code == 200:
            data = response.json()["data"]
            
            # 检查是否过滤了敏感信息
            sensitive_keys = ["password", "secret", "key", "token", "credential"]
            for key in data:
                key_lower = key.lower()
                for sensitive in sensitive_keys:
                    if sensitive in key_lower:
                        # 敏感信息应该被隐藏或加密
                        value = data[key]
                        if isinstance(value, str):
                            assert "*" in value or "***" in value or len(value) == 0
    
    @pytest.mark.asyncio
    async def test_system_reset_security(self, test_client: TestClient, test_utils: TestUtils):
        """测试系统重置安全性"""
        # 尝试不带确认的重置
        reset_request = {
            "backup_data": True
        }
        
        response = await test_client.post(API_ENDPOINTS["system"]["reset"], json_data=reset_request)
        test_utils.assert_response_error(response, 400)
        
        # 尝试带错误确认的重置
        reset_request = {
            "confirm": "yes",  # 应该是布尔值
            "backup_data": True
        }
        
        response = await test_client.post(API_ENDPOINTS["system"]["reset"], json_data=reset_request)
        test_utils.assert_response_error(response, 422)
    
    @pytest.mark.asyncio
    async def test_log_access_security(self, test_client: TestClient, test_utils: TestUtils):
        """测试日志访问安全性"""
        # 尝试访问系统日志
        response = await test_client.get(API_ENDPOINTS["system"]["logs"])
        
        if response.status_code == 200:
            data = response.json()["data"]
            
            # 检查日志是否包含敏感信息
            if "logs" in data:
                logs = data["logs"]
                for log_entry in logs[:10]:  # 检查前10条
                    if isinstance(log_entry, dict) and "message" in log_entry:
                        message = log_entry["message"].lower()
                        # 确保没有密码等敏感信息
                        sensitive_patterns = ["password=", "secret=", "token="]
                        for pattern in sensitive_patterns:
                            assert pattern not in message


class TestSystemEdgeCases:
    """系统管理边界情况测试"""
    
    @pytest.mark.asyncio
    async def test_high_frequency_health_checks(self, test_client: TestClient, test_utils: TestUtils):
        """测试高频健康检查"""
        # 快速连续发送多个健康检查请求
        tasks = []
        for _ in range(10):
            task = test_client.get(API_ENDPOINTS["system"]["health"])
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = 0
        for response in responses:
            if not isinstance(response, Exception) and response.status_code == 200:
                success_count += 1
        
        # 大部分请求应该成功
        assert success_count >= 8, f"只有 {success_count}/10 个健康检查成功"
    
    @pytest.mark.asyncio
    async def test_invalid_log_parameters(self, test_client: TestClient, test_utils: TestUtils):
        """测试无效的日志参数"""
        invalid_params = [
            {"level": "INVALID_LEVEL"},
            {"limit": -1},
            {"limit": 0},
            {"start_time": "invalid_date"},
            {"end_time": "2023-13-45T25:70:80Z"}  # 无效日期
        ]
        
        for params in invalid_params:
            response = await test_client.get(API_ENDPOINTS["system"]["logs"], params=params)
            # 应该返回错误或忽略无效参数
            assert response.status_code in [200, 400, 422]
    
    @pytest.mark.asyncio
    async def test_config_update_validation(self, test_client: TestClient, test_utils: TestUtils):
        """测试配置更新验证"""
        invalid_configs = [
            {"invalid_key": "value"},
            {"log_level": "INVALID_LEVEL"},
            {"max_query_length": -1},
            {"timeout": "not_a_number"}
        ]
        
        for config in invalid_configs:
            response = await test_client.put(API_ENDPOINTS["system"]["update_config"], json_data=config)
            # 应该拒绝无效配置
            assert response.status_code in [400, 422, 403, 501]
    
    @pytest.mark.asyncio
    async def test_system_under_load(self, test_client: TestClient, test_utils: TestUtils):
        """测试系统负载情况"""
        # 同时发送多种类型的请求
        tasks = []
        
        # 健康检查
        for _ in range(5):
            tasks.append(test_client.get(API_ENDPOINTS["system"]["health"]))
        
        # 状态查询
        for _ in range(3):
            tasks.append(test_client.get(API_ENDPOINTS["system"]["status"]))
        
        # 指标查询
        for _ in range(2):
            tasks.append(test_client.get(API_ENDPOINTS["system"]["metrics"]))
        
        # 执行所有请求
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 统计结果
        success_count = 0
        error_count = 0
        exception_count = 0
        
        for response in responses:
            if isinstance(response, Exception):
                exception_count += 1
            elif response.status_code == 200:
                success_count += 1
            else:
                error_count += 1
        
        print(f"负载测试结果: 成功={success_count}, 错误={error_count}, 异常={exception_count}")
        
        # 在负载情况下，大部分请求应该仍然成功
        total_requests = len(tasks)
        success_rate = success_count / total_requests
        assert success_rate >= 0.7, f"成功率过低: {success_rate:.2%}"
