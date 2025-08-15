#!/usr/bin/env python3
"""
意图识别服务主入口
"""
import sys
import asyncio
import argparse
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from config.settings import Config
from api.server import create_app
import uvicorn
import logging

logger = logging.getLogger(__name__)


def setup_logging(config: Config):
    """设置日志"""
    try:
        log_level = getattr(logging, config.logging.level.upper())
        
        # 配置日志处理器
        handlers = [logging.StreamHandler()]
        if config.logging.file:
            log_file = Path(config.logging.file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
        
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=handlers
        )
        
        logger.info("日志系统初始化完成")
        return True
        
    except Exception as e:
        print(f"❌ 日志设置失败: {e}")
        return False


def print_startup_info(config: Config):
    """打印启动信息"""
    print("🚀 意图识别服务")
    print("=" * 60)
    print("✅ 配置加载成功")
    print(f"   • 服务名称: {config.service.name}")
    print(f"   • 服务版本: {config.service.version}")
    print(f"   • 服务地址: {config.service.host}:{config.service.port}")
    print(f"   • 日志级别: {config.logging.level}")
    print(f"   • LLM启用: {config.llm.enabled}")
    print(f"   • 安全检查: {config.safety.enabled}")
    print(f"   • 缓存启用: {config.cache.enabled}")
    print(f"   • 微服务模式: {config.is_microservice_mode()}")
    print(f"   • 性能监控: {config.performance.enable_metrics}")
    print(f"   • API文档: {config.api.docs.get('enabled', True)}")
    print()
    
    print("🌟 服务端点:")
    print(f"   • 服务地址: http://{config.service.host}:{config.service.port}")
    print(f"   • API文档: http://{config.service.host}:{config.service.port}/docs")
    print(f"   • 健康检查: http://{config.service.host}:{config.service.port}/health")
    print(f"   • 服务信息: http://{config.service.host}:{config.service.port}/info")
    print()
    
    # print("🎯 快速测试:")
    # print(f"   curl http://{config.service.host}:{config.service.port}/health")
    # print(f"   curl -X POST http://{config.service.host}:{config.service.port}/analyze \\")
    # print("     -H 'Content-Type: application/json' \\")
    # print("     -d '{\"query\": \"什么是人工智能？\"}'")
    # print()
    # print("⚡ 按 Ctrl+C 停止服务")
    # print("=" * 60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="意图识别服务")
    parser.add_argument("--config", "-c", default="config.yaml", help="配置文件路径")
    parser.add_argument("--host", default=None, help="服务主机")
    parser.add_argument("--port", type=int, default=None, help="服务端口")
    parser.add_argument("--debug", action="store_true", help="调试模式")
    parser.add_argument("--test", action="store_true", help="运行测试")
    
    args = parser.parse_args()
    
    try:
        # 加载配置
        config = Config.load_from_yaml(args.config)
        
        # 命令行参数覆盖配置
        if args.host:
            config.service.host = args.host
        if args.port:
            config.service.port = args.port
        if args.debug:
            config.service.debug = True
            config.logging.level = "DEBUG"
        
        # 设置日志
        if not setup_logging(config):
            return 1
        
        # 运行测试
        if args.test:
            from test.test_config import main as test_main
            return asyncio.run(test_main())
        
        # 打印启动信息
        print_startup_info(config)
        
        # 创建应用
        app = create_app(config)
        logger.info("意图识别应用创建成功")
        
        # 启动服务
        uvicorn.run(
            app,
            host=config.service.host,
            port=config.service.port,
            log_level=config.logging.level.lower(),
            workers=1,
            reload=config.service.debug,
            access_log=True
        )
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("服务被用户中断")
        return 0
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        print(f"❌ 服务启动失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
