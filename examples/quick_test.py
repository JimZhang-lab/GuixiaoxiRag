#!/usr/bin/env python3
"""
GuiXiaoXiRag FastAPI 服务快速验证脚本
"""
import asyncio
import httpx
import json


async def quick_test():
    """快速测试主要API功能"""
    base_url = "http://localhost:8002"
    
    print("🚀 GuiXiaoXiRag FastAPI 服务快速测试")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=10) as client:
        
        # 1. 健康检查
        print("1. 测试健康检查...")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("   ✅ 健康检查通过")
                data = response.json()
                print(f"   📊 服务状态: {data['system']['status']}")
                print(f"   🕐 运行时间: {data['system']['uptime']:.1f}秒")
            else:
                print(f"   ❌ 健康检查失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 连接失败: {e}")
            print("   💡 请确保服务正在运行: uvicorn server.api:app --host 0.0.0.0 --port 8002")
            return
        
        # 2. 系统状态
        print("\n2. 测试系统状态...")
        try:
            response = await client.get(f"{base_url}/system/status")
            if response.status_code == 200:
                print("   ✅ 系统状态正常")
                data = response.json()
                config = data['data']['config']
                print(f"   🤖 LLM模型: {config['openai_chat_model']}")
                print(f"   🔤 Embedding模型: {config['openai_embedding_model']}")
            else:
                print(f"   ❌ 系统状态异常: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 获取系统状态失败: {e}")
        
        # 3. 查询模式
        print("\n3. 测试查询模式...")
        try:
            response = await client.get(f"{base_url}/query/modes")
            if response.status_code == 200:
                print("   ✅ 查询模式获取成功")
                data = response.json()
                modes = data['data']['modes']
                print(f"   📋 支持的模式: {', '.join(modes.keys())}")
                print(f"   🎯 推荐模式: {', '.join(data['data']['recommended'])}")
            else:
                print(f"   ❌ 查询模式获取失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 获取查询模式失败: {e}")
        
        # 4. 知识图谱统计
        print("\n4. 测试知识图谱统计...")
        try:
            response = await client.get(f"{base_url}/knowledge-graph/stats")
            if response.status_code == 200:
                print("   ✅ 知识图谱统计正常")
                data = response.json()
                stats = data['data']
                print(f"   📊 节点数量: {stats['total_nodes']}")
                print(f"   🔗 边数量: {stats['total_edges']}")
                print(f"   💾 存储类型: {stats['graph_type']}")
            else:
                print(f"   ❌ 知识图谱统计失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 获取知识图谱统计失败: {e}")
        
        # 5. 性能指标
        print("\n5. 测试性能指标...")
        try:
            response = await client.get(f"{base_url}/metrics")
            if response.status_code == 200:
                print("   ✅ 性能指标正常")
                data = response.json()
                metrics = data['data']
                print(f"   📈 总请求数: {metrics['total_requests']}")
                print(f"   ⚠️ 错误数: {metrics['total_errors']}")
                print(f"   ⏱️ 平均响应时间: {metrics['average_response_time']:.3f}秒")
            else:
                print(f"   ❌ 性能指标获取失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 获取性能指标失败: {e}")
        
        # 6. API文档测试
        print("\n6. 测试API文档...")
        try:
            response = await client.get(f"{base_url}/docs")
            if response.status_code == 200:
                print("   ✅ API文档可访问")
                print(f"   🌐 文档地址: {base_url}/docs")
            else:
                print(f"   ❌ API文档访问失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ API文档访问失败: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 快速测试完成！")
    print("\n📖 更多功能:")
    print(f"   • API文档: {base_url}/docs")
    print(f"   • 健康检查: {base_url}/health")
    print(f"   • 系统状态: {base_url}/system/status")
    print("\n💡 提示:")
    print("   • 要测试完整功能，请确保大模型服务运行在端口8100和8200")
    print("   • 运行完整测试: python test/run_tests.py")
    print("   • 查看项目文档: cat README.md")


if __name__ == "__main__":
    asyncio.run(quick_test())
