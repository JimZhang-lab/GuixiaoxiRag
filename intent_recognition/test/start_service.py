#!/usr/bin/env python3
"""
意图识别服务启动脚本
"""
import sys
import os
import logging
import uvicorn
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from api.server import create_intent_app
from config.settings import IntentRecognitionConfig


def setup_logging(log_level: str = "INFO"):
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('intent_recognition.log')
        ]
    )


def main():
    """主函数"""
    print("🚀 意图识别服务启动器")
    print("=" * 50)
    
    # 加载配置
    try:
        config = IntentRecognitionConfig.from_env()
        print(f"✅ 配置加载成功")
        print(f"   • 服务地址: {config.host}:{config.port}")
        print(f"   • 日志级别: {config.log_level}")
        print(f"   • LLM启用: {config.llm_enabled}")
        print(f"   • 安全检查: {config.enable_safety_check}")
        print(f"   • 查询增强: {config.enable_query_enhancement}")
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        sys.exit(1)
    
    # 设置日志
    setup_logging(config.log_level)
    logger = logging.getLogger(__name__)
    
    # 创建应用
    try:
        app = create_intent_app(config)
        logger.info("意图识别应用创建成功")
    except Exception as e:
        logger.error(f"应用创建失败: {e}")
        sys.exit(1)
    
    print("\n🌟 启动配置:")
    print(f"   • 服务地址: http://{config.host}:{config.port}")
    print(f"   • API文档: http://{config.host}:{config.port}/docs")
    print(f"   • 健康检查: http://{config.host}:{config.port}/health")
    print(f"   • 服务信息: http://{config.host}:{config.port}/info")
    
    print("\n🎯 快速测试:")
    print(f"   curl http://{config.host}:{config.port}/health")
    print(f"   curl -X POST http://{config.host}:{config.port}/analyze \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"query\": \"什么是人工智能？\"}}'")
    
    print("\n⚡ 按 Ctrl+C 停止服务")
    print("=" * 50)
    
    # 启动服务
    try:
        uvicorn.run(
            app,
            host=config.host,
            port=config.port,
            log_level=config.log_level.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("服务被用户中断")
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
