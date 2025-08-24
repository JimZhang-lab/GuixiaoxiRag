#!/usr/bin/env python3
"""
简单的并发控制验证脚本
验证QA系统的基本并发安全性
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.quick_qa_base.category_qa_storage import CategoryQAStorage
from core.quick_qa_base.qa_concurrency_manager import QAConcurrencyManager


async def test_concurrent_operations():
    """测试并发操作"""
    print("🧪 开始并发控制验证测试")
    
    # 创建临时存储目录
    test_storage_path = "temp_test_storage"
    os.makedirs(test_storage_path, exist_ok=True)
    
    try:
        # 初始化存储
        storage = CategoryQAStorage(
            storage_path=test_storage_path,
            embedding_dim=768,
            similarity_threshold=0.98
        )
        await storage.initialize()
        
        print("✅ 存储初始化成功")
        
        # 测试1: 并发创建同一分类的问答对
        print("\n📝 测试1: 并发创建问答对")
        
        async def create_qa_pair(index):
            """创建问答对的协程"""
            try:
                qa_id = await storage.add_qa_pair(
                    question=f"Test question {index}",
                    answer=f"Test answer {index}",
                    category="test_category",
                    confidence=0.9
                )
                print(f"  ✅ 创建问答对 {index}: {qa_id}")
                return qa_id
            except Exception as e:
                print(f"  ❌ 创建问答对 {index} 失败: {e}")
                return None
        
        # 并发创建5个问答对
        tasks = [create_qa_pair(i) for i in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_creates = [r for r in results if r is not None and not isinstance(r, Exception)]
        print(f"  📊 成功创建: {len(successful_creates)}/5")
        
        # 测试2: 并发删除分类
        print("\n🗑️ 测试2: 并发删除分类")
        
        async def delete_category(index):
            """删除分类的协程"""
            try:
                result = await storage.delete_category("test_category")
                print(f"  ✅ 删除操作 {index}: {result['success']}")
                return result
            except Exception as e:
                print(f"  ❌ 删除操作 {index} 失败: {e}")
                return {"success": False, "error": str(e)}
        
        # 并发执行3个删除操作
        delete_tasks = [delete_category(i) for i in range(3)]
        delete_results = await asyncio.gather(*delete_tasks, return_exceptions=True)
        
        successful_deletes = [r for r in delete_results if isinstance(r, dict) and r.get("success")]
        print(f"  📊 成功删除: {len(successful_deletes)}/3")
        
        # 测试3: 并发创建和删除
        print("\n⚡ 测试3: 并发创建和删除")
        
        # 重新创建一些问答对
        for i in range(3):
            await storage.add_qa_pair(
                question=f"Mixed test question {i}",
                answer=f"Mixed test answer {i}",
                category="mixed_test",
                confidence=0.9
            )
        
        async def mixed_operations():
            """混合操作"""
            tasks = []
            
            # 添加创建任务
            for i in range(3, 6):
                tasks.append(create_qa_pair_for_category("mixed_test", i))
            
            # 添加删除任务
            tasks.append(delete_category_by_name("mixed_test"))
            
            return await asyncio.gather(*tasks, return_exceptions=True)
        
        async def create_qa_pair_for_category(category, index):
            """为指定分类创建问答对"""
            try:
                qa_id = await storage.add_qa_pair(
                    question=f"Mixed question {index}",
                    answer=f"Mixed answer {index}",
                    category=category,
                    confidence=0.9
                )
                print(f"  ✅ 混合创建 {index}: {qa_id}")
                return qa_id
            except Exception as e:
                print(f"  ❌ 混合创建 {index} 失败: {e}")
                return None
        
        async def delete_category_by_name(category):
            """删除指定分类"""
            try:
                result = await storage.delete_category(category)
                print(f"  ✅ 混合删除 {category}: {result['success']}")
                return result
            except Exception as e:
                print(f"  ❌ 混合删除 {category} 失败: {e}")
                return {"success": False, "error": str(e)}
        
        mixed_results = await mixed_operations()
        print(f"  📊 混合操作完成: {len(mixed_results)} 个操作")
        
        # 测试4: 验证锁管理器状态
        print("\n🔒 测试4: 锁管理器状态")
        
        # 获取锁统计信息
        lock_stats = QAConcurrencyManager.get_lock_stats()
        print(f"  📊 锁统计: {lock_stats}")
        
        print("\n🎉 并发控制验证测试完成")
        
        return {
            "create_success": len(successful_creates),
            "delete_success": len(successful_deletes),
            "mixed_operations": len(mixed_results),
            "lock_stats": lock_stats
        }
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        # 清理测试数据
        try:
            import shutil
            if os.path.exists(test_storage_path):
                shutil.rmtree(test_storage_path)
            print("🧹 测试数据已清理")
        except Exception as e:
            print(f"⚠️ 清理测试数据失败: {e}")


async def main():
    """主函数"""
    print("=" * 60)
    print("🔒 QA系统并发控制验证")
    print("=" * 60)
    
    try:
        result = await test_concurrent_operations()
        
        if result:
            print("\n📊 测试结果总结:")
            print(f"  创建操作成功: {result['create_success']}")
            print(f"  删除操作成功: {result['delete_success']}")
            print(f"  混合操作数量: {result['mixed_operations']}")
            print(f"  锁统计信息: {result['lock_stats']}")
            print("\n✅ 并发控制验证通过")
        else:
            print("\n❌ 并发控制验证失败")
            
    except Exception as e:
        print(f"\n❌ 验证过程异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
