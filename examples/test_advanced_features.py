#!/usr/bin/env python3
"""
测试高级功能的脚本
"""
import asyncio
import httpx
import json
import time


async def test_knowledge_base_management():
    """测试知识库管理功能"""
    base_url = "http://localhost:8002"
    
    print("🗄️ 测试知识库管理功能")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=30) as client:
        
        # 1. 列出知识库
        print("1. 列出所有知识库...")
        response = await client.get(f"{base_url}/knowledge-bases")
        if response.status_code == 200:
            data = response.json()['data']
            print(f"   ✅ 找到 {data['total']} 个知识库")
            print(f"   📊 当前知识库: {data['current']}")
            for kb in data['knowledge_bases']:
                print(f"   📁 {kb['name']}: {kb['document_count']}文档, {kb['node_count']}节点")
        else:
            print(f"   ❌ 失败: {response.status_code}")
        
        # 2. 创建新知识库
        print(f"\n2. 创建新知识库...")
        kb_name = f"test_advanced_{int(time.time())}"
        response = await client.post(
            f"{base_url}/knowledge-bases",
            json={
                "name": kb_name,
                "description": "高级功能测试知识库"
            }
        )
        if response.status_code == 200:
            print(f"   ✅ 知识库 '{kb_name}' 创建成功")
        else:
            print(f"   ❌ 创建失败: {response.status_code}")
            return
        
        # 3. 切换知识库
        print(f"\n3. 切换到新知识库...")
        response = await client.post(
            f"{base_url}/knowledge-bases/switch",
            json={"name": kb_name}
        )
        if response.status_code == 200:
            print(f"   ✅ 成功切换到 '{kb_name}'")
        else:
            print(f"   ❌ 切换失败: {response.status_code}")
        
        # 4. 在新知识库中插入数据
        print(f"\n4. 在新知识库中插入测试数据...")
        test_data = {
            "text": "这是在新知识库中的测试数据。包含了关于高级功能测试的信息。",
            "doc_id": "advanced_test_1"
        }
        response = await client.post(f"{base_url}/insert/text", json=test_data)
        if response.status_code == 200:
            print(f"   ✅ 数据插入成功")
        else:
            print(f"   ❌ 插入失败: {response.status_code}")
        
        # 5. 导出知识库
        print(f"\n5. 导出知识库...")
        response = await client.get(f"{base_url}/knowledge-bases/{kb_name}/export")
        if response.status_code == 200:
            export_data = response.json()['data']
            print(f"   ✅ 导出成功")
            print(f"   📊 文档数量: {len(export_data.get('documents', []))}")
        else:
            print(f"   ❌ 导出失败: {response.status_code}")


async def test_performance_optimization():
    """测试性能优化功能"""
    base_url = "http://localhost:8002"
    
    print(f"\n⚡ 测试性能优化功能")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=60) as client:
        
        # 1. 获取性能配置
        print("1. 获取性能配置选项...")
        response = await client.get(f"{base_url}/performance/configs")
        if response.status_code == 200:
            configs = response.json()['data']['configs']
            print(f"   ✅ 获取成功")
            for mode, config in configs.items():
                print(f"   🔧 {mode}: embedding_dim={config['embedding_dim']}")
        else:
            print(f"   ❌ 获取失败: {response.status_code}")
        
        # 2. 测试优化查询
        print(f"\n2. 测试优化查询...")
        
        test_queries = [
            {
                "name": "快速模式",
                "data": {
                    "query": "什么是高级功能测试？",
                    "mode": "hybrid",
                    "performance_level": "fast"
                }
            },
            {
                "name": "平衡模式",
                "data": {
                    "query": "测试数据包含什么信息？",
                    "mode": "local",
                    "performance_level": "balanced"
                }
            }
        ]
        
        for test_query in test_queries:
            print(f"\n   测试{test_query['name']}...")
            start_time = time.time()
            
            response = await client.post(
                f"{base_url}/query/optimized",
                json=test_query['data']
            )
            
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()['data']
                print(f"   ✅ 查询成功")
                print(f"   ⏱️ 处理时间: {end_time - start_time:.2f}秒")
                print(f"   🎯 性能级别: {result['performance_level']}")
                print(f"   📝 结果预览: {result['result'][:100]}...")
            else:
                print(f"   ❌ 查询失败: {response.status_code}")


async def test_monitoring_features():
    """测试监控功能"""
    base_url = "http://localhost:8002"
    
    print(f"\n📊 测试监控功能")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=30) as client:
        
        # 1. 获取系统指标
        print("1. 获取系统性能指标...")
        response = await client.get(f"{base_url}/metrics")
        if response.status_code == 200:
            metrics = response.json()['data']
            print(f"   ✅ 指标获取成功")
            print(f"   📈 总请求数: {metrics['total_requests']}")
            print(f"   ⚠️ 错误数: {metrics['total_errors']}")
            print(f"   ⏱️ 平均响应时间: {metrics['average_response_time']:.3f}秒")
            print(f"   📊 错误率: {metrics['error_rate']:.2%}")
        else:
            print(f"   ❌ 获取失败: {response.status_code}")
        
        # 2. 获取系统状态
        print(f"\n2. 获取详细系统状态...")
        response = await client.get(f"{base_url}/system/status")
        if response.status_code == 200:
            status = response.json()['data']
            print(f"   ✅ 状态获取成功")
            print(f"   🚀 服务: {status['service_name']}")
            print(f"   📦 版本: {status['version']}")
            print(f"   🕐 运行时间: {status['uptime']:.1f}秒")
            print(f"   ⚙️ 配置: {status['config']['openai_chat_model']}")
        else:
            print(f"   ❌ 获取失败: {response.status_code}")
        
        # 3. 获取知识图谱统计
        print(f"\n3. 获取知识图谱统计...")
        response = await client.get(f"{base_url}/knowledge-graph/stats")
        if response.status_code == 200:
            stats = response.json()['data']
            print(f"   ✅ 统计获取成功")
            print(f"   📊 节点数: {stats['total_nodes']}")
            print(f"   🔗 边数: {stats['total_edges']}")
            print(f"   💾 存储类型: {stats['graph_type']}")
        else:
            print(f"   ❌ 获取失败: {response.status_code}")


async def test_api_documentation():
    """测试API文档访问"""
    base_url = "http://localhost:8002"
    
    print(f"\n📖 测试API文档")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=30) as client:
        
        # 1. 测试Swagger文档
        print("1. 测试Swagger UI文档...")
        response = await client.get(f"{base_url}/docs")
        if response.status_code == 200:
            print(f"   ✅ Swagger文档可访问")
            print(f"   🌐 地址: {base_url}/docs")
        else:
            print(f"   ❌ 访问失败: {response.status_code}")
        
        # 2. 测试OpenAPI规范
        print(f"\n2. 测试OpenAPI规范...")
        response = await client.get(f"{base_url}/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            print(f"   ✅ OpenAPI规范可访问")
            print(f"   📋 API数量: {len(openapi_spec.get('paths', {}))}")
            print(f"   📦 版本: {openapi_spec.get('info', {}).get('version', 'unknown')}")
        else:
            print(f"   ❌ 访问失败: {response.status_code}")


async def main():
    """主函数"""
    print("🚀 GuiXiaoXiRag FastAPI 高级功能测试")
    print("=" * 60)
    
    try:
        # 测试知识库管理
        await test_knowledge_base_management()
        
        # 等待一段时间
        await asyncio.sleep(2)
        
        # 测试性能优化
        await test_performance_optimization()
        
        # 测试监控功能
        await test_monitoring_features()
        
        # 测试API文档
        await test_api_documentation()
        
        print(f"\n🎉 所有高级功能测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
