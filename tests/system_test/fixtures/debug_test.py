#!/usr/bin/env python3
"""
DEBUG测试脚本
专门用于测试详细的DEBUG日志功能
"""

import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from runners.sync_test_runner import SyncTestRunner
from utils.test_logger import TestLogger


def test_debug_logging():
    """测试DEBUG日志功能"""
    
    # 创建详细模式的logger
    logger = TestLogger("DebugTest")
    logger.set_verbose(True)
    
    logger.section("🔍 DEBUG日志测试")
    
    # 测试各种日志级别
    logger.debug("这是一条DEBUG日志")
    logger.info("这是一条INFO日志")
    logger.warning("这是一条WARNING日志")
    logger.error("这是一条ERROR日志")
    
    # 测试测试相关的日志方法
    logger.test_start("示例测试")
    logger.debug("测试开始的详细信息")
    logger.test_pass("示例测试", 1.23)
    
    logger.test_start("另一个测试")
    logger.debug("这个测试会失败")
    logger.test_fail("另一个测试", "示例错误", 0.5)
    
    logger.test_skip("跳过的测试", "示例跳过原因")
    
    # 测试进度日志
    for i in range(1, 4):
        logger.progress(i, 3, f"步骤{i}")
        logger.debug(f"步骤{i}的详细信息")
    
    # 测试摘要
    logger.summary(3, 1, 1, 1)
    
    print(f"\n日志文件位置: {logger.get_log_file()}")


def test_single_api_call():
    """测试单个API调用的详细日志"""
    
    # 创建测试运行器
    runner = SyncTestRunner(
        base_url="http://localhost:8002",
        timeout=30,
        output_dir="logs",
        skip_text_insert=True
    )
    
    # 设置详细模式
    runner.logger.set_verbose(True)
    
    runner.logger.section("🔍 单个API调用DEBUG测试")
    
    # 只测试系统健康检查
    result = runner.test_system_health_check()
    
    runner.logger.debug(f"测试结果: {result}")
    
    print(f"\n日志文件位置: {runner.logger.get_log_file()}")
    
    return result


def main():
    """主函数"""
    print("🔍 DEBUG日志测试工具")
    print("=" * 50)
    
    # 测试基本的DEBUG日志功能
    print("\n1. 测试基本DEBUG日志功能...")
    test_debug_logging()
    
    # 测试单个API调用的详细日志
    print("\n2. 测试单个API调用的详细日志...")
    try:
        result = test_single_api_call()
        if result.get("success", False):
            print("✅ API调用成功")
        else:
            print(f"❌ API调用失败: {result.get('error', '未知错误')}")
    except Exception as e:
        print(f"❌ 测试异常: {e}")
    
    print("\n🎉 DEBUG测试完成")
    print("请检查生成的日志文件以查看详细的DEBUG信息")


if __name__ == "__main__":
    main()
