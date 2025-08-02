#!/usr/bin/env python3
"""
GuiXiaoXiRag FastAPI 服务功能演示
"""
import asyncio
import httpx
import json
import time


async def demo_complete_workflow():
    """演示完整的工作流程"""
    base_url = "http://localhost:8002"
    
    print("🎬 GuiXiaoXiRag FastAPI 服务完整功能演示")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=60) as client:
        
        # 1. 系统状态检查
        print("📊 1. 系统状态检查")
        print("-" * 30)
        
        response = await client.get(f"{base_url}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ 服务状态: {health['system']['status']}")
            print(f"🕐 运行时间: {health['system']['uptime']:.1f}秒")
        
        response = await client.get(f"{base_url}/knowledge-bases")
        if response.status_code == 200:
            kbs = response.json()['data']
            print(f"📁 知识库数量: {kbs['total']}")
            print(f"📊 当前知识库: {kbs['current']}")
        
        # 2. 创建演示知识库
        print(f"\n🗄️ 2. 创建演示知识库")
        print("-" * 30)
        
        demo_kb_name = f"demo_{int(time.time())}"
        response = await client.post(
            f"{base_url}/knowledge-bases",
            json={
                "name": demo_kb_name,
                "description": "功能演示知识库"
            }
        )
        if response.status_code == 200:
            print(f"✅ 创建知识库: {demo_kb_name}")
        
        # 切换到演示知识库
        response = await client.post(
            f"{base_url}/knowledge-bases/switch",
            json={"name": demo_kb_name}
        )
        if response.status_code == 200:
            print(f"✅ 切换到演示知识库")
        
        # 3. 插入演示数据
        print(f"\n📝 3. 插入演示数据")
        print("-" * 30)
        
        demo_documents = [
            {
                "text": "人工智能（Artificial Intelligence, AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。AI包括机器学习、深度学习、自然语言处理等多个子领域。",
                "doc_id": "ai_intro"
            },
            {
                "text": "机器学习（Machine Learning, ML）是人工智能的一个子集，它使计算机能够从数据中学习而无需明确编程。常见的机器学习算法包括线性回归、决策树、随机森林、支持向量机等。",
                "doc_id": "ml_intro"
            },
            {
                "text": "深度学习（Deep Learning, DL）是机器学习的一个子集，使用神经网络来模拟人脑的学习过程。深度学习在图像识别、语音识别、自然语言处理等领域取得了突破性进展。",
                "doc_id": "dl_intro"
            }
        ]
        
        for i, doc in enumerate(demo_documents, 1):
            print(f"   插入文档 {i}/3...")
            start_time = time.time()
            response = await client.post(f"{base_url}/insert/text", json=doc)
            end_time = time.time()
            
            if response.status_code == 200:
                track_id = response.json()['data']['track_id']
                print(f"   ✅ 文档 {i} 插入成功 ({end_time - start_time:.1f}秒)")
            else:
                print(f"   ❌ 文档 {i} 插入失败")
        
        # 等待数据处理
        print(f"\n⏳ 等待数据处理完成...")
        await asyncio.sleep(5)
        
        # 4. 查询演示
        print(f"\n🔍 4. 智能查询演示")
        print("-" * 30)
        
        demo_queries = [
            {
                "query": "什么是人工智能？",
                "mode": "hybrid",
                "description": "混合模式查询"
            },
            {
                "query": "机器学习和深度学习的关系是什么？",
                "mode": "local",
                "description": "本地模式查询"
            },
            {
                "query": "深度学习在哪些领域有应用？",
                "mode": "global",
                "description": "全局模式查询"
            }
        ]
        
        for i, query_info in enumerate(demo_queries, 1):
            print(f"\n   查询 {i}: {query_info['description']}")
            print(f"   问题: {query_info['query']}")
            
            start_time = time.time()
            response = await client.post(
                f"{base_url}/query",
                json={
                    "query": query_info['query'],
                    "mode": query_info['mode'],
                    "top_k": 10
                }
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()['data']
                print(f"   ✅ 查询成功 ({end_time - start_time:.1f}秒)")
                print(f"   📝 回答预览: {result['result'][:150]}...")
            else:
                print(f"   ❌ 查询失败")
        
        # 5. 性能优化演示
        print(f"\n⚡ 5. 性能优化演示")
        print("-" * 30)
        
        # 快速查询模式
        print(f"   测试快速查询模式...")
        start_time = time.time()
        response = await client.post(
            f"{base_url}/query/optimized",
            json={
                "query": "AI的主要应用领域",
                "mode": "hybrid",
                "performance_level": "fast"
            }
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()['data']
            print(f"   ✅ 快速模式查询成功 ({end_time - start_time:.1f}秒)")
            print(f"   🎯 优化参数: {result['optimized_params']}")
        
        # 6. 知识图谱分析
        print(f"\n🕸️ 6. 知识图谱分析")
        print("-" * 30)
        
        response = await client.get(f"{base_url}/knowledge-graph/stats")
        if response.status_code == 200:
            stats = response.json()['data']
            print(f"   📊 图谱统计:")
            print(f"   • 节点数量: {stats['total_nodes']}")
            print(f"   • 边数量: {stats['total_edges']}")
            print(f"   • 存储类型: {stats['graph_type']}")
        
        # 7. 系统监控
        print(f"\n📈 7. 系统监控")
        print("-" * 30)
        
        response = await client.get(f"{base_url}/metrics")
        if response.status_code == 200:
            metrics = response.json()['data']
            print(f"   📊 性能指标:")
            print(f"   • 总请求数: {metrics['total_requests']}")
            print(f"   • 错误数: {metrics['total_errors']}")
            print(f"   • 平均响应时间: {metrics['average_response_time']:.3f}秒")
            print(f"   • 错误率: {metrics['error_rate']:.2%}")
        
        # 8. 导出演示
        print(f"\n📤 8. 知识库导出")
        print("-" * 30)
        
        response = await client.get(f"{base_url}/knowledge-bases/{demo_kb_name}/export")
        if response.status_code == 200:
            export_data = response.json()['data']
            print(f"   ✅ 导出成功")
            print(f"   📊 导出数据:")
            print(f"   • 文档数量: {len(export_data.get('documents', []))}")
            print(f"   • 导出时间: {export_data.get('exported_at', 'unknown')}")
        
        # 9. API文档展示
        print(f"\n📖 9. API文档")
        print("-" * 30)
        
        response = await client.get(f"{base_url}/openapi.json")
        if response.status_code == 200:
            openapi = response.json()
            print(f"   ✅ API文档可访问")
            print(f"   📋 API端点数量: {len(openapi.get('paths', {}))}")
            print(f"   🌐 文档地址: {base_url}/docs")
        
        print(f"\n🎉 演示完成！")
        print("=" * 60)
        print("🚀 GuiXiaoXiRag FastAPI 服务功能特性:")
        print("• ✅ 多知识库管理")
        print("• ✅ 智能文档插入")
        print("• ✅ 多模式查询")
        print("• ✅ 性能优化")
        print("• ✅ 知识图谱分析")
        print("• ✅ 实时监控")
        print("• ✅ 数据导入导出")
        print("• ✅ 完整API文档")
        print(f"\n📖 更多信息请查看:")
        print(f"• API文档: {base_url}/docs")
        print(f"• 项目文档: README.md")
        print(f"• 部署指南: DEPLOYMENT_GUIDE.md")


if __name__ == "__main__":
    asyncio.run(demo_complete_workflow())
