#!/usr/bin/env python3
"""
GuiXiaoXiRag FastAPI 服务主启动文件
"""
import os
import sys
import asyncio
import argparse
import signal
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import uvicorn
    from server.config import settings, validate_config
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)


class GuiXiaoXiRagServer:
    """GuiXiaoXiRag服务器管理类"""
    
    def __init__(self):
        self.server_process = None
        self.is_running = False
    
    def check_dependencies(self):
        """检查依赖是否安装"""
        try:
            import fastapi
            import httpx
            import guixiaoxiRag
            print("✅ 依赖检查通过")
            return True
        except ImportError as e:
            print(f"❌ 缺少依赖: {e}")
            print("请运行: pip install -r requirements.txt")
            return False

    def check_config(self):
        """检查配置文件"""
        print("🔍 检查配置文件...")

        # 检查 .env 文件
        env_file = project_root / ".env"
        if not env_file.exists():
            print("⚠️  .env 文件不存在")
            env_example = project_root / ".env.example"
            if env_example.exists():
                print(f"📋 请复制 {env_example} 为 {env_file} 并修改配置")
            else:
                print("❌ .env.example 文件也不存在")
            return False

        # 验证配置
        config_valid = validate_config()
        if config_valid:
            print("✅ 配置验证通过")

        return config_valid
    
    def check_model_services(self):
        """检查大模型服务是否可用"""
        import httpx

        services = [
            ("LLM服务", settings.openai_api_base, settings.openai_chat_api_key),
            ("Embedding服务", settings.openai_embedding_api_base, settings.openai_embedding_api_key)
        ]

        print("🔍 检查模型服务状态:")
        for name, url, api_key in services:
            try:
                headers = {}
                if api_key and api_key != "your_api_key_here":
                    headers["Authorization"] = f"Bearer {api_key}"

                with httpx.Client(timeout=5) as client:
                    response = client.get(f"{url}/models", headers=headers)
                    if response.status_code == 200:
                        print(f"   ✅ {name} 可用 ({url})")
                    else:
                        print(f"   ⚠️ {name} 响应异常 (状态码: {response.status_code})")
                        if response.status_code == 401:
                            print(f"   💡 API密钥可能无效，请检查配置")
            except Exception as e:
                print(f"   ❌ {name} 不可用: {e}")
                print(f"   💡 请确保 {name} 正在运行在 {url}")
    
    def setup_directories(self):
        """创建必要的目录"""
        dirs = [
            settings.log_dir,
            settings.working_dir,
            "./uploads",
            "./knowledgeBase"
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        print("✅ 目录结构已创建")
    
    def setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            print(f"\n📡 接收到信号 {signum}，正在优雅关闭服务...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def start(self, host="0.0.0.0", port=8002, workers=1, reload=False, log_level="info"):
        """启动服务"""
        print("🚀 GuiXiaoXiRag FastAPI 服务启动器")
        print("=" * 60)
        
        # 检查依赖
        if not self.check_dependencies():
            return False
        
        # 设置目录
        self.setup_directories()
        
        # 检查模型服务
        self.check_model_services()
        
        # 设置信号处理
        self.setup_signal_handlers()
        
        print(f"\n🌟 启动配置:")
        print(f"   • 服务地址: http://{host}:{port}")
        print(f"   • API文档: http://{host}:{port}/docs")
        print(f"   • 工作目录: {settings.working_dir}")
        print(f"   • 日志目录: {settings.log_dir}")
        print(f"   • 工作进程: {workers}")
        print(f"   • 重载模式: {reload}")
        print(f"   • 日志级别: {log_level}")
        
        print(f"\n🎯 快速测试:")
        print(f"   curl http://{host}:{port}/health")
        
        print(f"\n📖 使用帮助:")
        print(f"   • 查看API文档: 浏览器打开 http://{host}:{port}/docs")
        print(f"   • 命令行工具: python scripts/guixiaoxirag_cli.py --help")
        print(f"   • Python客户端: 查看 examples/api_client.py")
        
        print(f"\n⚡ 按 Ctrl+C 停止服务")
        print("=" * 60)
        
        try:
            self.is_running = True
            
            # 启动uvicorn服务器
            uvicorn.run(
                "server.api:app",
                host=host,
                port=port,
                workers=workers,
                reload=reload,
                log_level=log_level.lower(),
                access_log=True,
                server_header=False,
                date_header=False
            )
            
        except KeyboardInterrupt:
            print("\n📡 接收到中断信号")
        except Exception as e:
            print(f"\n❌ 服务启动失败: {e}")
            return False
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """停止服务"""
        if self.is_running:
            print("🛑 正在停止服务...")
            self.is_running = False
            print("✅ 服务已停止")
    
    def status(self):
        """检查服务状态"""
        import httpx
        
        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(f"http://localhost:{settings.port}/health")
                if response.status_code == 200:
                    health = response.json()
                    print("✅ 服务正在运行")
                    print(f"   状态: {health.get('system', {}).get('status', 'unknown')}")
                    print(f"   运行时间: {health.get('system', {}).get('uptime', 0):.1f}秒")
                    return True
                else:
                    print(f"⚠️ 服务响应异常: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ 服务不可用: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="GuiXiaoXiRag FastAPI 服务启动器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s                                    # 使用默认配置启动
  %(prog)s --host 0.0.0.0 --port 8002        # 指定地址和端口
  %(prog)s --workers 4                       # 多进程模式
  %(prog)s --reload                          # 开发模式（自动重载）
  %(prog)s --log-level debug                 # 调试模式
  %(prog)s status                            # 检查服务状态

配置说明:
  • 默认地址: 0.0.0.0:8002
  • API文档: http://localhost:8002/docs
  • 健康检查: http://localhost:8002/health
  • 配置文件: server/config.py
        """
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        default="start",
        choices=["start", "status"],
        help="命令: start(启动服务) 或 status(检查状态)"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="绑定地址 (默认: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8002,
        help="绑定端口 (默认: 8002)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="工作进程数 (默认: 1)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="启用自动重载 (开发模式)"
    )
    
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="日志级别 (默认: info)"
    )
    
    args = parser.parse_args()
    
    # 创建服务器实例
    server = GuiXiaoXiRagServer()
    
    try:
        if args.command == "start":
            success = server.start(
                host=args.host,
                port=args.port,
                workers=args.workers,
                reload=args.reload,
                log_level=args.log_level
            )
            sys.exit(0 if success else 1)
        
        elif args.command == "status":
            success = server.status()
            sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
