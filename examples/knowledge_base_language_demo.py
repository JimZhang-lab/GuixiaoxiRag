#!/usr/bin/env python3
"""
知识库和语言选择功能演示
展示如何使用新的知识库选择和语言设置功能
"""
import asyncio
import httpx
import time
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def demo_knowledge_base_and_language():
    """演示知识库和语言选择功能"""
    base_url = "http://localhost:8002"
    
    async with httpx.AsyncClient(base_url=base_url, timeout=120) as client:
        
        print("🌍 知识库和语言选择功能演示")
        print("=" * 60)
        
        # 1. 查看支持的语言
        print("1. 查看支持的语言")
        print("-" * 30)
        
        response = await client.get("/languages")
        if response.status_code == 200:
            lang_info = response.json()['data']
            print(f"✅ 当前语言: {lang_info['current_language']}")
            print(f"📋 支持的语言: {', '.join(lang_info['supported_languages'])}")
        
        # 2. 查看当前服务配置
        print(f"\n2. 查看当前服务配置")
        print("-" * 30)
        
        response = await client.get("/service/config")
        if response.status_code == 200:
            config = response.json()['data']
            print(f"📁 当前知识库: {config['knowledge_base']}")
            print(f"🌍 当前语言: {config['language']}")
            print(f"🔧 初始化状态: {config['initialized']}")
            print(f"💾 缓存实例数: {config['cached_instances']}")
        
        # 3. 创建测试知识库
        print(f"\n3. 创建测试知识库")
        print("-" * 30)
        
        test_kb_name = f"lang_test_{int(time.time())}"
        kb_data = {
            "name": test_kb_name,
            "description": "语言和知识库测试"
        }
        
        response = await client.post("/knowledge-bases", json=kb_data)
        if response.status_code == 200:
            print(f"✅ 创建知识库: {test_kb_name}")
        
        # 4. 插入中文文档到测试知识库
        print(f"\n4. 插入中文文档")
        print("-" * 30)
        
        chinese_doc = {
            "text": "人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。机器学习是AI的核心技术之一。",
            "doc_id": "ai_chinese",
            "knowledge_base": test_kb_name,
            "language": "中文"
        }
        
        response = await client.post("/insert/text", json=chinese_doc)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 中文文档插入成功: {result['data']['track_id']}")
            print(f"📝 消息: {result['data']['message']}")
        
        # 5. 插入英文文档到测试知识库
        print(f"\n5. 插入英文文档")
        print("-" * 30)
        
        english_doc = {
            "text": "Artificial Intelligence (AI) is a branch of computer science that aims to create systems capable of performing tasks that typically require human intelligence. Machine learning is one of the core technologies of AI.",
            "doc_id": "ai_english",
            "knowledge_base": test_kb_name,
            "language": "英文"
        }
        
        response = await client.post("/insert/text", json=english_doc)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 英文文档插入成功: {result['data']['track_id']}")
            print(f"📝 消息: {result['data']['message']}")
        
        # 6. 等待文档处理
        print(f"\n⏳ 等待文档处理...")
        await asyncio.sleep(10)
        
        # 7. 使用中文查询
        print(f"\n7. 使用中文查询")
        print("-" * 30)
        
        chinese_query = {
            "query": "什么是人工智能？",
            "mode": "hybrid",
            "knowledge_base": test_kb_name,
            "language": "中文"
        }
        
        response = await client.post("/query", json=chinese_query)
        if response.status_code == 200:
            result = response.json()['data']
            print(f"✅ 中文查询成功")
            print(f"📁 知识库: {result['knowledge_base']}")
            print(f"🌍 语言: {result['language']}")
            print(f"📝 回答: {result['result'][:200]}...")
        
        # 8. 使用英文查询
        print(f"\n8. 使用英文查询")
        print("-" * 30)
        
        english_query = {
            "query": "What is artificial intelligence?",
            "mode": "hybrid",
            "knowledge_base": test_kb_name,
            "language": "英文"
        }
        
        response = await client.post("/query", json=english_query)
        if response.status_code == 200:
            result = response.json()['data']
            print(f"✅ 英文查询成功")
            print(f"📁 知识库: {result['knowledge_base']}")
            print(f"🌍 语言: {result['language']}")
            print(f"📝 回答: {result['result'][:200]}...")
        
        # 9. 切换服务默认配置
        print(f"\n9. 切换服务默认配置")
        print("-" * 30)
        
        switch_config = {
            "knowledge_base": test_kb_name,
            "language": "英文"
        }
        
        response = await client.post("/service/switch-kb", json=switch_config)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 服务配置切换成功")
            print(f"📝 消息: {result['message']}")
        
        # 10. 验证配置切换
        print(f"\n10. 验证配置切换")
        print("-" * 30)
        
        response = await client.get("/service/config")
        if response.status_code == 200:
            config = response.json()['data']
            print(f"📁 当前知识库: {config['knowledge_base']}")
            print(f"🌍 当前语言: {config['language']}")
        
        # 11. 使用默认配置查询（不指定知识库和语言）
        print(f"\n11. 使用默认配置查询")
        print("-" * 30)
        
        default_query = {
            "query": "Tell me about machine learning",
            "mode": "hybrid"
        }
        
        response = await client.post("/query", json=default_query)
        if response.status_code == 200:
            result = response.json()['data']
            print(f"✅ 默认配置查询成功")
            print(f"📁 使用知识库: {result['knowledge_base']}")
            print(f"🌍 使用语言: {result['language']}")
            print(f"📝 回答: {result['result'][:200]}...")
        
        # 12. 批量插入到不同知识库
        print(f"\n12. 批量插入到不同知识库")
        print("-" * 30)
        
        batch_docs = {
            "texts": [
                "深度学习是机器学习的一个子集，使用神经网络进行学习。",
                "自然语言处理是AI的重要应用领域之一。",
                "计算机视觉让机器能够理解和分析视觉信息。"
            ],
            "doc_ids": ["dl_chinese", "nlp_chinese", "cv_chinese"],
            "knowledge_base": test_kb_name,
            "language": "中文"
        }
        
        response = await client.post("/insert/texts", json=batch_docs)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 批量插入成功: {result['data']['track_id']}")
            print(f"📝 消息: {result['data']['message']}")
        
        print(f"\n🎉 知识库和语言选择功能演示完成！")
        print("=" * 60)
        
        print(f"\n📋 功能总结:")
        print("✅ 支持多知识库管理")
        print("✅ 支持多语言回答（中文/英文）")
        print("✅ 可以为每个操作指定知识库和语言")
        print("✅ 支持服务级别的默认配置")
        print("✅ 支持实时切换知识库和语言")
        print("✅ 支持批量操作的知识库和语言设置")
        
        print(f"\n🔧 使用建议:")
        print("• 为不同项目创建独立的知识库")
        print("• 根据用户需求选择合适的回答语言")
        print("• 使用服务配置API管理默认设置")
        print("• 在API调用中明确指定知识库和语言以获得最佳效果")


async def demo_api_examples():
    """API使用示例"""
    print(f"\n📖 API使用示例:")
    print("=" * 60)
    
    print(f"""
🔧 1. 插入文档到指定知识库和语言:
POST /insert/text
{{
    "text": "这是一个测试文档",
    "knowledge_base": "my_project",
    "language": "中文"
}}

🔍 2. 查询指定知识库并用英文回答:
POST /query
{{
    "query": "What is this about?",
    "knowledge_base": "my_project", 
    "language": "英文"
}}

📁 3. 批量插入到指定知识库:
POST /insert/texts
{{
    "texts": ["文档1", "文档2"],
    "knowledge_base": "my_project",
    "language": "中文"
}}

🌍 4. 设置默认语言:
POST /languages/set
{{
    "language": "英文"
}}

🔄 5. 切换服务默认配置:
POST /service/switch-kb
{{
    "knowledge_base": "my_project",
    "language": "英文"
}}

📊 6. 查看当前配置:
GET /service/config

📋 7. 查看支持的语言:
GET /languages
    """)


if __name__ == "__main__":
    asyncio.run(demo_knowledge_base_and_language())
    asyncio.run(demo_api_examples())
