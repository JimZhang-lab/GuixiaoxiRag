#!/usr/bin/env python3
"""
系统测试执行脚本
运行所有测试并记录详细的错误日志
"""

import os
import sys
import subprocess
import json
import time
import traceback
from datetime import datetime
from pathlib import Path
import logging


class SystemTestRunner:
    """系统测试运行器"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.logs_dir = self.test_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # 设置日志
        self.setup_logging()
        
        # 测试配置
        self.base_url = "http://localhost:8002"
        self.test_files = [
            "test_qa_system.py",
            "test_document_management.py", 
            "test_query_system.py",
            "test_system_management.py",
            "test_integration.py",
            "test_performance.py"
        ]
        
        self.results = {}
    
    def setup_logging(self):
        """设置日志配置"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_dir / f"system_test_{timestamp}.log"
        
        # 配置日志格式
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"系统测试开始 - 日志文件: {log_file}")
    
    def check_service_health(self) -> bool:
        """检查服务健康状态"""
        self.logger.info("检查服务健康状态...")
        
        try:
            import httpx
            response = httpx.get(f"{self.base_url}/api/v1/health", timeout=10)
            if response.status_code == 200:
                self.logger.info("✅ 服务健康检查通过")
                return True
            else:
                self.logger.error(f"❌ 服务健康检查失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ 无法连接到服务: {e}")
            return False
    
    def install_dependencies(self):
        """安装测试依赖"""
        self.logger.info("检查并安装测试依赖...")
        
        try:
            # 检查是否有requirements-test.txt
            requirements_file = self.test_dir / "requirements-test.txt"
            if requirements_file.exists():
                cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    self.logger.info("✅ 依赖安装成功")
                else:
                    self.logger.warning(f"⚠️ 依赖安装警告: {result.stderr}")
            else:
                self.logger.info("未找到requirements-test.txt，跳过依赖安装")
                
        except Exception as e:
            self.logger.error(f"❌ 依赖安装失败: {e}")
    
    def run_single_test(self, test_file: str) -> dict:
        """运行单个测试文件"""
        self.logger.info(f"🧪 运行测试: {test_file}")
        
        # 创建测试专用日志文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_log_file = self.logs_dir / f"{test_file}_{timestamp}.log"
        
        # 构建pytest命令
        cmd = [
            sys.executable, "-m", "pytest",
            test_file,
            "-v",
            "--tb=long",
            "--capture=no",
            f"--log-file={test_log_file}",
            "--log-file-level=DEBUG"
        ]
        
        # 设置环境变量
        env = os.environ.copy()
        env["TEST_BASE_URL"] = self.base_url
        env["PYTHONPATH"] = str(self.test_dir)
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.test_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=1800  # 30分钟超时
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 解析结果
            test_result = {
                "test_file": test_file,
                "success": result.returncode == 0,
                "duration": duration,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "log_file": str(test_log_file)
            }
            
            if test_result["success"]:
                self.logger.info(f"✅ {test_file} 测试通过 ({duration:.2f}s)")
            else:
                self.logger.error(f"❌ {test_file} 测试失败 ({duration:.2f}s)")
                self.logger.error(f"错误输出: {result.stderr}")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"❌ {test_file} 测试超时")
            return {
                "test_file": test_file,
                "success": False,
                "error": "测试超时",
                "duration": 1800
            }
        except Exception as e:
            self.logger.error(f"❌ {test_file} 测试执行异常: {e}")
            return {
                "test_file": test_file,
                "success": False,
                "error": str(e),
                "duration": 0
            }
    
    def run_all_tests(self):
        """运行所有测试"""
        self.logger.info("🚀 开始运行系统测试套件")
        
        # 检查服务健康状态
        if not self.check_service_health():
            self.logger.error("服务不可用，跳过测试")
            return
        
        # 安装依赖
        self.install_dependencies()
        
        # 运行每个测试文件
        total_tests = len(self.test_files)
        passed_tests = 0
        
        for i, test_file in enumerate(self.test_files, 1):
            self.logger.info(f"📋 进度: {i}/{total_tests}")
            
            # 检查测试文件是否存在
            test_path = self.test_dir / test_file
            if not test_path.exists():
                self.logger.warning(f"⚠️ 测试文件不存在: {test_file}")
                continue
            
            # 运行测试
            result = self.run_single_test(test_file)
            self.results[test_file] = result
            
            if result["success"]:
                passed_tests += 1
        
        # 生成总结报告
        self.generate_summary_report(passed_tests, total_tests)
    
    def generate_summary_report(self, passed_tests: int, total_tests: int):
        """生成总结报告"""
        self.logger.info("📊 生成测试总结报告...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.logs_dir / f"test_summary_{timestamp}.json"
        
        # 计算总体统计
        total_duration = sum(r.get("duration", 0) for r in self.results.values())
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": success_rate,
            "total_duration": total_duration,
            "base_url": self.base_url,
            "test_results": self.results
        }
        
        # 保存JSON报告
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # 生成Markdown报告
        self.generate_markdown_report(summary, timestamp)
        
        # 打印总结
        self.logger.info("=" * 60)
        self.logger.info("📊 测试总结")
        self.logger.info("=" * 60)
        self.logger.info(f"总测试数: {total_tests}")
        self.logger.info(f"通过测试: {passed_tests}")
        self.logger.info(f"失败测试: {total_tests - passed_tests}")
        self.logger.info(f"成功率: {success_rate:.2%}")
        self.logger.info(f"总耗时: {total_duration:.2f}s")
        self.logger.info(f"详细报告: {report_file}")
        
        if passed_tests == total_tests:
            self.logger.info("🎉 所有测试通过！")
        else:
            self.logger.warning("⚠️ 部分测试失败，请查看详细日志")
    
    def generate_markdown_report(self, summary: dict, timestamp: str):
        """生成Markdown格式的报告"""
        report_file = self.logs_dir / f"test_report_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# GuixiaoxiRag 系统测试报告\n\n")
            f.write(f"**生成时间**: {summary['timestamp']}\n")
            f.write(f"**测试服务**: {summary['base_url']}\n\n")
            
            # 总体结果
            if summary['success_rate'] == 1.0:
                f.write("## ✅ 测试结果: 全部通过\n\n")
            else:
                f.write("## ❌ 测试结果: 部分失败\n\n")
            
            # 统计信息
            f.write("## 📊 测试统计\n\n")
            f.write(f"- 总测试数: {summary['total_tests']}\n")
            f.write(f"- 通过测试: {summary['passed_tests']}\n")
            f.write(f"- 失败测试: {summary['failed_tests']}\n")
            f.write(f"- 成功率: {summary['success_rate']:.2%}\n")
            f.write(f"- 总耗时: {summary['total_duration']:.2f}秒\n\n")
            
            # 详细结果
            f.write("## 📋 详细结果\n\n")
            for test_file, result in summary['test_results'].items():
                status = "✅ 通过" if result['success'] else "❌ 失败"
                duration = result.get('duration', 0)
                f.write(f"### {test_file}\n")
                f.write(f"- 状态: {status}\n")
                f.write(f"- 耗时: {duration:.2f}秒\n")
                
                if not result['success']:
                    f.write(f"- 错误: {result.get('error', '未知错误')}\n")
                    if 'log_file' in result:
                        f.write(f"- 日志文件: {result['log_file']}\n")
                
                f.write("\n")
        
        self.logger.info(f"📄 Markdown报告已生成: {report_file}")


def main():
    """主函数"""
    print("🧪 GuixiaoxiRag 系统测试套件")
    print("=" * 50)
    
    runner = SystemTestRunner()
    
    try:
        runner.run_all_tests()
    except KeyboardInterrupt:
        runner.logger.info("❌ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        runner.logger.error(f"❌ 测试执行异常: {e}")
        runner.logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
