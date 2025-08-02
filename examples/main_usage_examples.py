#!/usr/bin/env python3
"""
main.py 主启动文件使用示例
演示不同的启动方式和配置选项
"""
import subprocess
import time
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n🔧 {description}")
    print(f"命令: {cmd}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ 执行成功")
            if result.stdout:
                print(f"输出:\n{result.stdout}")
        else:
            print("❌ 执行失败")
            if result.stderr:
                print(f"错误:\n{result.stderr}")
    except subprocess.TimeoutExpired:
        print("⏰ 命令执行超时")
    except Exception as e:
        print(f"❌ 执行异常: {e}")


def main():
    """主函数 - 演示main.py的各种用法"""
    print("🚀 main.py 主启动文件使用示例")
    print("=" * 60)
    
    # 1. 查看帮助信息
    run_command("python main.py --help", "查看帮助信息")
    
    # 2. 检查服务状态
    run_command("python main.py status", "检查服务状态")
    
    print(f"\n📖 main.py 使用说明:")
    print("=" * 60)
    
    print(f"""
🎯 基本用法:
   python main.py                          # 使用默认配置启动
   python main.py status                   # 检查服务状态

⚙️ 配置参数:
   python main.py --host 0.0.0.0          # 指定绑定地址
   python main.py --port 8002             # 指定端口
   python main.py --workers 4             # 多进程模式
   python main.py --log-level debug       # 设置日志级别

🔧 开发模式:
   python main.py --reload                # 启用自动重载
   python main.py --reload --log-level debug  # 开发调试模式

🚀 生产模式:
   python main.py --workers 4 --log-level info  # 多进程生产模式

📊 监控模式:
   python main.py --log-level info         # 标准监控日志
   python main.py --log-level debug       # 详细调试日志

🔍 状态检查:
   python main.py status                   # 检查服务是否运行

🆚 与其他启动方式对比:

1. 直接使用uvicorn:
   uvicorn server.api:app --host 0.0.0.0 --port 8002
   
   优点: 简单直接
   缺点: 缺少依赖检查、模型服务检查、目录创建等功能

2. 使用main.py:
   python main.py --host 0.0.0.0 --port 8002
   
   优点: 
   - 自动检查依赖
   - 检查模型服务状态
   - 自动创建必要目录
   - 优雅的信号处理
   - 详细的启动信息
   - 状态检查功能
   - 友好的错误提示

3. 使用start.sh脚本:
   ./start.sh
   
   优点:
   - 自动安装依赖
   - 环境变量配置
   - 彩色输出
   - 适合Linux/Mac用户

🎯 推荐使用场景:

开发环境:
   python main.py --reload --log-level debug

测试环境:
   python main.py --workers 2 --log-level info

生产环境:
   python main.py --workers 4 --log-level warning

快速测试:
   python main.py status  # 检查服务
   ./start.sh             # 快速启动

🔧 环境变量配置:
   
   可以通过环境变量配置默认值:
   export LIGHTRAG_HOST=0.0.0.0
   export LIGHTRAG_PORT=8002
   export LIGHTRAG_WORKERS=4
   export LIGHTRAG_LOG_LEVEL=info
   
   然后直接运行:
   python main.py

📝 配置文件:
   
   服务配置在 server/config.py 中定义
   可以通过环境变量覆盖默认配置

🚨 注意事项:
   
   1. 确保大模型服务正在运行
   2. 检查端口是否被占用
   3. 确保有足够的磁盘空间
   4. 生产环境建议使用多进程模式

🔗 相关文档:
   
   - 快速开始: docs/QUICK_START.md
   - API文档: docs/API_REFERENCE.md
   - 部署指南: docs/DEPLOYMENT_GUIDE.md
   - 项目结构: docs/PROJECT_STRUCTURE.md
    """)


if __name__ == "__main__":
    main()
