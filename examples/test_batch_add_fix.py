"""
测试批量添加修复
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_batch_add():
    """测试批量添加问答对"""
    try:
        print("开始测试批量添加修复...")
        
        # 导入OptimizedQAManager
        from core.quick_qa_base.optimized_qa_manager import OptimizedQAManager
        
        # 创建管理器
        qa_manager = OptimizedQAManager(
            workspace="test_qa_base",
            namespace="test",
            similarity_threshold=0.98,
            max_results=10,
            working_dir="./Q_A_Base"
        )
        
        print("✅ OptimizedQAManager创建成功")
        
        # 初始化
        success = await qa_manager.initialize()
        if not success:
            print("❌ 初始化失败")
            return
        
        print("✅ OptimizedQAManager初始化成功")
        
        # 测试批量添加
        test_qa_pairs = [
            {
                "question": "测试问题1：什么是人工智能？",
                "answer": "人工智能是计算机科学的一个分支。",
                "category": "test",
                "confidence": 0.9,
                "keywords": ["AI", "人工智能"],
                "source": "test_script"
            },
            {
                "question": "测试问题2：什么是机器学习？",
                "answer": "机器学习是人工智能的一个子集。",
                "category": "test",
                "confidence": 0.9,
                "keywords": ["ML", "机器学习"],
                "source": "test_script"
            }
        ]
        
        print("开始批量添加问答对...")
        result = await qa_manager.add_qa_pairs_batch(test_qa_pairs)
        
        if result.get("success"):
            print(f"✅ 批量添加成功！添加了 {result.get('added_count', 0)} 个问答对")
            print(f"   失败: {result.get('failed_count', 0)} 个")
            print(f"   添加的ID: {result.get('added_ids', [])}")
        else:
            print(f"❌ 批量添加失败: {result.get('error')}")
            return
        
        # 测试查询
        print("\n测试查询...")
        query_result = await qa_manager.query("什么是AI？")
        
        if query_result.get("success"):
            if query_result.get("found"):
                print(f"✅ 查询成功！相似度: {query_result.get('similarity', 0):.4f}")
                print(f"   答案: {query_result.get('answer', '')[:50]}...")
            else:
                print("⚠️ 未找到匹配的答案")
        else:
            print(f"❌ 查询失败: {query_result.get('error')}")
        
        # 获取统计信息
        stats = qa_manager.get_statistics()
        if stats.get("success"):
            total_pairs = stats.get("data", {}).get("storage_stats", {}).get("total_pairs", 0)
            print(f"✅ 当前总问答对数: {total_pairs}")
        
        print("\n测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_batch_add())
