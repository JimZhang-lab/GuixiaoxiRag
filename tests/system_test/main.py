#!/usr/bin/env python3
"""
GuixiaoxiRag 系统测试主启动文件
统一的测试入口，支持多种测试模式和清理选项

版本: 2.0.0
更新日期: 2025-08-22
主要功能:
- 支持多种测试模式 (sync, async, performance, integration, all)
- 详细的DEBUG级别日志记录
- 自动清理生成的文件
- 灵活的配置选项
- 完整的错误处理和诊断
"""

import os
import sys
import argparse
import shutil
from pathlib import Path
from typing import List, Dict, Any
import json
import time
import platform

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from runners.sync_test_runner import SyncTestRunner
from utils.cleanup_manager import CleanupManager
from utils.test_logger import TestLogger

# 版本信息
VERSION = "2.0.0"
BUILD_DATE = "2025-08-22"


class SystemTestMain:
    """系统测试主控制器"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.cleanup_manager = CleanupManager(self.test_dir)
        self.logger = TestLogger()
        
    def parse_arguments(self) -> argparse.Namespace:
        """解析命令行参数"""
        parser = argparse.ArgumentParser(
            description=f"GuixiaoxiRag 系统测试套件 v{VERSION}",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=f"""
测试模式:
  sync        - 同步HTTP测试（推荐，稳定可靠）
  async       - 异步pytest测试（实验性，高性能）
  performance - 性能压力测试（并发和负载测试）
  integration - 集成测试（端到端工作流）
  all         - 运行所有测试（完整验证）

常用示例:
  # 基础测试（推荐日常使用）
  python main.py sync --no-text-insert --clean-after

  # 完整测试（包含慢速操作）
  python main.py sync --clean-after --timeout 180

  # 详细调试模式
  python main.py sync --verbose --no-text-insert

  # 性能测试
  python main.py performance --timeout 300

  # 完整验证
  python main.py all --clean-before --clean-after

版本信息:
  版本: {VERSION}
  构建日期: {BUILD_DATE}
  Python: {platform.python_version()}
  平台: {platform.system()} {platform.release()}
            """
        )
        
        parser.add_argument(
            'mode',
            choices=['sync', 'async', 'performance', 'integration', 'all'],
            default='sync',
            nargs='?',
            help='测试模式 (默认: sync)'
        )
        
        parser.add_argument(
            '--base-url',
            default='http://localhost:8002',
            help='测试服务的基础URL (默认: http://localhost:8002)'
        )
        
        parser.add_argument(
            '--timeout',
            type=int,
            default=60,
            help='HTTP请求超时时间，秒 (默认: 60)'
        )
        
        parser.add_argument(
            '--clean-before',
            action='store_true',
            help='测试前清理所有生成的文件'
        )
        
        parser.add_argument(
            '--clean-after',
            action='store_true',
            help='测试后清理所有生成的文件'
        )
        
        parser.add_argument(
            '--clean-only',
            action='store_true',
            help='只执行清理操作，不运行测试'
        )
        
        parser.add_argument(
            '--verbose',
            '-v',
            action='store_true',
            help='详细输出模式'
        )
        
        parser.add_argument(
            '--output-dir',
            default='logs',
            help='输出目录 (默认: logs)'
        )
        
        parser.add_argument(
            '--no-text-insert',
            action='store_true',
            help='跳过文本插入测试（避免超时，推荐日常使用）'
        )

        parser.add_argument(
            '--retry-failed',
            action='store_true',
            help='对失败的测试进行重试'
        )

        parser.add_argument(
            '--save-results',
            action='store_true',
            default=True,
            help='保存测试结果到文件（默认启用）'
        )

        parser.add_argument(
            '--version',
            action='version',
            version=f'GuixiaoxiRag 测试套件 v{VERSION} (构建日期: {BUILD_DATE})'
        )

        return parser.parse_args()
    
    def run_sync_tests(self, args: argparse.Namespace) -> Dict[str, Any]:
        """运行同步测试"""
        self.logger.info("🚀 启动同步HTTP测试")

        runner = SyncTestRunner(
            base_url=args.base_url,
            timeout=args.timeout,
            output_dir=args.output_dir,
            skip_text_insert=args.no_text_insert
        )

        # 设置详细模式
        if args.verbose:
            runner.logger.set_verbose(True)

        return runner.run_all_tests()
    
    def run_async_tests(self, args: argparse.Namespace) -> Dict[str, Any]:
        """运行异步pytest测试"""
        self.logger.info("🧪 启动异步pytest测试")
        
        # 这里可以集成pytest运行器
        self.logger.warning("异步测试模式暂未实现")
        return {"status": "not_implemented", "message": "异步测试模式暂未实现"}
    
    def run_performance_tests(self, args: argparse.Namespace) -> Dict[str, Any]:
        """运行性能测试"""
        self.logger.info("⚡ 启动性能压力测试")
        
        # 这里可以集成性能测试
        self.logger.warning("性能测试模式暂未实现")
        return {"status": "not_implemented", "message": "性能测试模式暂未实现"}
    
    def run_integration_tests(self, args: argparse.Namespace) -> Dict[str, Any]:
        """运行集成测试"""
        self.logger.info("🔗 启动集成测试")
        
        # 这里可以集成集成测试
        self.logger.warning("集成测试模式暂未实现")
        return {"status": "not_implemented", "message": "集成测试模式暂未实现"}
    
    def run_all_tests(self, args: argparse.Namespace) -> Dict[str, Any]:
        """运行所有测试"""
        self.logger.info("🎯 启动全套测试")
        
        results = {}
        
        # 运行同步测试
        try:
            sync_results = self.run_sync_tests(args)
            results['sync'] = sync_results
        except Exception as e:
            self.logger.error(f"同步测试失败: {e}")
            results['sync'] = {"status": "error", "error": str(e)}
        
        # 可以添加其他测试类型
        
        return results
    
    def print_banner(self):
        """打印启动横幅"""
        banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                GuixiaoxiRag 系统测试套件                      ║
║                                                              ║
║  版本: {VERSION:<20} 构建日期: {BUILD_DATE:<15} ║
║  Python: {platform.python_version():<17} 平台: {platform.system():<20} ║
║                                                              ║
║  🚀 支持多种测试模式和详细的DEBUG日志                          ║
║  🧹 自动清理功能保持环境整洁                                   ║
║  📊 完整的测试报告和性能分析                                   ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)

    def main(self):
        """主函数"""
        # 打印启动横幅
        self.print_banner()

        args = self.parse_arguments()

        # 设置日志级别
        if args.verbose:
            self.logger.set_verbose(True)

        self.logger.info("=" * 60)
        self.logger.info(f"🔧 GuixiaoxiRag 系统测试套件 v{VERSION}")
        self.logger.info("=" * 60)
        self.logger.debug(f"命令行参数: {vars(args)}")
        self.logger.debug(f"Python版本: {platform.python_version()}")
        self.logger.debug(f"运行平台: {platform.system()} {platform.release()}")
        self.logger.debug(f"工作目录: {os.getcwd()}")
        
        try:
            # 只清理模式
            if args.clean_only:
                self.logger.info("🧹 执行清理操作...")
                cleaned_files = self.cleanup_manager.clean_all()
                self.logger.info(f"✅ 清理完成，删除了 {len(cleaned_files)} 个文件/目录")
                for file_path in cleaned_files:
                    self.logger.debug(f"  删除: {file_path}")
                return
            
            # 测试前清理
            if args.clean_before:
                self.logger.info("🧹 测试前清理...")
                cleaned_files = self.cleanup_manager.clean_all()
                self.logger.info(f"清理了 {len(cleaned_files)} 个文件/目录")
            
            # 运行测试
            start_time = time.time()
            
            if args.mode == 'sync':
                results = self.run_sync_tests(args)
            elif args.mode == 'async':
                results = self.run_async_tests(args)
            elif args.mode == 'performance':
                results = self.run_performance_tests(args)
            elif args.mode == 'integration':
                results = self.run_integration_tests(args)
            elif args.mode == 'all':
                results = self.run_all_tests(args)
            else:
                raise ValueError(f"未知的测试模式: {args.mode}")
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 输出结果摘要
            self.logger.info("=" * 60)
            self.logger.info("📊 测试完成摘要")
            self.logger.info("=" * 60)
            self.logger.info(f"测试模式: {args.mode}")
            self.logger.info(f"总耗时: {duration:.2f}秒")
            self.logger.info(f"基础URL: {args.base_url}")
            self.logger.info(f"超时设置: {args.timeout}秒")

            if isinstance(results, dict) and 'summary' in results:
                summary = results['summary']
                total = summary.get('total', 0)
                passed = summary.get('passed', 0)
                failed = summary.get('failed', 0)
                skipped = summary.get('skipped', 0)

                self.logger.info(f"总测试: {total}")
                self.logger.info(f"通过: {passed}")
                self.logger.info(f"失败: {failed}")
                if skipped > 0:
                    self.logger.info(f"跳过: {skipped}")

                success_rate = passed / max(total, 1)
                self.logger.info(f"成功率: {success_rate:.2%}")

                # 根据结果显示不同的状态
                if failed == 0 and passed > 0:
                    self.logger.info("🎉 所有测试通过！")
                elif passed > 0:
                    self.logger.info("✅ 部分测试通过")
                    if failed > 0:
                        self.logger.warning(f"⚠️ 有 {failed} 个测试失败，请检查日志")
                else:
                    self.logger.error("❌ 所有测试失败")

                # 保存结果摘要
                if args.save_results and 'timestamp' in results:
                    summary_file = self.test_dir / "logs" / f"test_summary_{results['timestamp']}.json"
                    try:
                        with open(summary_file, 'w', encoding='utf-8') as f:
                            json.dump({
                                "test_summary": summary,
                                "test_config": {
                                    "mode": args.mode,
                                    "base_url": args.base_url,
                                    "timeout": args.timeout,
                                    "skip_text_insert": args.no_text_insert,
                                    "verbose": args.verbose
                                },
                                "environment": {
                                    "python_version": platform.python_version(),
                                    "platform": platform.system(),
                                    "version": VERSION
                                }
                            }, f, ensure_ascii=False, indent=2)
                        self.logger.debug(f"测试摘要已保存: {summary_file}")
                    except Exception as e:
                        self.logger.warning(f"保存测试摘要失败: {e}")

            # 测试后清理
            if args.clean_after:
                self.logger.info("🧹 测试后清理...")
                cleaned_files = self.cleanup_manager.clean_all()
                self.logger.info(f"清理了 {len(cleaned_files)} 个文件/目录")

            self.logger.info("🎉 测试套件执行完成")

            # 返回适当的退出码
            if isinstance(results, dict) and 'summary' in results:
                failed_count = results['summary'].get('failed', 0)
                if failed_count > 0:
                    self.logger.debug(f"退出码: {failed_count} (失败测试数量)")
                    sys.exit(min(failed_count, 255))  # 限制退出码在有效范围内
            
        except KeyboardInterrupt:
            self.logger.warning("❌ 测试被用户中断")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"❌ 测试执行失败: {e}")
            if args.verbose:
                import traceback
                self.logger.error(traceback.format_exc())
            sys.exit(1)


if __name__ == "__main__":
    main = SystemTestMain()
    main.main()
