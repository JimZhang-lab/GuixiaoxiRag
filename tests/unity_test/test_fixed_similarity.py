#!/usr/bin/env python3
"""
测试修复后的相似度计算
"""

import asyncio
import os
import sys
import tempfile
import shutil

# 添加项目路径
sys.path.append('.')

async def test_fixed_similarity():
    """测试修复后的相似度计算"""
    print("🔧 测试修复后的相似度计算")
    print("=" * 50)
    
    try:
        # 导入必要的模块
        from core.common.llm_client import create_embedding_function
        from core.quick_qa_base.qa_vector_storage import QAVectorStorage
        
        # 创建embedding函数
        embedding_func = await create_embedding_function()
        if not embedding_func:
            print("❌ 无法创建embedding函数")
            return
        
        print("✅ Embedding函数创建成功")
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 创建向量存储
            storage = QAVectorStorage(
                namespace="test",
                embedding_func=embedding_func,
                workspace=None,  # 不使用workspace
                global_config={
                    "working_dir": temp_dir,
                    "embedding_batch_num": 10
                }
            )
            
            await storage.initialize()
            print("✅ 向量存储初始化成功")
            
            # 添加测试问答对
            test_questions = [
                "问答系统支持哪些功能？",
                "问答系统支持哪些功能？",  # 完全相同
                "问答系统有哪些功能？",    # 非常相似
                "什么是机器学习？"         # 完全不同
            ]
            
            qa_ids = []
            for i, question in enumerate(test_questions):
                qa_id = await storage.add_qa_pair(
                    question=question,
                    answer=f"这是第{i+1}个测试答案。",
                    category="test",
                    skip_duplicate_check=True  # 跳过重复检查以便测试
                )
                qa_ids.append(qa_id)
                print(f"添加问答对 {i+1}: {qa_id}")
            
            print(f"\n🔍 测试查询相似度:")
            
            # 测试查询
            for i, query in enumerate(test_questions):
                print(f"\n查询 {i+1}: '{query}'")
                
                results = await storage.query(query, top_k=4, better_than_threshold=None)
                
                if results:
                    print(f"  找到 {len(results)} 个结果:")
                    for j, result in enumerate(results):
                        similarity = result.get("similarity", 0.0)
                        distance = result.get("distance", 1.0)
                        qa_id = result.get("qa_id", "N/A")
                        
                        # 获取问题内容
                        qa_pair = storage.qa_pairs.get(qa_id)
                        question_text = qa_pair.question if qa_pair else "未知"
                        
                        print(f"    {j+1}. 相似度={similarity:.6f}, 距离={distance:.6f}")
                        print(f"       匹配问题: '{question_text}'")
                        print(f"       QA ID: {qa_id}")
                        
                        # 检查完全相同的问题
                        if query == question_text:
                            if similarity > 0.99:
                                print(f"       ✅ 完全相同问题的相似度正常: {similarity:.6f}")
                            else:
                                print(f"       ❌ 完全相同问题的相似度异常低: {similarity:.6f}")
                        elif similarity > 0.9:
                            print(f"       📈 高相似度匹配")
                        elif similarity > 0.5:
                            print(f"       📊 中等相似度匹配")
                        else:
                            print(f"       📉 低相似度匹配")
                else:
                    print(f"  ❌ 未找到任何结果")
            
            # 测试query_qa方法
            print(f"\n🔍 测试query_qa方法:")
            
            for i, query in enumerate(test_questions[:2]):  # 只测试前两个
                print(f"\nquery_qa测试 {i+1}: '{query}'")
                
                result = await storage.query_qa(query, top_k=1, min_similarity=0.1)
                
                if result.get("found"):
                    similarity = result.get("similarity", 0.0)
                    question = result.get("question", "")
                    print(f"  ✅ 找到匹配")
                    print(f"  相似度: {similarity:.6f}")
                    print(f"  匹配问题: '{question}'")
                    
                    if query == question and similarity > 0.99:
                        print(f"  🎉 完美匹配！")
                    elif query == question:
                        print(f"  ⚠️  问题匹配但相似度低: {similarity:.6f}")
                    else:
                        print(f"  ⚠️  匹配到不同问题")
                else:
                    print(f"  ❌ 未找到匹配")
                    print(f"  消息: {result.get('message', 'N/A')}")
        
        finally:
            # 清理临时目录
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_fixed_similarity())
