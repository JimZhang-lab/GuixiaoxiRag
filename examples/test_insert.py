#!/usr/bin/env python3
"""
测试插入功能的脚本
"""
import asyncio
import httpx
import json
import time


async def test_insert():
    """测试插入功能"""
    base_url = "http://localhost:8002"
    
    print("🧪 测试GuiXiaoXiRag插入功能")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=60) as client:
        
        # 测试数据
        test_cases = [
            {
                "name": "英文文本",
                "data": {
                    "text": "Artificial Intelligence is a branch of computer science.",
                    "doc_id": "ai_en_1"
                }
            },
            {
                "name": "中文文本",
                "data": {
                    "text": "人工智能是计算机科学的重要分支。",
                    "doc_id": "ai_zh_1"
                }
            },
            {
                "name": "混合文本",
                "data": {
                    "text": "机器学习(Machine Learning)是人工智能的核心技术之一。",
                    "doc_id": "ml_mixed_1"
                }
            },
            {
                "name": "长文本",
                "data": {
                    "text": "深度学习是机器学习的一个子集，它使用神经网络来模拟人脑的学习过程。深度学习在图像识别、自然语言处理、语音识别等领域取得了突破性进展。",
                    "doc_id": "dl_long_1"
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. 测试{test_case['name']}...")
            
            try:
                start_time = time.time()
                response = await client.post(
                    f"{base_url}/insert/text",
                    json=test_case['data']
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ 插入成功")
                    print(f"   📊 Track ID: {result['data']['track_id']}")
                    print(f"   ⏱️ 处理时间: {end_time - start_time:.2f}秒")
                else:
                    print(f"   ❌ 插入失败: {response.status_code}")
                    print(f"   📄 响应: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ 请求失败: {e}")
        
        # 测试知识图谱统计
        print(f"\n5. 检查知识图谱统计...")
        try:
            response = await client.get(f"{base_url}/knowledge-graph/stats")
            if response.status_code == 200:
                stats = response.json()['data']
                print(f"   📊 节点数量: {stats['total_nodes']}")
                print(f"   🔗 边数量: {stats['total_edges']}")
            else:
                print(f"   ❌ 获取统计失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 获取统计失败: {e}")


async def test_query():
    """测试查询功能"""
    base_url = "http://localhost:8002"
    
    print(f"\n🔍 测试查询功能")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=60) as client:
        
        # 测试查询
        queries = [
            {
                "name": "英文查询",
                "query": "What is artificial intelligence?",
                "mode": "hybrid"
            },
            {
                "name": "中文查询", 
                "query": "什么是人工智能？",
                "mode": "hybrid"
            },
            {
                "name": "技术查询",
                "query": "机器学习和深度学习的关系",
                "mode": "local"
            }
        ]
        
        for i, test_query in enumerate(queries, 1):
            print(f"\n{i}. 测试{test_query['name']}...")
            
            try:
                start_time = time.time()
                response = await client.post(
                    f"{base_url}/query",
                    json={
                        "query": test_query['query'],
                        "mode": test_query['mode'],
                        "top_k": 10
                    }
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ 查询成功")
                    print(f"   🎯 模式: {result['data']['mode']}")
                    print(f"   ⏱️ 处理时间: {end_time - start_time:.2f}秒")
                    print(f"   📝 结果预览: {result['data']['result'][:100]}...")
                else:
                    print(f"   ❌ 查询失败: {response.status_code}")
                    print(f"   📄 响应: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ 查询失败: {e}")


async def main():
    """主函数"""
    print("🚀 GuiXiaoXiRag FastAPI 完整功能测试")
    print("=" * 60)
    
    # 先测试插入
    await test_insert()
    
    # 等待一段时间让数据处理完成
    print(f"\n⏳ 等待数据处理完成...")
    await asyncio.sleep(3)
    
    # 再测试查询
    await test_query()
    
    print(f"\n🎉 测试完成！")


if __name__ == "__main__":
    asyncio.run(main())
