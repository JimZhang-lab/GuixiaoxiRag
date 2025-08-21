#!/usr/bin/env python3
"""
测试运行脚本
提供便捷的测试执行和报告生成功能
"""

import os
import sys
import argparse
import subprocess
import json
import time
from pathlib import Path
from typing import List, Dict, Any


class TestRunner:
    """测试运行器"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.test_dir = Path(__file__).parent
        self.results = {}
    
    def run_health_check(self) -> bool:
        """运行健康检查"""
        print("🔍 检查服务健康状态...")
        
        try:
            import httpx
            response = httpx.get(f"{self.base_url}/api/v1/health", timeout=10)
            if response.status_code == 200:
                print("✅ 服务健康检查通过")
                return True
            else:
                print(f"❌ 服务健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 无法连接到服务: {e}")
            return False
    
    def run_test_suite(self, test_pattern: str = None, verbose: bool = False) -> Dict[str, Any]:
        """运行测试套件"""
        print(f"🚀 开始运行测试套件...")
        
        # 构建pytest命令
        cmd = ["python", "-m", "pytest"]
        
        if test_pattern:
            cmd.append(f"-k {test_pattern}")
        
        if verbose:
            cmd.append("-v")
        
        # 添加输出格式
        cmd.extend([
            "--tb=short",
            "--json-report",
            "--json-report-file=test_results.json"
        ])
        
        # 设置环境变量
        env = os.environ.copy()
        env["TEST_BASE_URL"] = self.base_url
        
        # 运行测试
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
            test_results = {
                "success": result.returncode == 0,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
            # 尝试读取JSON报告
            json_report_file = self.test_dir / "test_results.json"
            if json_report_file.exists():
                try:
                    with open(json_report_file, 'r', encoding='utf-8') as f:
                        json_report = json.load(f)
                    test_results["detailed_report"] = json_report
                except Exception as e:
                    print(f"⚠️ 无法读取详细报告: {e}")
            
            return test_results
            
        except subprocess.TimeoutExpired:
            print("❌ 测试执行超时")
            return {
                "success": False,
                "error": "测试执行超时",
                "duration": 1800
            }
        except Exception as e:
            print(f"❌ 测试执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration": 0
            }
    
    def run_specific_tests(self, test_files: List[str], verbose: bool = False) -> Dict[str, Any]:
        """运行指定的测试文件"""
        print(f"🎯 运行指定测试: {', '.join(test_files)}")
        
        cmd = ["python", "-m", "pytest"] + test_files
        
        if verbose:
            cmd.append("-v")
        
        cmd.extend([
            "--tb=short",
            "--json-report",
            "--json-report-file=specific_test_results.json"
        ])
        
        env = os.environ.copy()
        env["TEST_BASE_URL"] = self.base_url
        
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=self.test_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=1800
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            return {
                "success": result.returncode == 0,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except Exception as e:
            print(f"❌ 指定测试执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration": 0
            }
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """生成测试报告"""
        report = []
        report.append("# 测试报告")
        report.append(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"测试服务: {self.base_url}")
        report.append("")
        
        # 总体结果
        if results.get("success"):
            report.append("## ✅ 测试结果: 通过")
        else:
            report.append("## ❌ 测试结果: 失败")
        
        report.append(f"执行时间: {results.get('duration', 0):.2f} 秒")
        report.append("")
        
        # 详细报告
        if "detailed_report" in results:
            detailed = results["detailed_report"]
            summary = detailed.get("summary", {})
            
            report.append("## 📊 测试统计")
            report.append(f"- 总测试数: {summary.get('total', 0)}")
            report.append(f"- 通过: {summary.get('passed', 0)}")
            report.append(f"- 失败: {summary.get('failed', 0)}")
            report.append(f"- 跳过: {summary.get('skipped', 0)}")
            report.append(f"- 错误: {summary.get('error', 0)}")
            report.append("")
            
            # 失败的测试
            if summary.get('failed', 0) > 0:
                report.append("## ❌ 失败的测试")
                tests = detailed.get("tests", [])
                for test in tests:
                    if test.get("outcome") == "failed":
                        report.append(f"- {test.get('nodeid', 'Unknown')}")
                        if "call" in test and "longrepr" in test["call"]:
                            report.append(f"  错误: {test['call']['longrepr'][:200]}...")
                report.append("")
        
        # 输出信息
        if results.get("stdout"):
            report.append("## 📝 测试输出")
            report.append("```")
            report.append(results["stdout"][-2000:])  # 最后2000字符
            report.append("```")
            report.append("")
        
        if results.get("stderr"):
            report.append("## ⚠️ 错误输出")
            report.append("```")
            report.append(results["stderr"][-1000:])  # 最后1000字符
            report.append("```")
        
        return "\n".join(report)
    
    def save_report(self, report: str, filename: str = None):
        """保存报告到文件"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.md"
        
        report_path = self.test_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 测试报告已保存: {report_path}")
        return report_path


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="GuixiaoxiRag 测试运行器")
    parser.add_argument("--url", default="http://localhost:8002", help="服务URL")
    parser.add_argument("--pattern", "-k", help="测试模式匹配")
    parser.add_argument("--files", nargs="+", help="指定测试文件")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--no-health-check", action="store_true", help="跳过健康检查")
    parser.add_argument("--report", help="报告文件名")
    parser.add_argument("--quick", action="store_true", help="快速测试（跳过性能测试）")
    
    args = parser.parse_args()
    
    # 创建测试运行器
    runner = TestRunner(args.url)
    
    print("🧪 GuixiaoxiRag 系统测试")
    print("=" * 50)
    
    # 健康检查
    if not args.no_health_check:
        if not runner.run_health_check():
            print("❌ 服务不可用，退出测试")
            sys.exit(1)
        print()
    
    # 运行测试
    if args.files:
        # 运行指定文件
        results = runner.run_specific_tests(args.files, args.verbose)
    else:
        # 运行测试套件
        pattern = args.pattern
        if args.quick:
            # 快速测试，排除性能测试
            pattern = "not test_performance and not test_stress"
        
        results = runner.run_test_suite(pattern, args.verbose)
    
    # 生成报告
    report = runner.generate_report(results)
    print("\n" + "=" * 50)
    print(report)
    
    # 保存报告
    runner.save_report(report, args.report)
    
    # 退出码
    sys.exit(0 if results.get("success") else 1)


if __name__ == "__main__":
    main()
