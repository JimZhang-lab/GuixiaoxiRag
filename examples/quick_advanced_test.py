#!/usr/bin/env python3
"""
快速高级功能测试
"""
import asyncio
import httpx
import json


async def quick_test():
    """快速测试主要高级功能"""
    base_url = "http://localhost:8002"
    
    print("🚀 GuiXiaoXiRag 高级功能快速测试")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=30) as client:
        
        # 1. 知识库管理
        print("1. 测试知识库管理...")
        response = await client.get(f"{base_url}/knowledge-bases")
        if response.status_code == 200:
            data = response.json()['data']
            print(f"   ✅ 知识库列表: {len(data['knowledge_bases'])}个")
            print(f"   📊 当前: {data['current']}")
        else:
            print(f"   ❌ 失败: {response.status_code}")
        
        # 2. 性能配置
        print(f"\n2. 测试性能配置...")
        response = await client.get(f"{base_url}/performance/configs")
        if response.status_code == 200:
            configs = response.json()['data']['configs']
            print(f"   ✅ 配置选项: {list(configs.keys())}")
        else:
            print(f"   ❌ 失败: {response.status_code}")
        
        # 3. 系统监控
        print(f"\n3. 测试系统监控...")
        response = await client.get(f"{base_url}/metrics")
        if response.status_code == 200:
            metrics = response.json()['data']
            print(f"   ✅ 请求数: {metrics['total_requests']}")
            print(f"   📊 错误率: {metrics['error_rate']:.2%}")
        else:
            print(f"   ❌ 失败: {response.status_code}")
        
        # 4. 知识图谱统计
        print(f"\n4. 测试知识图谱统计...")
        response = await client.get(f"{base_url}/knowledge-graph/stats")
        if response.status_code == 200:
            stats = response.json()['data']
            print(f"   ✅ 节点: {stats['total_nodes']}, 边: {stats['total_edges']}")
        else:
            print(f"   ❌ 失败: {response.status_code}")
        
        # 5. API文档
        print(f"\n5. 测试API文档...")
        response = await client.get(f"{base_url}/docs")
        if response.status_code == 200:
            print(f"   ✅ Swagger文档可访问")
        else:
            print(f"   ❌ 失败: {response.status_code}")
        
        response = await client.get(f"{base_url}/openapi.json")
        if response.status_code == 200:
            openapi = response.json()
            print(f"   ✅ OpenAPI: {len(openapi.get('paths', {}))}个端点")
        else:
            print(f"   ❌ OpenAPI失败: {response.status_code}")
    
    print(f"\n🎉 快速测试完成！")


if __name__ == "__main__":
    asyncio.run(quick_test())
