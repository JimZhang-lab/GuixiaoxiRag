#!/usr/bin/env python3
"""
专门检查相似度计算问题的调试脚本
"""

import asyncio
import json
import os
import sys
import numpy as np
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_embedding_consistency():
    """测试embedding的一致性"""
    print("=== 测试Embedding一致性 ===\n")
    
    try:
        from core.common.llm_client import create_embedding_function
        
        embedding_func = await create_embedding_function()
        if not embedding_func:
            print("❌ 无法创建embedding函数")
            return False
        
        # 测试相同文本的embedding一致性
        test_text = "问答系统支持哪些功能？"
        
        print(f"测试文本: '{test_text}'")
        print("多次向量化测试:")
        
        embeddings = []
        for i in range(3):
            embedding = await embedding_func([test_text])
            if embedding and len(embedding) > 0:
                emb_array = np.array(embedding[0])
                embeddings.append(emb_array)
                print(f"  第{i+1}次: 维度={emb_array.shape}, 范数={np.linalg.norm(emb_array):.6f}")
            else:
                print(f"  第{i+1}次: ❌ 向量化失败")
                return False
        
        # 检查一致性
        if len(embeddings) >= 2:
            similarity_12 = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
            similarity_13 = np.dot(embeddings[0], embeddings[2]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[2]))
            
            print(f"\n一致性检查:")
            print(f"  第1次 vs 第2次: {similarity_12:.8f}")
            print(f"  第1次 vs 第3次: {similarity_13:.8f}")
            
            if similarity_12 > 0.999 and similarity_13 > 0.999:
                print(f"  ✅ Embedding一致性良好")
            else:
                print(f"  ⚠️  Embedding一致性有问题")
        
        return True
        
    except Exception as e:
        print(f"❌ Embedding测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_vector_storage_similarity():
    """测试向量存储的相似度计算"""
    print("\n=== 测试向量存储相似度计算 ===\n")
    
    try:
        from core.quick_qa_base.qa_vector_storage import QAVectorStorage
        from core.common.llm_client import create_embedding_function
        
        # 创建临时存储
        embedding_func = await create_embedding_function()
        storage = QAVectorStorage(
            namespace="test",
            embedding_func=embedding_func,
            workspace="temp_test",  # 移除前导的./
            global_config={
                "working_dir": ".",  # 设置为当前目录
                "embedding_batch_num": 10
            }
        )
        
        await storage.initialize()
        print("✅ 临时向量存储初始化成功")
        
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
        
        print(f"\n测试查询相似度:")
        
        # 测试查询
        for i, query in enumerate(test_questions):
            print(f"\n查询 {i+1}: '{query}'")
            
            results = await storage.query(query, top_k=4, better_than_threshold=None)
            
            if results:
                print(f"  找到 {len(results)} 个结果:")
                for j, result in enumerate(results):
                    distance = result.get("distance", 1.0)
                    similarity = 1.0 - distance
                    qa_id = result.get("qa_id")
                    matched_question = storage.qa_pairs.get(qa_id).question if qa_id in storage.qa_pairs else "未知"
                    
                    print(f"    {j+1}. 距离={distance:.6f}, 相似度={similarity:.6f}")
                    print(f"       匹配问题: '{matched_question}'")
                    print(f"       QA ID: {qa_id}")
                    
                    # 特别检查完全相同的问题
                    if query == matched_question:
                        if similarity > 0.99:
                            print(f"       ✅ 完全相同问题的相似度正常")
                        else:
                            print(f"       ❌ 完全相同问题的相似度异常低: {similarity:.6f}")
            else:
                print(f"  ❌ 未找到任何结果")
        
        # 清理临时文件
        await storage.cleanup()
        import shutil
        if os.path.exists("./temp_test"):
            shutil.rmtree("./temp_test")
        
        return True
        
    except Exception as e:
        print(f"❌ 向量存储测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_nanodb_similarity():
    """直接测试NanoVectorDB的相似度计算"""
    print("\n=== 测试NanoVectorDB相似度计算 ===\n")
    
    try:
        from nano_vectordb import NanoVectorDB
        from core.common.llm_client import create_embedding_function
        
        # 创建临时数据库
        db = NanoVectorDB(
            embedding_dim=2560,
            metric="cosine",
            storage_file="./temp_nanodb_test.json"
        )
        
        embedding_func = await create_embedding_function()
        
        # 准备测试数据
        test_texts = [
            "问答系统支持哪些功能？",
            "问答系统支持哪些功能？",  # 完全相同
            "问答系统有哪些功能？",    # 非常相似
            "什么是机器学习？"         # 完全不同
        ]
        
        # 生成embeddings
        embeddings = await embedding_func(test_texts)
        
        # 插入数据
        data_list = []
        for i, (text, embedding) in enumerate(zip(test_texts, embeddings)):
            data_list.append({
                "__id__": f"test_{i}",
                "__vector__": np.array(embedding, dtype=np.float32),
                "content": text,
                "text": text
            })
        
        db.upsert(datas=data_list)
        print(f"✅ 插入 {len(data_list)} 条测试数据")
        
        # 测试查询
        for i, query_text in enumerate(test_texts):
            print(f"\n查询 {i+1}: '{query_text}'")
            
            # 生成查询向量
            query_embedding = await embedding_func([query_text])
            query_vector = np.array(query_embedding[0], dtype=np.float32)
            
            # 执行查询
            results = db.query(query=query_vector, top_k=4)
            
            if results:
                print(f"  找到 {len(results)} 个结果:")
                for j, result in enumerate(results):
                    # 调试：打印所有字段
                    print(f"    结果 {j+1} 的所有字段: {list(result.keys())}")

                    # 尝试不同的距离字段名
                    distance = result.get("__distance__", result.get("__metrics__", result.get("distance", 1.0)))
                    similarity = 1.0 - distance
                    content = result.get("content", "未知")

                    print(f"    {j+1}. 距离={distance:.6f}, 相似度={similarity:.6f}")
                    print(f"       内容: '{content}'")
                    
                    # 检查完全相同的文本
                    if query_text == content:
                        if similarity > 0.99:
                            print(f"       ✅ 完全相同文本的相似度正常")
                        else:
                            print(f"       ❌ 完全相同文本的相似度异常: {similarity:.6f}")
                            
                            # 详细分析
                            print(f"       🔍 详细分析:")
                            print(f"          查询向量范数: {np.linalg.norm(query_vector):.6f}")
                            stored_vector = result.get("__vector__")
                            if stored_vector is not None:
                                print(f"          存储向量范数: {np.linalg.norm(stored_vector):.6f}")
                                dot_product = np.dot(query_vector, stored_vector)
                                manual_similarity = dot_product / (np.linalg.norm(query_vector) * np.linalg.norm(stored_vector))
                                print(f"          手动计算相似度: {manual_similarity:.6f}")
                                print(f"          向量差异: {np.linalg.norm(query_vector - stored_vector):.6f}")
            else:
                print(f"  ❌ 未找到任何结果")
        
        # 清理临时文件
        if os.path.exists("./temp_nanodb_test.json"):
            os.remove("./temp_nanodb_test.json")
        
        return True
        
    except Exception as e:
        print(f"❌ NanoVectorDB测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_current_system_similarity():
    """测试当前系统的相似度计算"""
    print("\n=== 测试当前系统相似度计算 ===\n")
    
    try:
        from core.quick_qa_base.optimized_qa_manager import OptimizedQAManager
        
        qa_manager = OptimizedQAManager(
            workspace="qa_base",
            namespace="default",
            similarity_threshold=0.1,
            working_dir="./Q_A_Base"
        )
        
        success = await qa_manager.initialize()
        if not success:
            print("❌ QA管理器初始化失败")
            return False
        
        print("✅ QA管理器初始化成功")
        
        # 获取当前系统中的问题
        qa_pairs = qa_manager.storage.qa_pairs
        print(f"当前系统中有 {len(qa_pairs)} 个问答对:")
        
        questions = []
        for qa_id, qa_pair in qa_pairs.items():
            questions.append(qa_pair.question)
            print(f"  - {qa_id}: '{qa_pair.question}'")
        
        print(f"\n测试相似度计算:")
        
        # 测试每个问题与自己的相似度
        for question in questions[:4]:  # 只测试前4个
            print(f"\n查询: '{question}'")
            
            result = await qa_manager.query(
                question=question,
                top_k=5,
                min_similarity=0.0
            )
            
            if result.get("found"):
                print(f"  ✅ 找到匹配")
                print(f"  最佳匹配问题: '{result.get('question')}'")
                print(f"  相似度: {result.get('similarity', 0):.6f}")
                print(f"  分类: {result.get('category')}")
                
                # 检查是否是完全相同的问题
                if question == result.get('question'):
                    similarity = result.get('similarity', 0)
                    if similarity > 0.99:
                        print(f"  ✅ 完全相同问题的相似度正常")
                    else:
                        print(f"  ❌ 完全相同问题的相似度异常低: {similarity:.6f}")
                        
                        # 显示所有结果进行分析
                        all_results = result.get('all_results', [])
                        if all_results:
                            print(f"  🔍 所有匹配结果:")
                            for i, res in enumerate(all_results):
                                qa_pair = res.get('qa_pair', {})
                                sim = res.get('similarity', 0)
                                print(f"    {i+1}. '{qa_pair.get('question', 'N/A')}' - 相似度: {sim:.6f}")
                else:
                    print(f"  ⚠️  匹配到了不同的问题")
            else:
                print(f"  ❌ 未找到匹配")
        
        await qa_manager.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ 当前系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("🔍 相似度计算问题诊断脚本")
    print("=" * 60)
    
    print("\n📋 诊断计划:")
    print("  1. 测试Embedding函数的一致性")
    print("  2. 测试向量存储的相似度计算")
    print("  3. 直接测试NanoVectorDB的相似度计算")
    print("  4. 测试当前系统的相似度计算")
    print()
    
    # 测试1: Embedding一致性
    embedding_ok = await test_embedding_consistency()
    
    # 测试2: 向量存储相似度
    if embedding_ok:
        storage_ok = await test_vector_storage_similarity()
    else:
        storage_ok = False
    
    # 测试3: NanoVectorDB相似度
    if embedding_ok:
        nanodb_ok = await test_nanodb_similarity()
    else:
        nanodb_ok = False
    
    # 测试4: 当前系统相似度
    system_ok = await test_current_system_similarity()
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 诊断结果总结:")
    print(f"  Embedding一致性: {'✅ 正常' if embedding_ok else '❌ 异常'}")
    print(f"  向量存储相似度: {'✅ 正常' if storage_ok else '❌ 异常'}")
    print(f"  NanoVectorDB相似度: {'✅ 正常' if nanodb_ok else '❌ 异常'}")
    print(f"  当前系统相似度: {'✅ 正常' if system_ok else '❌ 异常'}")
    
    if all([embedding_ok, storage_ok, nanodb_ok, system_ok]):
        print("\n🎉 所有测试通过！相似度计算正常。")
    else:
        print("\n⚠️  发现问题，需要进一步调试:")
        if not embedding_ok:
            print("    - Embedding函数可能不稳定或配置有问题")
        if not storage_ok:
            print("    - 向量存储层的相似度计算有问题")
        if not nanodb_ok:
            print("    - NanoVectorDB的距离计算有问题")
        if not system_ok:
            print("    - 系统整体的相似度计算逻辑有问题")
    
    print("\n💡 可能的解决方案:")
    print("    1. 检查embedding模型配置")
    print("    2. 验证向量归一化处理")
    print("    3. 检查距离度量设置(cosine vs euclidean)")
    print("    4. 验证向量存储和检索逻辑")
    print("    5. 检查相似度阈值设置")


if __name__ == "__main__":
    asyncio.run(main())
