#!/usr/bin/env python3
"""
验证并发控制相关的导入和基本功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试导入"""
    print("🔍 验证并发控制相关导入...")
    
    try:
        # 测试QA并发管理器导入
        from core.quick_qa_base.qa_concurrency_manager import QAConcurrencyManager
        print("✅ QAConcurrencyManager 导入成功")
        
        # 测试基本方法
        print("🔒 测试锁管理器基本功能...")
        
        # 获取锁统计
        stats = QAConcurrencyManager.get_lock_stats()
        print(f"📊 锁统计: {stats}")
        
        # 测试分类存储导入
        from core.quick_qa_base.category_qa_storage import CategoryQAStorage
        print("✅ CategoryQAStorage 导入成功")
        
        print("🎉 所有导入验证通过")
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 验证过程异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_lock_manager():
    """测试锁管理器"""
    print("\n🔒 测试锁管理器功能...")
    
    try:
        from core.quick_qa_base.qa_concurrency_manager import QAConcurrencyManager
        
        # 测试获取分类锁
        print("📝 测试分类锁获取...")
        
        import asyncio
        
        async def test_category_lock():
            async with QAConcurrencyManager.get_category_lock("test_category", "create", enable_logging=True):
                print("✅ 成功获取分类锁")
                return True
        
        # 运行异步测试
        result = asyncio.run(test_category_lock())
        
        if result:
            print("✅ 分类锁测试通过")
        else:
            print("❌ 分类锁测试失败")
            
        return result
        
    except Exception as e:
        print(f"❌ 锁管理器测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("🔍 QA并发控制导入验证")
    print("=" * 60)
    
    # 测试导入
    import_success = test_imports()
    
    if import_success:
        # 测试锁管理器
        lock_success = test_lock_manager()
        
        if lock_success:
            print("\n🎉 所有验证通过，并发控制功能正常")
        else:
            print("\n⚠️ 锁管理器测试失败")
    else:
        print("\n❌ 导入验证失败")


if __name__ == "__main__":
    main()
