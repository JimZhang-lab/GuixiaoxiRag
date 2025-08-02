#!/usr/bin/env python3
"""
GuiXiaoXiRag FastAPI 服务启动脚本
"""
import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import guixiaoxiRag
        print("✓ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_model_services():
    """检查大模型服务是否可用"""
    import httpx
    
    services = [
        ("LLM服务", "http://localhost:8100/v1/models"),
        ("Embedding服务", "http://localhost:8200/v1/models")
    ]
    
    for name, url in services:
        try:
            response = httpx.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✓ {name} 可用")
            else:
                print(f"⚠️ {name} 响应异常 (状态码: {response.status_code})")
        except Exception as e:
            print(f"❌ {name} 不可用: {e}")
            print(f"请确保 {name} 正在运行")

def setup_directories():
    """创建必要的目录"""
    dirs = ["logs", "knowledgeBase/default", "uploads"]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ 目录已创建: {dir_path}")

def start_server(host="0.0.0.0", port=8002, reload=True):
    """启动服务器"""
    print(f"正在启动 GuiXiaoXiRag FastAPI 服务...")
    print(f"地址: http://{host}:{port}")
    print(f"API文档: http://{host}:{port}/docs")
    print("按 Ctrl+C 停止服务")
    print("-" * 50)
    
    try:
        # 使用uvicorn启动服务
        cmd = [
            sys.executable, "-m", "uvicorn",
            "server.api:app",
            "--host", host,
            "--port", str(port)
        ]
        
        if reload:
            cmd.append("--reload")
        
        process = subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动失败: {e}")

def main():
    """主函数"""
    print("GuiXiaoXiRag FastAPI 服务启动器")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 设置目录
    setup_directories()
    
    # 检查模型服务
    print("\n检查模型服务状态:")
    check_model_services()
    
    print("\n准备启动服务...")
    time.sleep(2)
    
    # 启动服务
    start_server()

if __name__ == "__main__":
    main()
