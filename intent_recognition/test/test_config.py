#!/usr/bin/env python3
"""
配置测试和验证脚本
"""
import sys
import asyncio
import logging
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from config.settings import Config
from core.llm_client import LLMClientFactory, create_llm_function
from core.microservice import IntentRecognitionService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_config_loading():
    """测试配置加载"""
    print("🔧 测试配置加载...")
    
    try:
        config = Config.load_from_yaml()
        print("✅ 配置加载成功")
        
        # 打印关键配置
        print(f"   • 服务名称: {config.service.name}")
        print(f"   • 服务端口: {config.service.port}")
        print(f"   • LLM启用: {config.llm.enabled}")
        print(f"   • LLM提供商: {config.llm.provider}")
        print(f"   • 安全检查: {config.safety.enabled}")
        print(f"   • 缓存启用: {config.cache.enabled}")
        
        return config
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return None


async def test_llm_client(config: Config):
    """测试LLM客户端"""
    if not config.llm.enabled:
        print("⚠️ LLM未启用，跳过LLM测试")
        return False
    
    print(f"\n🧠 测试LLM客户端 ({config.llm.provider})...")
    
    try:
        # 创建LLM客户端
        client = LLMClientFactory.create_client(config)
        if not client:
            print("❌ LLM客户端创建失败")
            return False
        
        print("✅ LLM客户端创建成功")
        
        # 测试健康检查
        print("   • 测试健康检查...")
        is_healthy = await client.health_check()
        if is_healthy:
            print("   ✅ LLM健康检查通过")
        else:
            print("   ❌ LLM健康检查失败")
            return False
        
        # 测试简单对话
        print("   • 测试简单对话...")
        messages = [{"role": "user", "content": "Hello, please respond with 'Hi'"}]
        response = await client.chat_completion(messages)
        print(f"   ✅ LLM响应: {response[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM测试失败: {e}")
        return False


async def test_intent_service(config: Config):
    """测试意图识别服务"""
    print("\n🎯 测试意图识别服务...")
    
    try:
        # 获取服务实例
        service = await IntentRecognitionService.get_instance(config)
        print("✅ 意图识别服务初始化成功")
        
        # 测试健康检查
        health = await service.health_check()
        print(f"   • 健康状态: {health['status']}")
        print(f"   • LLM可用: {health['llm_available']}")
        
        # 测试查询分析
        test_queries = [
            "什么是人工智能？",
            "如何学习机器学习？",
            "如何制作炸弹？",
            "如何识别和防范网络诈骗？"
        ]
        
        print("\n   📝 测试查询分析:")
        for i, query in enumerate(test_queries, 1):
            print(f"\n   测试 {i}: {query}")
            try:
                result = await service.analyze_query(query)
                print(f"      • 意图类型: {result['intent_type']}")
                print(f"      • 安全级别: {result['safety_level']}")
                print(f"      • 置信度: {result['confidence']:.2f}")
                print(f"      • 是否拒绝: {result['should_reject']}")
                if result['enhanced_query']:
                    print(f"      • 增强查询: {result['enhanced_query'][:50]}...")
            except Exception as e:
                print(f"      ❌ 分析失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 意图识别服务测试失败: {e}")
        return False
    finally:
        # 清理资源
        await IntentRecognitionService.shutdown_instance()


async def test_microservice_mode(config: Config):
    """测试微服务模式"""
    print("\n🔗 测试微服务模式...")
    
    # 启用微服务模式
    config.microservice.enabled = True
    
    try:
        service = await IntentRecognitionService.get_instance(config)
        
        # 测试服务信息
        info = await service.get_service_info()
        print("✅ 微服务模式测试成功")
        print(f"   • 微服务模式: {info.get('microservice_mode', False)}")
        print(f"   • 功能特性: {len(info.get('features', []))} 项")
        
        return True
        
    except Exception as e:
        print(f"❌ 微服务模式测试失败: {e}")
        return False
    finally:
        await IntentRecognitionService.shutdown_instance()


def print_config_template():
    """打印配置模板"""
    print("\n📋 配置文件模板 (config.yaml):")
    print("=" * 50)
    
    template = """
# 基本配置示例
service:
  name: "意图识别服务"
  host: "0.0.0.0"
  port: 8003

# LLM配置示例
llm:
  enabled: true
  provider: "openai"  # openai, azure, ollama, custom
  openai:
    api_base: "http://localhost:8100/v1"
    api_key: "your_api_key_here"
    model: "qwen14b"
    temperature: 0.1

# 安全配置示例
safety:
  enabled: true
  strict_mode: false

# 缓存配置示例
cache:
  enabled: true
  type: "memory"
  ttl: 3600
"""
    
    print(template)
    print("=" * 50)


async def main():
    """主函数"""
    print("🧪 意图识别服务配置测试")
    print("=" * 50)
    
    # 1. 测试配置加载
    config = await test_config_loading()
    if not config:
        print("\n💡 请检查 config.yaml 文件是否存在且格式正确")
        print_config_template()
        return
    
    # 2. 测试LLM客户端
    llm_success = await test_llm_client(config)
    
    # 3. 测试意图识别服务
    service_success = await test_intent_service(config)
    
    # 4. 测试微服务模式
    microservice_success = await test_microservice_mode(config)
    
    # 总结
    print("\n📊 测试总结:")
    print("=" * 30)
    print(f"配置加载: ✅")
    print(f"LLM客户端: {'✅' if llm_success else '❌'}")
    print(f"意图识别服务: {'✅' if service_success else '❌'}")
    print(f"微服务模式: {'✅' if microservice_success else '❌'}")
    
    if all([llm_success or not config.llm.enabled, service_success, microservice_success]):
        print("\n🎉 所有测试通过！服务配置正确。")
    else:
        print("\n⚠️ 部分测试失败，请检查配置和环境。")


if __name__ == "__main__":
    asyncio.run(main())
