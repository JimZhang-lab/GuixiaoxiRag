#!/usr/bin/env python3
"""
测试运行脚本
"""
import asyncio
import sys
import os
import time
import subprocess
import signal
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from test_api import run_all_tests


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.server_process = None
        self.server_url = "http://localhost:8000"
        
    def start_server(self):
        """启动服务器"""
        print("正在启动GuiXiaoXiRag服务器...")
        
        # 切换到项目根目录
        os.chdir(project_root)
        
        # 启动服务器
        cmd = [sys.executable, "-m", "server.api"]
        self.server_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务器启动
        print("等待服务器启动...")
        time.sleep(10)  # 给服务器足够的启动时间
        
        # 检查服务器是否正在运行
        if self.server_process.poll() is not None:
            stdout, stderr = self.server_process.communicate()
            print(f"服务器启动失败:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
        
        print("服务器启动成功!")
        return True
    
    def stop_server(self):
        """停止服务器"""
        if self.server_process:
            print("正在停止服务器...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                print("强制终止服务器...")
                self.server_process.kill()
                self.server_process.wait()
            print("服务器已停止")
    
    async def check_server_health(self):
        """检查服务器健康状态"""
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.server_url}/health", timeout=5)
                return response.status_code == 200
        except Exception as e:
            print(f"健康检查失败: {e}")
            return False
    
    async def run_tests(self):
        """运行测试"""
        print("开始运行测试...")
        
        # 检查服务器健康状态
        if not await self.check_server_health():
            print("服务器健康检查失败，无法运行测试")
            return False
        
        try:
            await run_all_tests()
            print("所有测试通过!")
            return True
        except Exception as e:
            print(f"测试失败: {e}")
            return False
    
    async def run_full_test_suite(self):
        """运行完整测试套件"""
        success = False
        
        try:
            # 启动服务器
            if not self.start_server():
                return False
            
            # 运行测试
            success = await self.run_tests()
            
        finally:
            # 停止服务器
            self.stop_server()
        
        return success


def main():
    """主函数"""
    print("GuiXiaoXiRag API 测试套件")
    print("=" * 50)
    
    runner = TestRunner()
    
    try:
        success = asyncio.run(runner.run_full_test_suite())
        
        if success:
            print("\n" + "=" * 50)
            print("所有测试通过! ✅")
            sys.exit(0)
        else:
            print("\n" + "=" * 50)
            print("测试失败! ❌")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        runner.stop_server()
        sys.exit(1)
    except Exception as e:
        print(f"\n测试运行出错: {e}")
        runner.stop_server()
        sys.exit(1)


if __name__ == "__main__":
    main()
