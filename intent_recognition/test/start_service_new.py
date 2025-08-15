#!/usr/bin/env python3
"""
意图识别服务启动脚本（新版本）
"""
import sys
import os
import logging
import uvicorn
import yaml
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from api.server import create_intent_app
from config.settings import Config


def setup_logging(config: Config):
    """设置日志"""
    log_level = getattr(logging, config.logging.level.upper())
    
    # 创建日志处理器
    handlers = [logging.StreamHandler(sys.stdout)]
    
    # 添加文件处理器
    if config.logging.file:
        try:
            # 确保日志目录存在
            log_file = Path(config.logging.file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(config.logging.file)
            handlers.append(file_handler)
        except Exception as e:
            print(f"⚠️ 无法创建日志文件: {e}")
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers
    )


def print_config_info(config: Config):
    """打印配置信息"""
    print("✅ 配置加载成功")
    print(f"   • 服务名称: {config.service.name}")
    print(f"   • 服务版本: {config.service.version}")
    print(f"   • 服务地址: {config.service.host}:{config.service.port}")
    print(f"   • 日志级别: {config.logging.level}")
    print(f"   • LLM启用: {config.llm.enabled}")
    if config.llm.enabled:
        print(f"   • LLM提供商: {config.llm.provider}")
    print(f"   • 安全检查: {config.safety.enabled}")
    print(f"   • 查询增强: {config.intent.enhancement.get('enabled', True)}")
    print(f"   • 缓存启用: {config.cache.enabled}")
    print(f"   • 微服务模式: {config.is_microservice_mode()}")
    if config.is_microservice_mode():
        print(f"   • 服务注册: {config.microservice.registry.get('enabled', False)}")
        print(f"   • 服务发现: {config.microservice.discovery.get('enabled', False)}")
    print(f"   • 性能监控: {config.performance.enable_metrics}")
    print(f"   • API文档: {config.api.docs.get('enabled', True)}")


def print_startup_info(config: Config):
    """打印启动信息"""
    print("\n🌟 启动配置:")
    print(f"   • 服务地址: http://{config.service.host}:{config.service.port}")
    print(f"   • API文档: http://{config.service.host}:{config.service.port}/docs")
    print(f"   • 健康检查: http://{config.service.host}:{config.service.port}/health")
    print(f"   • 服务信息: http://{config.service.host}:{config.service.port}/info")
    
    print("\n🎯 快速测试:")
    print(f"   curl http://{config.service.host}:{config.service.port}/health")
    print(f"   curl -X POST http://{config.service.host}:{config.service.port}/analyze \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"query\": \"什么是人工智能？\"}}'")
    
    if config.llm.enabled:
        print(f"\n🧠 LLM配置:")
        print(f"   • 提供商: {config.llm.provider}")
        try:
            llm_config = config.get_llm_config()
            if config.llm.provider == "openai":
                print(f"   • API地址: {llm_config.get('api_base', 'N/A')}")
                print(f"   • 模型: {llm_config.get('model', 'N/A')}")
            elif config.llm.provider == "azure":
                print(f"   • API地址: {llm_config.get('api_base', 'N/A')}")
                print(f"   • 部署名称: {llm_config.get('deployment_name', 'N/A')}")
            elif config.llm.provider == "ollama":
                print(f"   • API地址: {llm_config.get('api_base', 'N/A')}")
                print(f"   • 模型: {llm_config.get('model', 'N/A')}")
        except Exception as e:
            print(f"   • 配置获取失败: {e}")


def main():
    """主函数"""
    print("🚀 意图识别服务启动器（配置化版本）")
    print("=" * 60)
    
    # 加载配置
    try:
        config = Config.load_from_yaml()
        print_config_info(config)
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        print("💡 请检查 config.yaml 文件是否存在且格式正确")
        sys.exit(1)
    
    # 设置日志
    try:
        setup_logging(config)
        logger = logging.getLogger(__name__)
        logger.info("日志系统初始化完成")
    except Exception as e:
        print(f"❌ 日志设置失败: {e}")
        sys.exit(1)
    
    # 创建应用
    try:
        app = create_intent_app(config)
        logger.info("意图识别应用创建成功")
    except Exception as e:
        logger.error(f"应用创建失败: {e}")
        print(f"❌ 应用创建失败: {e}")
        sys.exit(1)
    
    print_startup_info(config)
    
    print("\n⚡ 按 Ctrl+C 停止服务")
    print("=" * 60)
    
    # 启动服务
    try:
        uvicorn.run(
            app,
            host=config.service.host,
            port=config.service.port,
            log_level=config.logging.level.lower(),
            workers=1,
            reload=config.service.debug,
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("服务被用户中断")
        print("\n👋 服务已停止")
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        print(f"❌ 服务启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
