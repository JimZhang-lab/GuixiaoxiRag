#!/usr/bin/env python3
"""
GuiXiaoXiRag 新服务器启动脚本
支持自定义参数配置
"""
import sys
import os
import subprocess
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

def get_project_root():
    """获取项目根目录"""
    return Path(__file__).parent.resolve()


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="GuiXiaoXiRag 服务器启动脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python strat.py                           # 使用默认配置启动
  python strat.py --host 127.0.0.1 --port 8003  # 自定义主机和端口
  python strat.py --debug --reload          # 开启调试模式和热重载
  python strat.py --workers 4               # 设置工作进程数
  python strat.py --config-only             # 仅检查配置不启动服务
  python strat.py --env-file .env.prod      # 使用指定的环境文件
        """
    )

    # 服务器配置
    server_group = parser.add_argument_group('服务器配置')
    server_group.add_argument(
        '--host',
        type=str,
        help='服务器主机地址 (默认: 0.0.0.0)'
    )
    server_group.add_argument(
        '--port',
        type=int,
        help='服务器端口 (默认: 8002)'
    )
    server_group.add_argument(
        '--workers',
        type=int,
        help='工作进程数 (默认: 1)'
    )
    server_group.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    server_group.add_argument(
        '--reload',
        action='store_true',
        help='启用热重载 (开发模式)'
    )

    # 配置文件
    config_group = parser.add_argument_group('配置选项')
    config_group.add_argument(
        '--env-file',
        type=str,
        help='指定环境配置文件路径'
    )
    config_group.add_argument(
        '--working-dir',
        type=str,
        help='知识库工作目录'
    )
    config_group.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='日志级别'
    )

    # 模型配置
    model_group = parser.add_argument_group('模型配置')
    model_group.add_argument(
        '--llm-api-base',
        type=str,
        help='LLM API 基础URL'
    )
    model_group.add_argument(
        '--llm-model',
        type=str,
        help='LLM 模型名称'
    )
    model_group.add_argument(
        '--embedding-api-base',
        type=str,
        help='Embedding API 基础URL'
    )
    model_group.add_argument(
        '--embedding-model',
        type=str,
        help='Embedding 模型名称'
    )

    # 操作选项
    action_group = parser.add_argument_group('操作选项')
    action_group.add_argument(
        '--config-only',
        action='store_true',
        help='仅检查配置，不启动服务器'
    )
    action_group.add_argument(
        '--skip-deps-check',
        action='store_true',
        help='跳过依赖检查'
    )
    action_group.add_argument(
        '--skip-env-check',
        action='store_true',
        help='跳过环境检查'
    )
    action_group.add_argument(
        '--version',
        action='store_true',
        help='显示版本信息'
    )

    return parser.parse_args()

def apply_custom_env_vars(args: argparse.Namespace):
    """根据命令行参数设置环境变量"""
    env_mappings = {
        'host': 'HOST',
        'port': 'PORT',
        'debug': 'DEBUG',
        'workers': 'WORKERS',
        'working_dir': 'WORKING_DIR',
        'log_level': 'LOG_LEVEL',
        'llm_api_base': 'OPENAI_API_BASE',
        'llm_model': 'OPENAI_CHAT_MODEL',
        'embedding_api_base': 'OPENAI_EMBEDDING_API_BASE',
        'embedding_model': 'OPENAI_EMBEDDING_MODEL'
    }

    for arg_name, env_name in env_mappings.items():
        value = getattr(args, arg_name, None)
        if value is not None:
            if isinstance(value, bool):
                os.environ[env_name] = str(value).lower()
            else:
                os.environ[env_name] = str(value)
            print(f"🔧 设置环境变量: {env_name}={value}")


def load_custom_env_file(env_file_path: str):
    """加载自定义环境文件"""
    env_path = Path(env_file_path)
    if not env_path.exists():
        print(f"❌ 环境文件不存在: {env_path}")
        return False

    try:
        # 简单的 .env 文件解析
        with open(env_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value

        print(f"✅ 已加载环境文件: {env_path}")
        return True
    except Exception as e:
        print(f"❌ 加载环境文件失败: {e}")
        return False


def show_version_info():
    """显示版本信息"""
    print("🎯 GuiXiaoXiRag 服务器启动器")
    print("=" * 50)
    print(f"Python 版本: {sys.version}")
    print(f"脚本路径: {Path(__file__).resolve()}")
    print(f"工作目录: {get_project_root()}")

    # 尝试获取应用版本
    try:
        sys.path.insert(0, str(get_project_root()))
        from common.config import settings
        print(f"应用版本: {settings.app_version}")
        print(f"应用名称: {settings.app_name}")
    except ImportError:
        print("应用版本: 无法获取 (配置模块未找到)")


def show_startup_banner(config: Dict[str, Any]):
    """显示启动横幅"""
    print("🎯 GuiXiaoXiRag 智能知识图谱问答系统")
    print("=" * 60)
    print("🚀 正在启动服务...")
    print()

    # 显示关键配置
    print("📋 关键配置:")
    print(f"   🌐 服务地址: http://{config['host']}:{config['port']}")
    print(f"   📁 工作目录: {config['working_dir']}")
    print(f"   📊 日志级别: {config['log_level']}")
    if config['debug']:
        print("   🐛 调试模式: 已启用")
    if config['reload']:
        print("   🔄 热重载: 已启用")
    print()


def show_quick_help():
    """显示快速帮助信息"""
    print("🎯 GuiXiaoXiRag 服务器启动器 - 快速帮助")
    print("=" * 50)
    print("常用命令:")
    print("  python strat.py                    # 默认启动")
    print("  python strat.py --help             # 显示完整帮助")
    print("  python strat.py --version          # 显示版本信息")
    print("  python strat.py --config-only      # 仅检查配置")
    print("  python strat.py --debug --reload   # 开发模式")
    print("  python strat.py --port 8003        # 自定义端口")
    print()
    print("更多选项请使用 --help 查看")


def validate_server_config(config: Dict[str, Any]) -> bool:
    """验证服务器配置"""
    errors = []

    # 验证端口
    if not (1 <= config['port'] <= 65535):
        errors.append(f"端口号无效: {config['port']} (必须在 1-65535 范围内)")

    # 验证工作进程数
    if config['workers'] < 1:
        errors.append(f"工作进程数无效: {config['workers']} (必须大于 0)")

    # 验证日志级别
    valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    if config['log_level'].upper() not in valid_log_levels:
        errors.append(f"日志级别无效: {config['log_level']} (支持: {', '.join(valid_log_levels)})")

    # 验证工作目录
    try:
        working_dir = Path(config['working_dir'])
        working_dir.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        errors.append(f"工作目录无效: {config['working_dir']} ({e})")

    # 输出错误
    if errors:
        print("❌ 配置验证失败:")
        for error in errors:
            print(f"   - {error}")
        return False

    return True


def get_server_config(args: argparse.Namespace) -> Dict[str, Any]:
    """获取服务器配置"""
    try:
        # 确保项目路径在 Python 路径中
        project_root = get_project_root()
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from common.config import settings

        # 使用命令行参数覆盖配置
        config = {
            'host': args.host or settings.host,
            'port': args.port or settings.port,
            'workers': args.workers or settings.workers,
            'debug': args.debug or settings.debug,
            'reload': args.reload or (args.debug or settings.debug),
            'working_dir': args.working_dir or settings.working_dir,
            'log_level': args.log_level or settings.log_level
        }

        # 验证配置
        if not validate_server_config(config):
            print("💡 请检查配置参数并重试")
            sys.exit(1)

        return config
    except ImportError:
        # 如果无法导入配置，使用默认值
        config = {
            'host': args.host or '0.0.0.0',
            'port': args.port or 8002,
            'workers': args.workers or 1,
            'debug': args.debug or False,
            'reload': args.reload or args.debug,
            'working_dir': args.working_dir or './knowledgeBase/default',
            'log_level': args.log_level or 'INFO'
        }

        # 验证配置
        if not validate_server_config(config):
            print("💡 请检查配置参数并重试")
            sys.exit(1)

        return config

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查 Python 版本
    if sys.version_info < (3, 8):
        print(f"❌ Python 版本过低: {sys.version}")
        print("   需要 Python 3.8+")
        return False
    
    print(f"✅ Python 版本: {sys.version}")
    
    # 检查 server_new 目录
    # server_new_path = get_server_new_path()
    # if not server_new_path.exists():
    #     print(f"❌ server_new 目录不存在: {server_new_path}")
    #     return False
    
    # print(f"✅ server_new 目录: {server_new_path}")
    
    # 获取工作目录
    work_path = get_project_root()
    
    # 检查 main.py 文件
    main_py = work_path / "main.py"
    if not main_py.exists():
        print(f"❌ main.py 文件不存在: {main_py}")
        return False
    
    print(f"✅ main.py 文件: {main_py}")
    
    return True

def check_dependencies():
    """检查依赖"""
    print("📦 检查依赖...")
    
    try:
        import fastapi
        print(f"✅ FastAPI: {fastapi.__version__}")
    except ImportError:
        print("❌ FastAPI 未安装")
        return False
    
    try:
        import uvicorn
        print(f"✅ Uvicorn: {uvicorn.__version__}")
    except ImportError:
        print("❌ Uvicorn 未安装")
        return False
    
    return True

def setup_environment():
    """设置环境"""
    print("⚙️  设置环境...")
    
    project_root = get_project_root()
    # server_new_path = get_server_new_path()
    
    # 添加路径到 Python 路径
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # if str(server_new_path) not in sys.path:
    #     sys.path.insert(0, str(server_new_path))
    
    # 设置环境变量
    os.environ.setdefault("PYTHONPATH", f"{project_root}:{project_root}")
    
    # 切换到 server_new 目录
    # os.chdir(server_new_path)
    
    print(f"✅ 工作目录: {os.getcwd()}")
    print(f"✅ Python 路径已设置")

def check_config():
    """检查配置文件"""
    print("📋 检查配置...")
    
    project_root = get_project_root()
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if env_file.exists():
        print(f"✅ 配置文件: {env_file}")
    elif env_example.exists():
        print(f"⚠️  未找到 .env 文件，但找到了 .env.example")
        print(f"💡 建议复制 {env_example} 为 {env_file} 并修改配置")
    else:
        print("⚠️  未找到配置文件，将使用默认配置")
    
    return True

def start_server(config: Dict[str, Any]):
    """启动服务器"""
    print("🚀 启动 GuiXiaoXiRag 服务器...")
    print("=" * 50)

    # 显示配置信息
    print("📋 服务器配置:")
    print(f"   - 主机地址: {config['host']}")
    print(f"   - 端口: {config['port']}")
    print(f"   - 工作进程数: {config['workers']}")
    print(f"   - 调试模式: {config['debug']}")
    print(f"   - 热重载: {config['reload']}")
    print(f"   - 工作目录: {config['working_dir']}")
    print(f"   - 日志级别: {config['log_level']}")
    print()

    try:
        project_root = get_project_root()

        # 设置环境变量
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{project_root}:{project_root}"

        # 构建 uvicorn 启动命令
        cmd = [
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", config['host'],
            "--port", str(config['port']),
        ]

        # 添加可选参数
        if config['reload']:
            cmd.append("--reload")

        if config['workers'] > 1 and not config['reload']:
            cmd.extend(["--workers", str(config['workers'])])

        # 设置日志级别
        log_level = config['log_level'].lower()
        cmd.extend(["--log-level", log_level])

        print(f"💡 启动命令: {' '.join(cmd)}")
        print("\n📚 API 文档地址:")
        print(f"   - Swagger UI: http://{config['host']}:{config['port']}/docs")
        print(f"   - ReDoc: http://{config['host']}:{config['port']}/redoc")
        print(f"   - OpenAPI JSON: http://{config['host']}:{config['port']}/openapi.json")

        # 如果是本地地址，也显示 localhost 链接
        if config['host'] in ['0.0.0.0', '127.0.0.1']:
            print(f"   - 本地访问: http://localhost:{config['port']}/docs")

        print("=" * 50)

        result = subprocess.run(cmd, cwd=project_root, env=env)

        if result.returncode != 0:
            print(f"❌ 服务器退出，返回码: {result.returncode}")
            return False

    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

def main():
    """主函数"""
    try:
        # 解析命令行参数
        args = parse_arguments()

        # 处理版本信息
        if args.version:
            show_version_info()
            return

        # 加载自定义环境文件
        if args.env_file:
            if not load_custom_env_file(args.env_file):
                sys.exit(1)

        # 应用命令行参数到环境变量
        apply_custom_env_vars(args)

        # 获取服务器配置
        config = get_server_config(args)

        # 显示启动横幅
        show_startup_banner(config)

        # 检查环境
        if not args.skip_env_check:
            if not check_environment():
                print("\n❌ 环境检查失败")
                sys.exit(1)

        # 检查依赖
        if not args.skip_deps_check:
            if not check_dependencies():
                print("\n❌ 依赖检查失败")
                print("💡 请运行: pip install -r requirements.txt")
                sys.exit(1)

        # 检查配置
        if not check_config():
            print("\n❌ 配置检查失败")
            sys.exit(1)

        # 如果只是检查配置，则退出
        if args.config_only:
            print("\n✅ 配置检查完成")
            print("📋 当前配置:")
            for key, value in config.items():
                print(f"   - {key}: {value}")
            return

        # 设置环境
        setup_environment()

        # 启动服务器
        if not start_server(config):
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n👋 用户中断，退出程序")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
