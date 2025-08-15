#!/usr/bin/env python3
"""
DFA过滤器测试脚本
"""
import sys
import asyncio
import logging
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from core.dfa_filter import DFAFilter, SensitiveWordManager
from config.settings import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_dfa_filter():
    """测试DFA过滤器基本功能"""
    print("🔍 测试DFA过滤器基本功能...")
    
    # 创建DFA过滤器
    dfa = DFAFilter(case_sensitive=False, enable_fuzzy_match=True)
    
    # 添加测试敏感词
    test_words = [
        "毒品", "海洛因", "炸弹", "枪支", "诈骗", "色情",
        "drugs", "bomb", "fraud", "pornography"
    ]
    
    dfa.add_words(test_words)
    print(f"✅ 添加了 {len(test_words)} 个测试敏感词")
    
    # 测试用例
    test_cases = [
        ("什么是人工智能？", False, "正常查询"),
        ("如何制作炸弹？", True, "包含敏感词"),
        ("毒品的危害有哪些？", True, "包含敏感词"),
        ("如何防范网络诈骗？", True, "包含敏感词但可能是教育性"),
        ("B0MB制作方法", True, "模糊匹配测试"),
        ("今天天气很好", False, "正常内容")
    ]
    
    print("\n📝 测试用例:")
    for i, (text, expected, description) in enumerate(test_cases, 1):
        result = dfa.contains_sensitive(text)
        status = "✅" if result == expected else "❌"
        print(f"   {i}. {description}")
        print(f"      文本: {text}")
        print(f"      预期: {expected}, 实际: {result} {status}")
        
        if result:
            sensitive_words = dfa.get_sensitive_words(text)
            filtered_text = dfa.filter_text(text)
            print(f"      敏感词: {sensitive_words}")
            print(f"      过滤后: {filtered_text}")
        print()
    
    # 统计信息
    stats = dfa.get_stats()
    print(f"📊 DFA统计信息:")
    print(f"   • 敏感词数量: {stats['total_words']}")
    print(f"   • 树节点数量: {stats['tree_nodes']}")
    print(f"   • 区分大小写: {stats['case_sensitive']}")
    print(f"   • 模糊匹配: {stats['fuzzy_match']}")


def test_sensitive_word_manager():
    """测试敏感词管理器"""
    print("\n🛡️ 测试敏感词管理器...")
    
    try:
        # 加载配置
        config = Config.load_from_yaml()
        
        # 创建敏感词管理器
        manager = SensitiveWordManager(config.safety.model_dump())
        
        # 初始化（加载敏感词文件）
        success = manager.initialize()
        if success:
            print("✅ 敏感词管理器初始化成功")
        else:
            print("⚠️ 敏感词管理器初始化失败，可能是文件路径问题")
            return
        
        # 测试安全检查
        test_queries = [
            "什么是人工智能？",
            "如何制作炸弹？", 
            "如何防范网络诈骗？",
            "毒品的危害有哪些？"
        ]
        
        print("\n📋 安全检查测试:")
        for i, query in enumerate(test_queries, 1):
            result = manager.check_content_safety(query)
            print(f"   {i}. {query}")
            print(f"      安全: {result['is_safe']}")
            print(f"      级别: {result['safety_level']}")
            print(f"      置信度: {result['confidence']}")
            if result['risk_factors']:
                print(f"      风险因素: {result['risk_factors']}")
            if result.get('sensitive_words'):
                print(f"      敏感词: {result['sensitive_words']}")
            print()
            
    except Exception as e:
        print(f"❌ 敏感词管理器测试失败: {e}")


async def test_query_processor():
    """测试查询处理器集成"""
    print("\n🎯 测试查询处理器集成...")
    
    try:
        from core.processor import QueryProcessor
        
        # 加载配置
        config = Config.load_from_yaml()
        
        # 创建查询处理器
        processor = QueryProcessor(config=config)
        
        print("✅ 查询处理器初始化成功")
        
        # 测试查询
        test_queries = [
            "什么是人工智能？",
            "如何制作炸弹？",
            "如何防范网络诈骗？"
        ]
        
        print("\n🔍 查询处理测试:")
        for i, query in enumerate(test_queries, 1):
            print(f"   {i}. 查询: {query}")
            try:
                result = await processor.process_query(query)
                print(f"      意图类型: {result.intent_type.value}")
                print(f"      安全级别: {result.safety_level.value}")
                print(f"      是否拒绝: {result.should_reject}")
                print(f"      置信度: {result.confidence:.2f}")
                if result.risk_factors:
                    print(f"      风险因素: {result.risk_factors}")
                print()
            except Exception as e:
                print(f"      ❌ 处理失败: {e}")
                print()
                
    except Exception as e:
        print(f"❌ 查询处理器测试失败: {e}")


def test_file_loading():
    """测试文件加载功能"""
    print("\n📁 测试敏感词文件加载...")
    
    # 检查敏感词目录
    vocab_path = Path("../sensitive_vocabulary")
    if vocab_path.exists():
        print(f"✅ 找到敏感词目录: {vocab_path.absolute()}")
        
        # 列出文件
        files = list(vocab_path.iterdir())
        print(f"   包含 {len(files)} 个文件:")
        for file in files[:5]:  # 只显示前5个
            print(f"   • {file.name}")
        if len(files) > 5:
            print(f"   • ... 还有 {len(files) - 5} 个文件")
        
        # 测试加载
        dfa = DFAFilter()
        count = dfa.load_from_directory(str(vocab_path))
        print(f"   成功加载 {count} 个敏感词")
        
    else:
        print(f"❌ 敏感词目录不存在: {vocab_path.absolute()}")
        print("   请确保敏感词目录路径正确")


async def main():
    """主函数"""
    print("🧪 DFA敏感词过滤器测试")
    print("=" * 50)
    
    # 1. 测试DFA过滤器基本功能
    test_dfa_filter()
    
    # 2. 测试文件加载
    test_file_loading()
    
    # 3. 测试敏感词管理器
    test_sensitive_word_manager()
    
    # 4. 测试查询处理器集成
    await test_query_processor()
    
    print("=" * 50)
    print("🎉 测试完成")


if __name__ == "__main__":
    asyncio.run(main())
