#!/usr/bin/env python3
"""
GuiXiaoXiRag 系统全方位压测脚本 - 优化版
专为2000+用户高并发场景设计，支持多种查询模式和可变文本长度测试

主要测试功能:
1. 智能查询测试 - 支持6种查询模式(local/global/hybrid/naive/mix/bypass)
2. 可变长度文本测试 - 50-8000 tokens不等的查询文本
3. cs_college知识库专项测试
4. 问答系统压力测试
5. 系统性能监控

使用方法:
1. 激活环境: conda activate guixiaoxi312
2. 确保服务运行在8002端口
3. 运行压测: python tests/stress_test.py

高并发优化特性:
- 支持2000+并发用户
- 多种查询模式覆盖
- 可变文本长度测试
- 连接池优化
- 内存使用优化
- 实时性能监控
- 详细测试报告
- 自动故障恢复
"""

import asyncio
import aiohttp
import time
import json
import random
import statistics
import psutil
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import argparse
import logging
import gc
from collections import defaultdict, deque
import threading
import queue

# 配置日志
def setup_logging():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f'tests/stress_test_{timestamp}.log'
    
    # 确保tests目录存在
    os.makedirs("tests", exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

@dataclass
class TestConfig:
    """测试配置 - 针对高并发优化"""
    base_url: str = "http://localhost:8002"
    concurrent_users: int = 100  # 默认100，可扩展到2000+
    test_duration: int = 600     # 10分钟测试
    ramp_up_time: int = 60       # 1分钟逐步增加负载
    ramp_down_time: int = 30     # 30秒逐步减少负载
    
    # 测试比例配置
    query_ratio: float = 0.70         # 70% 智能查询（各种模式）
    qa_query_ratio: float = 0.15      # 15% 问答查询
    qa_batch_ratio: float = 0.05      # 5% 批量查询
    qa_create_ratio: float = 0.05     # 5% 创建问答对
    health_ratio: float = 0.05        # 5% 健康检查
    
    # 性能优化配置
    connection_pool_size: int = 500   # 连接池大小
    connection_per_host: int = 100    # 每个主机连接数
    request_timeout: int = 30         # 请求超时
    max_retries: int = 3              # 最大重试次数

    # 用户与限流模拟配置
    min_interval_per_user: float = 0.0  # 单用户最小请求间隔（秒），0 表示不限制
    spoof_client_ip: bool = True        # 是否为每个用户伪造不同的客户端IP
    user_tier: str = "default"          # 用户套餐等级：default/free/pro/enterprise

    # 错误样本采集
    error_sample_limit: int = 50        # 每类错误采样条数上限
    error_sample_size: int = 500        # 每条样本最大字符数

    # 监控配置
    metrics_interval: int = 5         # 指标收集间隔
    progress_report_interval: int = 30 # 进度报告间隔

    # 内存优化
    result_buffer_size: int = 10000   # 结果缓冲区大小
    gc_interval: int = 100            # 垃圾回收间隔

@dataclass
class TestResult:
    """单次测试结果 - 内存优化版"""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    success: bool
    error_message: Optional[str] = None
    timestamp: float = 0.0
    user_id: int = 0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

@dataclass
class SystemMetrics:
    """系统指标"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    active_connections: int = 0
    
class PerformanceMonitor:
    """性能监控器 - 实时监控系统性能"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.metrics_queue = queue.Queue()
        self.is_monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """开始监控"""
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info("📊 性能监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("📊 性能监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_queue.put(metrics)
                time.sleep(self.config.metrics_interval)
            except Exception as e:
                logger.warning(f"收集系统指标失败: {e}")
    
    def _collect_metrics(self) -> SystemMetrics:
        """收集系统指标"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        
        # 磁盘IO
        disk_io = psutil.disk_io_counters()
        disk_io_read_mb = disk_io.read_bytes / (1024 * 1024) if disk_io else 0
        disk_io_write_mb = disk_io.write_bytes / (1024 * 1024) if disk_io else 0
        
        # 网络IO
        network_io = psutil.net_io_counters()
        network_sent_mb = network_io.bytes_sent / (1024 * 1024) if network_io else 0
        network_recv_mb = network_io.bytes_recv / (1024 * 1024) if network_io else 0
        
        # 活跃连接数
        try:
            connections = psutil.net_connections()
            active_connections = len([c for c in connections if c.status == 'ESTABLISHED'])
        except:
            active_connections = 0
        
        return SystemMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            disk_io_read_mb=disk_io_read_mb,
            disk_io_write_mb=disk_io_write_mb,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            active_connections=active_connections
        )
    
    def get_all_metrics(self) -> List[SystemMetrics]:
        """获取所有收集的指标"""
        metrics = []
        while not self.metrics_queue.empty():
            try:
                metrics.append(self.metrics_queue.get_nowait())
            except queue.Empty:
                break
        return metrics

class ResultBuffer:
    """结果缓冲区 - 优化内存使用"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)
        self.overflow_count = 0
        self.lock = threading.Lock()
    
    def add_result(self, result: TestResult):
        """添加测试结果"""
        with self.lock:
            if len(self.buffer) >= self.max_size:
                self.overflow_count += 1
            self.buffer.append(result)
    
    def get_all_results(self) -> List[TestResult]:
        """获取所有结果"""
        with self.lock:
            return list(self.buffer)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓冲区统计"""
        with self.lock:
            return {
                "buffer_size": len(self.buffer),
                "max_size": self.max_size,
                "overflow_count": self.overflow_count
            }

class HighConcurrencyStressTest:
    """高并发压力测试器"""

    def __init__(self, config: TestConfig):
        self.config = config
        self.result_buffer = ResultBuffer(config.result_buffer_size)
        self.performance_monitor = PerformanceMonitor(config)
        self.session: Optional[aiohttp.ClientSession] = None
        self.start_time = 0.0
        self.end_time = 0.0
        self.active_users = 0
        self.total_requests = 0
        self.request_counter_lock = threading.Lock()
        # 失败样本收集（按 endpoint::HTTP<code> 聚合）
        self.error_samples = defaultdict(list)

        # 测试数据 - 扩展测试数据
        self.test_questions = self._generate_test_questions()
        self.qa_pairs_data = self._generate_qa_pairs_data()
        self.query_modes = ["local", "global", "hybrid", "naive", "mix", "bypass"]
        self.performance_modes = ["fast", "balanced", "quality"]
        self.variable_length_queries = self._generate_variable_length_queries()

    def _build_user_headers(self, user_id: int, request_count: int = 0) -> Dict[str, str]:
        """构造每个请求的用户与代理相关头部"""
        headers: Dict[str, str] = {}
        if self.config.spoof_client_ip:
            a = 10
            b = user_id % 255
            c = (user_id // 255) % 255
            d = request_count % 255
            fake_ip = f"{a}.{b}.{c}.{d}"
            headers["X-Forwarded-For"] = fake_ip
            headers["X-Real-IP"] = fake_ip
        headers["X-User-Id"] = str(user_id)
        headers["X-Client-Id"] = f"stress-user-{user_id}"
        if getattr(self.config, "user_tier", None):
            headers["X-User-Tier"] = self.config.user_tier
        return headers

    async def _handle_response_and_backoff(self, endpoint: str, response: aiohttp.ClientResponse, response_time: float, user_id: int, request_count: int, is_warmup: bool) -> TestResult:
        """统一处理响应、采样错误、并对 429 做指数退避"""
        status = response.status
        error_msg = None
        success = False
        try:
            data = await response.json()
            success = bool(data.get("success", status == 200))
            if not success:
                error_msg = data.get("message") or data.get("error") or f"HTTP {status}"
                # 采样错误响应体
                self._record_error_sample(endpoint, status, json.dumps(data, ensure_ascii=False)[:1000])
        except Exception:
            text = await response.text()
            success = (status == 200)
            if not success:
                error_msg = f"HTTP {status}"
                self._record_error_sample(endpoint, status, text[:1000])

        result = TestResult(
            endpoint=endpoint,
            method=response.method if hasattr(response, 'method') else 'POST',
            status_code=status,
            response_time=response_time,
            success=success,
            error_message=error_msg,
            user_id=user_id
        )

        if not is_warmup:
            self.result_buffer.add_result(result)
            self.increment_request_counter()

        # 对 429 做指数退避，避免雪崩（仅非预热阶段）
        if status == 429 and not is_warmup:
            backoff_base = 0.2
            attempt = min(request_count, 6)
            await asyncio.sleep(backoff_base * (2 ** attempt))

        # 单用户最小请求间隔
        if self.config.min_interval_per_user and not is_warmup:
            await asyncio.sleep(self.config.min_interval_per_user)

        return result

    def _record_error_sample(self, endpoint: str, status_code: int, sample_text: str):
        """记录失败响应的样本（限长、限量）"""
        key = f"{endpoint}::HTTP{status_code}"
        limit = getattr(self.config, "error_sample_limit", 50)
        size = getattr(self.config, "error_sample_size", 500)
        if len(self.error_samples[key]) < limit:
            snippet = (sample_text or "").strip()
            if len(snippet) > size:
                snippet = snippet[:size] + "..."
            self.error_samples[key].append(snippet)

    def _generate_test_questions(self) -> List[str]:
        """生成测试问题"""
        base_questions = [
            "什么是人工智能？",
            "机器学习的基本原理是什么？",
            "深度学习和传统机器学习有什么区别？",
            "神经网络是如何工作的？",
            "什么是自然语言处理？",
            "计算机视觉的应用领域有哪些？",
            "强化学习的核心概念是什么？",
            "大数据分析的主要技术有哪些？",
            "云计算的优势是什么？",
            "区块链技术的原理是什么？",
            "物联网的发展趋势如何？",
            "5G技术带来了哪些变化？",
            "量子计算的潜在应用有哪些？",
            "网络安全的重要性体现在哪里？",
            "数据挖掘的常用算法有哪些？",
            "什么是边缘计算？",
            "容器化技术的优势是什么？",
            "微服务架构的特点有哪些？",
            "DevOps的核心理念是什么？",
            "什么是数字化转型？"
        ]
        
        # 扩展问题列表，增加变体
        extended_questions = []
        for question in base_questions:
            extended_questions.append(question)
            # 添加变体
            extended_questions.append(f"请详细解释{question}")
            extended_questions.append(f"能否简单介绍一下{question}")
            extended_questions.append(f"关于{question}，你了解多少？")
        
        return extended_questions

    def _generate_qa_pairs_data(self) -> List[Dict[str, Any]]:
        """生成问答对测试数据"""
        base_pairs = [
            {
                "question": "什么是Python？",
                "answer": "Python是一种高级编程语言，以其简洁的语法和强大的功能而闻名。",
                "category": "programming",
                "confidence": 0.95,
                "keywords": ["Python", "编程语言"],
                "source": "stress_test"
            },
            {
                "question": "什么是数据结构？",
                "answer": "数据结构是计算机存储、组织数据的方式，包括数组、链表、栈、队列等。",
                "category": "computer_science",
                "confidence": 0.92,
                "keywords": ["数据结构", "算法"],
                "source": "stress_test"
            },
            {
                "question": "什么是API？",
                "answer": "API（应用程序编程接口）是不同软件应用程序之间进行通信的接口。",
                "category": "technology",
                "confidence": 0.90,
                "keywords": ["API", "接口"],
                "source": "stress_test"
            },
            {
                "question": "什么是数据库？",
                "answer": "数据库是存储和管理数据的系统，提供数据的增删改查功能。",
                "category": "database",
                "confidence": 0.93,
                "keywords": ["数据库", "存储"],
                "source": "stress_test"
            },
            {
                "question": "什么是云计算？",
                "answer": "云计算是通过互联网提供计算资源和服务的模式。",
                "category": "cloud",
                "confidence": 0.91,
                "keywords": ["云计算", "互联网"],
                "source": "stress_test"
            }
        ]
        return base_pairs

    def _generate_variable_length_queries(self) -> Dict[str, List[str]]:
        """生成不同长度的查询文本 (50-8000 tokens)"""

        # 基础查询模板
        base_topics = [
            "计算机科学", "人工智能", "机器学习", "深度学习", "数据科学", "软件工程",
            "网络安全", "云计算", "大数据", "区块链", "物联网", "量子计算",
            "编程语言", "算法设计", "数据结构", "操作系统", "数据库系统", "分布式系统"
        ]

        # 扩展内容片段
        content_fragments = [
            "的基本概念和核心原理", "在现代科技发展中的重要作用", "的历史发展过程和里程碑事件",
            "的技术实现方法和关键技术", "在各个行业中的实际应用案例", "面临的主要挑战和解决方案",
            "的未来发展趋势和前景展望", "与其他技术领域的交叉融合", "对社会经济发展的深远影响",
            "的理论基础和数学模型", "的工程实践和项目管理", "的标准化和规范化进程",
            "的安全性和可靠性考虑", "的性能优化和效率提升", "的成本效益分析和投资回报",
            "的人才培养和教育体系", "的国际合作和技术交流", "的法律法规和伦理考量"
        ]

        # 详细描述片段
        detailed_fragments = [
            "从技术架构的角度来看，这个领域涉及多个层次的复杂系统设计，包括底层硬件优化、中间件集成、上层应用开发等各个环节。",
            "在实际应用过程中，需要考虑用户体验、系统性能、数据安全、成本控制等多个维度的平衡和优化。",
            "随着技术的不断进步和市场需求的变化，相关的标准和规范也在持续演进和完善。",
            "产业界和学术界的紧密合作推动了理论研究和实践应用的相互促进和共同发展。",
            "国际化的技术交流和标准制定为全球范围内的技术创新和应用推广提供了重要支撑。",
            "跨学科的研究方法和多元化的技术路径为解决复杂问题提供了更多的可能性和选择。",
            "可持续发展的理念和绿色技术的应用成为了现代技术发展的重要考量因素。",
            "数字化转型和智能化升级为传统行业带来了新的机遇和挑战。"
        ]

        queries_by_length = {
            "short": [],      # 50-200 tokens
            "medium": [],     # 200-800 tokens
            "long": [],       # 800-2000 tokens
            "very_long": [],  # 2000-5000 tokens
            "ultra_long": []  # 5000-8000 tokens
        }

        # 生成短查询 (50-200 tokens)
        for topic in base_topics:
            for fragment in content_fragments[:6]:
                query = f"请详细介绍{topic}{fragment}，包括相关的技术细节、应用场景和发展现状。"
                queries_by_length["short"].append(query)

        # 生成中等长度查询 (200-800 tokens)
        for topic in base_topics[:10]:
            query_parts = [
                f"关于{topic}这个重要的技术领域，我想了解以下几个方面的内容：",
                f"1. {topic}的核心概念和基本原理是什么？",
                f"2. {topic}在当前技术发展中处于什么地位？",
                f"3. {topic}有哪些主要的应用领域和实际案例？",
                f"4. {topic}面临的主要技术挑战有哪些？",
                f"5. {topic}的未来发展方向和趋势如何？",
                "请针对每个问题提供详细的分析和说明，并结合具体的技术实例进行阐述。"
            ]
            query = " ".join(query_parts)
            queries_by_length["medium"].append(query)

        # 生成长查询 (800-2000 tokens)
        for topic in base_topics[:8]:
            query_parts = [
                f"我正在进行关于{topic}的深入研究，希望能够获得全面而详细的信息。",
                f"首先，请介绍{topic}的历史发展脉络，包括重要的里程碑事件和关键技术突破。",
                f"其次，请详细阐述{topic}的核心技术原理和理论基础，包括相关的数学模型和算法设计。",
                f"第三，请分析{topic}在不同行业和领域中的应用情况，包括成功案例和失败教训。",
                f"第四，请讨论{topic}当前面临的主要技术挑战和瓶颈，以及可能的解决方案。",
                f"第五，请展望{topic}的未来发展趋势，包括新兴技术的融合和创新方向。",
                f"最后，请分析{topic}对社会经济发展的影响，包括就业、教育、产业结构等方面的变化。",
                "请确保回答内容的准确性和权威性，并提供相关的数据支撑和案例分析。"
            ]
            for fragment in detailed_fragments[:3]:
                query_parts.append(fragment)
            query = " ".join(query_parts)
            queries_by_length["long"].append(query)

        # 生成很长查询 (2000-5000 tokens)
        for topic in base_topics[:5]:
            query_parts = [
                f"作为{topic}领域的研究者，我需要对这个领域进行全方位的深度分析和研究。",
                f"请从以下多个维度对{topic}进行详细的阐述和分析：",
                "",
                "一、历史发展维度：",
                f"1.1 {topic}的起源和早期发展阶段",
                f"1.2 {topic}发展过程中的重要里程碑和转折点",
                f"1.3 {topic}领域的重要人物和贡献",
                f"1.4 {topic}与其他学科领域的交叉发展",
                "",
                "二、技术原理维度：",
                f"2.1 {topic}的核心理论基础和数学模型",
                f"2.2 {topic}的关键技术和实现方法",
                f"2.3 {topic}的技术架构和系统设计",
                f"2.4 {topic}的性能评估和优化策略",
                "",
                "三、应用实践维度：",
                f"3.1 {topic}在各个行业中的具体应用",
                f"3.2 {topic}的成功案例和最佳实践",
                f"3.3 {topic}的实施挑战和解决方案",
                f"3.4 {topic}的投资回报和经济效益",
                "",
                "四、发展趋势维度：",
                f"4.1 {topic}的技术发展趋势和创新方向",
                f"4.2 {topic}与新兴技术的融合发展",
                f"4.3 {topic}的市场前景和商业模式",
                f"4.4 {topic}的标准化和规范化进程",
                "",
                "五、社会影响维度：",
                f"5.1 {topic}对就业市场和人才需求的影响",
                f"5.2 {topic}对教育体系和培养模式的影响",
                f"5.3 {topic}对社会结构和生活方式的影响",
                f"5.4 {topic}的伦理考量和社会责任",
            ]
            for fragment in detailed_fragments:
                query_parts.append(fragment)
            query_parts.extend([
                "请确保回答内容的系统性和完整性，提供充分的数据支撑和案例分析。",
                "同时，请注意内容的前沿性和实用性，结合最新的研究成果和行业动态。"
            ])
            query = " ".join(query_parts)
            queries_by_length["very_long"].append(query)

        # 生成超长查询 (5000-8000 tokens)
        for topic in base_topics[:3]:
            query_parts = [
                f"我正在撰写关于{topic}的综合性研究报告，需要对这个领域进行极其详细和全面的分析。",
                f"请从学术研究、产业应用、技术发展、社会影响等多个角度对{topic}进行深度剖析：",
                "",
                "第一部分：理论基础与学术研究",
                f"1.1 {topic}的理论起源和哲学基础",
                f"1.2 {topic}的核心概念体系和分类框架",
                f"1.3 {topic}的数学模型和算法理论",
                f"1.4 {topic}的研究方法论和实验设计",
                f"1.5 {topic}领域的重要学术机构和研究团队",
                f"1.6 {topic}的学术期刊和会议体系",
                f"1.7 {topic}的知识产权和专利分析",
                "",
                "第二部分：技术实现与工程应用",
                f"2.1 {topic}的技术架构和系统设计原则",
                f"2.2 {topic}的核心算法和实现技术",
                f"2.3 {topic}的开发工具和平台生态",
                f"2.4 {topic}的性能优化和扩展性设计",
                f"2.5 {topic}的安全性和可靠性保障",
                f"2.6 {topic}的测试验证和质量控制",
                f"2.7 {topic}的部署运维和监控管理",
                "",
                "第三部分：产业应用与商业价值",
                f"3.1 {topic}在金融服务业的应用和创新",
                f"3.2 {topic}在制造业的数字化转型应用",
                f"3.3 {topic}在医疗健康领域的突破性应用",
                f"3.4 {topic}在教育培训行业的变革性应用",
                f"3.5 {topic}在交通物流领域的智能化应用",
                f"3.6 {topic}在能源环保行业的可持续发展应用",
                f"3.7 {topic}的商业模式创新和价值链重构",
                "",
                "第四部分：发展趋势与未来展望",
                f"4.1 {topic}的技术发展路线图和里程碑规划",
                f"4.2 {topic}与人工智能技术的深度融合",
                f"4.3 {topic}与物联网技术的协同发展",
                f"4.4 {topic}与区块链技术的创新结合",
                f"4.5 {topic}与量子计算的前沿探索",
                f"4.6 {topic}的国际标准化和规范化进程",
                f"4.7 {topic}的全球化发展和国际合作",
                "",
                "第五部分：挑战分析与解决策略",
                f"5.1 {topic}面临的技术挑战和瓶颈分析",
                f"5.2 {topic}的人才短缺和培养体系建设",
                f"5.3 {topic}的数据安全和隐私保护问题",
                f"5.4 {topic}的伦理道德和社会责任考量",
                f"5.5 {topic}的法律法规和政策环境",
                f"5.6 {topic}的投资风险和市场不确定性",
                f"5.7 {topic}的可持续发展和环境影响",
                "",
                "第六部分：社会影响与变革意义",
                f"6.1 {topic}对劳动力市场和就业结构的影响",
                f"6.2 {topic}对教育体系和人才培养的变革",
                f"6.3 {topic}对社会治理和公共服务的提升",
                f"6.4 {topic}对经济发展模式的重塑",
                f"6.5 {topic}对文化传播和社会交往的影响",
                f"6.6 {topic}对城市规划和智慧城市建设的推动",
                f"6.7 {topic}对全球化进程和国际关系的影响",
            ]

            # 添加更多详细内容
            for i, fragment in enumerate(detailed_fragments):
                query_parts.append(f"补充说明{i+1}：{fragment}")

            query_parts.extend([
                "",
                "请确保回答内容具有以下特点：",
                "- 学术严谨性：基于权威资料和最新研究成果",
                "- 实践指导性：结合具体案例和实际应用经验",
                "- 前瞻预测性：把握技术发展趋势和未来方向",
                "- 系统完整性：覆盖理论、技术、应用、影响等各个层面",
                "- 数据支撑性：提供充分的统计数据和量化分析",
                "- 国际视野性：结合全球发展现状和国际比较",
                "- 创新启发性：提出新的思考角度和发展建议",
                "",
                "同时，请在回答中注明信息来源和参考文献，确保内容的可信度和可追溯性。"
            ])

            query = " ".join(query_parts)
            queries_by_length["ultra_long"].append(query)

        return queries_by_length

    def get_user_specific_query_config(self, user_id: int, request_count: int) -> Dict[str, Any]:
        """为每个用户生成特定的查询配置，确保覆盖所有模式和长度"""

        # 确保每个用户在测试过程中会轮换使用所有查询模式
        mode_index = (user_id * 7 + request_count) % len(self.query_modes)
        query_mode = self.query_modes[mode_index]

        # 确保每个用户在测试过程中会使用不同长度的文本
        length_categories = list(self.variable_length_queries.keys())
        length_index = (user_id * 3 + request_count // 2) % len(length_categories)
        length_category = length_categories[length_index]

        # 性能模式也进行轮换
        perf_index = (user_id + request_count // 3) % len(self.performance_modes)
        performance_mode = self.performance_modes[perf_index]

        # 选择特定的查询文本
        available_queries = self.variable_length_queries[length_category]
        query_index = (user_id * 5 + request_count) % len(available_queries)
        query_text = available_queries[query_index]

        return {
            "query_mode": query_mode,
            "performance_mode": performance_mode,
            "length_category": length_category,
            "query_text": query_text,
            "estimated_tokens": self._estimate_tokens(query_text)
        }

    def _estimate_tokens(self, text: str) -> int:
        """估算文本的token数量（简单估算：中文字符数 + 英文单词数）"""
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        english_words = len([w for w in text.split() if any(c.isalpha() for c in w)])
        return chinese_chars + english_words

    async def setup(self):
        """初始化设置 - 高并发优化"""
        # 创建高性能连接器
        connector = aiohttp.TCPConnector(
            limit=self.config.connection_pool_size,
            limit_per_host=self.config.connection_per_host,
            ttl_dns_cache=300,
            use_dns_cache=True,
            enable_cleanup_closed=True,
            keepalive_timeout=30
        )

        timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'Connection': 'keep-alive'}
        )

        # 检查服务可用性
        await self.check_service_availability()

        # 预热系统
        await self.warmup_system()

        # 启动性能监控
        self.performance_monitor.start_monitoring()

        logger.info(f"✅ 系统初始化完成，准备启动 {self.config.concurrent_users} 个并发用户")

    async def cleanup(self):
        """清理资源"""
        self.performance_monitor.stop_monitoring()

        if self.session:
            await self.session.close()

        # 强制垃圾回收
        gc.collect()

        logger.info("🧹 资源清理完成")

    async def check_service_availability(self):
        """检查服务可用性"""
        try:
            async with self.session.get(f"{self.config.base_url}/health") as response:
                if response.status == 200:
                    logger.info("✅ 服务可用，开始压力测试")
                else:
                    raise Exception(f"服务不可用，状态码: {response.status}")
        except Exception as e:
            logger.error(f"❌ 服务不可用: {e}")
            raise

    async def warmup_system(self):
        """系统预热"""
        logger.info("🔥 开始系统预热...")
        warmup_tasks = []

        # 预热各种类型的请求
        for _ in range(10):
            question = random.choice(self.test_questions)
            warmup_tasks.append(self.test_qa_query(question, user_id=-1, is_warmup=True))

        for _ in range(5):
            warmup_tasks.append(self.test_intelligent_query(user_id=-1, request_count=0, is_warmup=True))

        for _ in range(3):
            warmup_tasks.append(self.test_qa_batch_query(user_id=-1, is_warmup=True))

        warmup_tasks.append(self.test_qa_health_check(user_id=-1, is_warmup=True))
        warmup_tasks.append(self.test_qa_statistics(user_id=-1, is_warmup=True))

        await asyncio.gather(*warmup_tasks, return_exceptions=True)
        logger.info("✅ 系统预热完成")

    def increment_request_counter(self):
        """线程安全的请求计数器"""
        with self.request_counter_lock:
            self.total_requests += 1

    async def test_qa_query(self, question: str, user_id: int, is_warmup: bool = False) -> TestResult:
        """测试问答查询"""
        start_time = time.time()
        endpoint = "/api/v1/qa/query"

        payload = {
            "question": question,
            "top_k": random.randint(1, 5),
            "min_similarity": random.uniform(0.7, 0.98)
        }

        try:
            headers = self._build_user_headers(user_id)
            async with self.session.post(
                f"{self.config.base_url}{endpoint}",
                json=payload,
                headers=headers
            ) as response:
                response_time = time.time() - start_time
                return await self._handle_response_and_backoff(endpoint, response, response_time, user_id, 0, is_warmup)

        except Exception as e:
            response_time = time.time() - start_time
            result = TestResult(
                endpoint=endpoint,
                method="POST",
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=str(e),
                user_id=user_id
            )

            if not is_warmup:
                self.result_buffer.add_result(result)
                self.increment_request_counter()

            return result

    async def test_intelligent_query(self, user_id: int, request_count: int = 0, is_warmup: bool = False) -> TestResult:
        """测试智能查询（不同模式和文本长度）"""
        start_time = time.time()
        endpoint = "/api/v1/query"

        # 获取用户特定的查询配置
        if is_warmup:
            # 预热时使用随机配置
            query_mode = random.choice(self.query_modes)
            performance_mode = random.choice(self.performance_modes)
            length_category = random.choice(list(self.variable_length_queries.keys()))
            query_text = random.choice(self.variable_length_queries[length_category])
            estimated_tokens = self._estimate_tokens(query_text)
        else:
            # 正式测试时使用确定性配置，确保覆盖所有模式
            config = self.get_user_specific_query_config(user_id, request_count)
            query_mode = config["query_mode"]
            performance_mode = config["performance_mode"]
            length_category = config["length_category"]
            query_text = config["query_text"]
            estimated_tokens = config["estimated_tokens"]

        payload = {
            "query": query_text,
            "knowledge_base": "cs_college",  # 指定cs_college知识库
            "mode": query_mode,
            "performance_mode": performance_mode,
            "stream": False,
            "only_need_context": False
        }

        try:
            headers = self._build_user_headers(user_id, request_count=request_count)
            async with self.session.post(
                f"{self.config.base_url}{endpoint}",
                json=payload,
                headers=headers
            ) as response:
                response_time = time.time() - start_time
                return await self._handle_response_and_backoff(
                    f"{endpoint}_{query_mode}_{length_category}_{estimated_tokens}tokens",
                    response,
                    response_time,
                    user_id,
                    request_count,
                    is_warmup,
                )

        except Exception as e:
            response_time = time.time() - start_time
            result = TestResult(
                endpoint=f"{endpoint}_{query_mode}_{length_category}_{estimated_tokens}tokens",
                method="POST",
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=str(e),
                user_id=user_id
            )

            if not is_warmup:
                self.result_buffer.add_result(result)
                self.increment_request_counter()

            return result

    async def test_qa_batch_query(self, user_id: int, is_warmup: bool = False) -> TestResult:
        """测试批量问答查询"""
        start_time = time.time()
        endpoint = "/api/v1/qa/query/batch"

        # 随机选择2-5个问题进行批量查询
        questions = random.sample(self.test_questions, random.randint(2, 5))
        payload = {
            "questions": questions,
            "top_k": random.randint(1, 3),
            "min_similarity": random.uniform(0.7, 0.98)
        }

        try:
            headers = self._build_user_headers(user_id)
            async with self.session.post(
                f"{self.config.base_url}{endpoint}",
                json=payload,
                headers=headers
            ) as response:
                response_time = time.time() - start_time
                return await self._handle_response_and_backoff(endpoint, response, response_time, user_id, 0, is_warmup)

        except Exception as e:
            response_time = time.time() - start_time
            result = TestResult(
                endpoint=endpoint,
                method="POST",
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=str(e),
                user_id=user_id
            )

            if not is_warmup:
                self.result_buffer.add_result(result)
                self.increment_request_counter()

            return result

    async def test_qa_create_pair(self, user_id: int, is_warmup: bool = False) -> TestResult:
        """测试创建问答对"""
        start_time = time.time()
        endpoint = "/api/v1/qa/pairs"

        # 随机选择一个问答对数据并添加随机后缀
        base_data = random.choice(self.qa_pairs_data).copy()
        timestamp = int(time.time() * 1000)
        base_data["question"] = f"{base_data['question']} (用户{user_id}-{timestamp})"
        base_data["answer"] = f"{base_data['answer']} (压测数据-{timestamp})"

        try:
            headers = self._build_user_headers(user_id)
            async with self.session.post(
                f"{self.config.base_url}{endpoint}",
                json=base_data,
                headers=headers
            ) as response:
                response_time = time.time() - start_time
                return await self._handle_response_and_backoff(endpoint, response, response_time, user_id, 0, is_warmup)

        except Exception as e:
            response_time = time.time() - start_time
            result = TestResult(
                endpoint=endpoint,
                method="POST",
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=str(e),
                user_id=user_id
            )

            if not is_warmup:
                self.result_buffer.add_result(result)
                self.increment_request_counter()

            return result

    async def test_qa_health_check(self, user_id: int, is_warmup: bool = False) -> TestResult:
        """测试问答系统健康检查"""
        start_time = time.time()
        endpoint = "/api/v1/qa/health"

        try:
            async with self.session.get(f"{self.config.base_url}{endpoint}") as response:
                response_time = time.time() - start_time

                success = response.status == 200
                error_msg = None if success else f"HTTP {response.status}"

                result = TestResult(
                    endpoint=endpoint,
                    method="GET",
                    status_code=response.status,
                    response_time=response_time,
                    success=success,
                    error_message=error_msg,
                    user_id=user_id
                )

                if not is_warmup:
                    self.result_buffer.add_result(result)
                    self.increment_request_counter()

                return result

        except Exception as e:
            response_time = time.time() - start_time
            result = TestResult(
                endpoint=endpoint,
                method="GET",
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=str(e),
                user_id=user_id
            )

            if not is_warmup:
                self.result_buffer.add_result(result)
                self.increment_request_counter()

            return result

    async def test_qa_statistics(self, user_id: int, is_warmup: bool = False) -> TestResult:
        """测试问答系统统计信息"""
        start_time = time.time()
        endpoint = "/api/v1/qa/statistics"

        try:
            async with self.session.get(f"{self.config.base_url}{endpoint}") as response:
                response_time = time.time() - start_time

                success = response.status == 200
                error_msg = None if success else f"HTTP {response.status}"

                result = TestResult(
                    endpoint=endpoint,
                    method="GET",
                    status_code=response.status,
                    response_time=response_time,
                    success=success,
                    error_message=error_msg,
                    user_id=user_id
                )

                if not is_warmup:
                    self.result_buffer.add_result(result)
                    self.increment_request_counter()

                return result

        except Exception as e:
            response_time = time.time() - start_time
            result = TestResult(
                endpoint=endpoint,
                method="GET",
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=str(e),
                user_id=user_id
            )

            if not is_warmup:
                self.result_buffer.add_result(result)
                self.increment_request_counter()

            return result

    async def user_simulation_task(self, user_id: int):
        """模拟单个用户的测试任务 - 高并发优化"""
        logger.info(f"👤 用户 {user_id} 开始测试")
        self.active_users += 1

        request_count = 0
        last_gc_time = time.time()

        try:
            while time.time() - self.start_time < self.config.test_duration:
                try:
                    # 根据配置的比例选择测试类型
                    rand = random.random()

                    if rand < self.config.query_ratio:
                        # 智能查询测试（各种模式和文本长度）
                        await self.test_intelligent_query(user_id, request_count)

                    elif rand < self.config.query_ratio + self.config.qa_query_ratio:
                        # 问答查询测试
                        question = random.choice(self.test_questions)
                        await self.test_qa_query(question, user_id)

                    elif rand < (self.config.query_ratio + self.config.qa_query_ratio +
                                self.config.qa_batch_ratio):
                        # 批量查询测试
                        await self.test_qa_batch_query(user_id)

                    elif rand < (self.config.query_ratio + self.config.qa_query_ratio +
                                self.config.qa_batch_ratio + self.config.qa_create_ratio):
                        # 创建问答对测试
                        await self.test_qa_create_pair(user_id)

                    else:
                        # 健康检查测试
                        await self.test_qa_health_check(user_id)

                    request_count += 1

                    # 定期垃圾回收
                    if request_count % self.config.gc_interval == 0:
                        current_time = time.time()
                        if current_time - last_gc_time > 60:  # 每分钟最多一次
                            gc.collect()
                            last_gc_time = current_time

                    # 随机等待时间，模拟真实用户行为
                    await asyncio.sleep(random.uniform(0.1, 1.5))

                except Exception as e:
                    logger.warning(f"用户 {user_id} 请求异常: {e}")
                    await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"用户 {user_id} 任务异常: {e}")
        finally:
            self.active_users -= 1
            logger.info(f"👤 用户 {user_id} 测试完成，总请求数: {request_count}")

    async def progress_reporter_task(self):
        """进度报告任务"""
        logger.info("📈 开始进度监控")

        while time.time() - self.start_time < self.config.test_duration:
            elapsed_time = time.time() - self.start_time
            remaining_time = self.config.test_duration - elapsed_time
            progress_percent = (elapsed_time / self.config.test_duration) * 100

            buffer_stats = self.result_buffer.get_stats()

            logger.info(
                f"📊 进度: {progress_percent:.1f}% | "
                f"活跃用户: {self.active_users} | "
                f"总请求: {self.total_requests} | "
                f"剩余时间: {remaining_time:.0f}s | "
                f"缓冲区: {buffer_stats['buffer_size']}/{buffer_stats['max_size']}"
            )

            await asyncio.sleep(self.config.progress_report_interval)

        logger.info("📈 进度监控完成")

    async def run_stress_test(self):
        """运行压力测试 - 高并发优化"""
        logger.info(f"🚀 开始高并发压力测试 - {self.config.concurrent_users} 并发用户")
        self.start_time = time.time()

        # 创建用户模拟任务
        user_tasks = []

        # 启动进度报告任务
        progress_task = asyncio.create_task(self.progress_reporter_task())

        # 逐步增加负载 (Ramp-up)
        ramp_up_interval = self.config.ramp_up_time / self.config.concurrent_users

        logger.info(f"🔄 开始负载增加阶段，{self.config.ramp_up_time}秒内逐步启动用户")

        for user_id in range(self.config.concurrent_users):
            # 延迟启动用户，实现逐步增加负载
            if user_id > 0:
                await asyncio.sleep(ramp_up_interval)

            task = asyncio.create_task(self.user_simulation_task(user_id))
            user_tasks.append(task)

            if (user_id + 1) % 100 == 0:  # 每100个用户报告一次
                logger.info(f"🔄 已启动 {user_id + 1}/{self.config.concurrent_users} 个用户")

        logger.info(f"✅ 所有 {self.config.concurrent_users} 个用户已启动，进入稳定测试阶段")

        # 等待所有任务完成
        all_tasks = user_tasks + [progress_task]
        await asyncio.gather(*all_tasks, return_exceptions=True)

        self.end_time = time.time()
        logger.info("✅ 压力测试完成")

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成全面的测试报告"""
        results = self.result_buffer.get_all_results()
        system_metrics = self.performance_monitor.get_all_metrics()

        if not results:
            return {"error": "没有测试结果"}

        # 基本统计
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r.success)
        failed_requests = total_requests - successful_requests
        success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0

        # 响应时间统计
        response_times = [r.response_time for r in results]
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)

        # 计算百分位数
        sorted_times = sorted(response_times)
        p50_response_time = statistics.median(sorted_times)
        p90_response_time = sorted_times[int(len(sorted_times) * 0.9)] if len(sorted_times) > 10 else max_response_time
        p95_response_time = sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 20 else max_response_time
        p99_response_time = sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) > 100 else max_response_time

        # 按端点统计
        endpoint_stats = defaultdict(lambda: {
            "total": 0, "success": 0, "failed": 0, "response_times": []
        })

        for result in results:
            endpoint = result.endpoint
            endpoint_stats[endpoint]["total"] += 1
            if result.success:
                endpoint_stats[endpoint]["success"] += 1
            else:
                endpoint_stats[endpoint]["failed"] += 1
            endpoint_stats[endpoint]["response_times"].append(result.response_time)

        # 计算每个端点的统计信息
        for endpoint, stats in endpoint_stats.items():
            times = stats["response_times"]
            if times:
                stats["avg_response_time"] = statistics.mean(times)
                stats["min_response_time"] = min(times)
                stats["max_response_time"] = max(times)
                stats["p95_response_time"] = sorted(times)[int(len(times) * 0.95)] if len(times) > 20 else max(times)
                stats["success_rate"] = (stats["success"] / stats["total"]) * 100
            del stats["response_times"]  # 删除原始数据

        # 系统资源统计
        system_stats = {}
        if system_metrics:
            cpu_values = [m.cpu_percent for m in system_metrics]
            memory_values = [m.memory_percent for m in system_metrics]
            connection_values = [m.active_connections for m in system_metrics]

            system_stats = {
                "avg_cpu_percent": statistics.mean(cpu_values),
                "max_cpu_percent": max(cpu_values),
                "min_cpu_percent": min(cpu_values),
                "avg_memory_percent": statistics.mean(memory_values),
                "max_memory_percent": max(memory_values),
                "avg_memory_used_mb": statistics.mean([m.memory_used_mb for m in system_metrics]),
                "max_memory_used_mb": max([m.memory_used_mb for m in system_metrics]),
                "avg_active_connections": statistics.mean(connection_values),
                "max_active_connections": max(connection_values),
                "metrics_count": len(system_metrics)
            }

        # 收集错误样本统计
        error_samples_summary = {k: v for k, v in self.error_samples.items()}

        # 错误统计
        error_stats = defaultdict(int)
        for result in results:
            if not result.success and result.error_message:
                error_stats[result.error_message] += 1

        # 用户统计
        user_stats = defaultdict(lambda: {"requests": 0, "success": 0, "failed": 0})
        for result in results:
            user_id = result.user_id
            user_stats[user_id]["requests"] += 1
            if result.success:
                user_stats[user_id]["success"] += 1
            else:
                user_stats[user_id]["failed"] += 1

        # 时间分布统计
        test_duration = self.end_time - self.start_time if self.end_time > 0 else 0
        requests_per_second = total_requests / test_duration if test_duration > 0 else 0

        # 缓冲区统计
        buffer_stats = self.result_buffer.get_stats()

        report = {
            "test_summary": {
                "test_duration_seconds": round(test_duration, 2),
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate_percent": round(success_rate, 2),
                "requests_per_second": round(requests_per_second, 2),
                "concurrent_users": self.config.concurrent_users,
                "buffer_overflow_count": buffer_stats.get("overflow_count", 0)
            },
            "response_time_stats": {
                "average_ms": round(avg_response_time * 1000, 2),
                "minimum_ms": round(min_response_time * 1000, 2),
                "maximum_ms": round(max_response_time * 1000, 2),
                "p50_ms": round(p50_response_time * 1000, 2),
                "p90_ms": round(p90_response_time * 1000, 2),
                "p95_ms": round(p95_response_time * 1000, 2),
                "p99_ms": round(p99_response_time * 1000, 2)
            },
            "endpoint_statistics": dict(endpoint_stats),
            "system_resources": system_stats,
            "error_statistics": dict(error_stats),
            "error_samples": error_samples_summary,
            "user_statistics": {
                "total_users": len(user_stats),
                "avg_requests_per_user": round(total_requests / len(user_stats), 2) if user_stats else 0,
                "user_details": dict(user_stats) if len(user_stats) <= 50 else {}  # 只保存前50个用户详情
            },
            "test_config": asdict(self.config),
            "timestamp": datetime.now().isoformat(),
            "test_environment": {
                "python_version": sys.version,
                "platform": sys.platform,
                "cpu_count": psutil.cpu_count(),
                "total_memory_gb": round(psutil.virtual_memory().total / (1024**3), 2)
            }
        }

        return report

    def save_comprehensive_report(self, report: Dict[str, Any], filename: str = None):
        """保存全面的测试报告"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tests/stress_test_report_{self.config.concurrent_users}users_{timestamp}.json"

        try:
            # 确保tests目录存在
            os.makedirs("tests", exist_ok=True)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            # 同时保存简化版报告
            summary_filename = filename.replace('.json', '_summary.json')
            summary_report = {
                "test_summary": report["test_summary"],
                "response_time_stats": report["response_time_stats"],
                "endpoint_statistics": report["endpoint_statistics"],
                "system_resources": report["system_resources"],
                "timestamp": report["timestamp"]
            }

            with open(summary_filename, 'w', encoding='utf-8') as f:
                json.dump(summary_report, f, ensure_ascii=False, indent=2)

            logger.info(f"📄 详细测试报告已保存: {filename}")
            logger.info(f"📄 简化测试报告已保存: {summary_filename}")

            return filename, summary_filename

        except Exception as e:
            logger.error(f"保存报告失败: {e}")
            return None, None

    def print_comprehensive_summary(self, report: Dict[str, Any]):
        """打印全面的测试摘要"""
        summary = report["test_summary"]
        response_stats = report["response_time_stats"]
        system_stats = report.get("system_resources", {})
        user_stats = report.get("user_statistics", {})

        print("\n" + "="*100)
        print("🎯 高并发压力测试结果摘要")
        print("="*100)

        print(f"📊 测试概览:")
        print(f"   • 测试时长: {summary['test_duration_seconds']} 秒")
        print(f"   • 并发用户: {summary['concurrent_users']}")
        print(f"   • 总请求数: {summary['total_requests']}")
        print(f"   • 成功请求: {summary['successful_requests']}")
        print(f"   • 失败请求: {summary['failed_requests']}")
        print(f"   • 成功率: {summary['success_rate_percent']}%")
        print(f"   • 吞吐量: {summary['requests_per_second']} 请求/秒")
        if summary.get('buffer_overflow_count', 0) > 0:
            print(f"   ⚠️  缓冲区溢出: {summary['buffer_overflow_count']} 次")

        print(f"\n⏱️  响应时间统计:")
        print(f"   • 平均响应时间: {response_stats['average_ms']} ms")
        print(f"   • 最小响应时间: {response_stats['minimum_ms']} ms")
        print(f"   • 最大响应时间: {response_stats['maximum_ms']} ms")
        print(f"   • P50响应时间: {response_stats['p50_ms']} ms")
        print(f"   • P90响应时间: {response_stats['p90_ms']} ms")
        print(f"   • P95响应时间: {response_stats['p95_ms']} ms")
        print(f"   • P99响应时间: {response_stats['p99_ms']} ms")

        if system_stats:
            print(f"\n💻 系统资源使用:")
            print(f"   • CPU使用率: 平均 {system_stats.get('avg_cpu_percent', 0):.1f}% | "
                  f"最大 {system_stats.get('max_cpu_percent', 0):.1f}%")
            print(f"   • 内存使用率: 平均 {system_stats.get('avg_memory_percent', 0):.1f}% | "
                  f"最大 {system_stats.get('max_memory_percent', 0):.1f}%")
            print(f"   • 内存使用量: 最大 {system_stats.get('max_memory_used_mb', 0):.1f} MB")
            print(f"   • 活跃连接数: 平均 {system_stats.get('avg_active_connections', 0):.0f} | "
                  f"最大 {system_stats.get('max_active_connections', 0)}")

        print(f"\n👥 用户统计:")
        print(f"   • 参与用户数: {user_stats.get('total_users', 0)}")
        print(f"   • 平均每用户请求数: {user_stats.get('avg_requests_per_user', 0)}")

        print(f"\n🔍 端点性能详情:")
        query_mode_stats = defaultdict(lambda: {"total": 0, "success": 0, "response_times": []})
        text_length_stats = defaultdict(lambda: {"total": 0, "success": 0, "response_times": []})
        token_range_stats = defaultdict(lambda: {"total": 0, "success": 0, "response_times": []})

        for endpoint, stats in report["endpoint_statistics"].items():
            print(f"   • {endpoint}:")
            print(f"     - 请求数: {stats['total']} | 成功率: {stats['success_rate']:.1f}%")
            print(f"     - 响应时间: 平均 {stats['avg_response_time']*1000:.1f}ms | "
                  f"P95 {stats.get('p95_response_time', 0)*1000:.1f}ms")

            # 解析端点信息：/api/v1/query_mode_length_tokenstokens
            if "/api/v1/query_" in endpoint:
                parts = endpoint.split("_")
                if len(parts) >= 4:
                    mode = parts[2]
                    length = parts[3]

                    # 提取token数量
                    tokens_str = parts[4] if len(parts) > 4 else "0tokens"
                    tokens = int(tokens_str.replace("tokens", "")) if tokens_str.replace("tokens", "").isdigit() else 0

                    # 按token范围分类
                    if tokens <= 200:
                        token_range = "50-200"
                    elif tokens <= 800:
                        token_range = "200-800"
                    elif tokens <= 2000:
                        token_range = "800-2000"
                    elif tokens <= 5000:
                        token_range = "2000-5000"
                    else:
                        token_range = "5000-8000"

                    # 统计查询模式
                    query_mode_stats[mode]["total"] += stats['total']
                    query_mode_stats[mode]["success"] += stats['success']
                    query_mode_stats[mode]["response_times"].append(stats['avg_response_time'])

                    # 统计文本长度类别
                    text_length_stats[length]["total"] += stats['total']
                    text_length_stats[length]["success"] += stats['success']
                    text_length_stats[length]["response_times"].append(stats['avg_response_time'])

                    # 统计token范围
                    token_range_stats[token_range]["total"] += stats['total']
                    token_range_stats[token_range]["success"] += stats['success']
                    token_range_stats[token_range]["response_times"].append(stats['avg_response_time'])

        # 显示查询模式统计
        if query_mode_stats:
            print(f"\n📊 查询模式性能统计 (cs_college知识库):")
            for mode in ["local", "global", "hybrid", "naive", "mix", "bypass"]:
                if mode in query_mode_stats:
                    stats = query_mode_stats[mode]
                    success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
                    avg_time = statistics.mean(stats['response_times']) * 1000 if stats['response_times'] else 0
                    print(f"   • {mode:8}模式: {stats['total']:4}次 | 成功率: {success_rate:5.1f}% | 平均响应: {avg_time:6.1f}ms")

        # 显示文本长度统计
        if text_length_stats:
            print(f"\n📏 文本长度类别性能统计:")
            length_order = ["short", "medium", "long", "very_long", "ultra_long"]
            for length in length_order:
                if length in text_length_stats:
                    stats = text_length_stats[length]
                    success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
                    avg_time = statistics.mean(stats['response_times']) * 1000 if stats['response_times'] else 0
                    print(f"   • {length:10}: {stats['total']:4}次 | 成功率: {success_rate:5.1f}% | 平均响应: {avg_time:6.1f}ms")

        # 显示token范围统计
        if token_range_stats:
            print(f"\n🎯 Token范围性能统计:")
            token_ranges = ["50-200", "200-800", "800-2000", "2000-5000", "5000-8000"]
            for token_range in token_ranges:
                if token_range in token_range_stats:
                    stats = token_range_stats[token_range]
                    success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
                    avg_time = statistics.mean(stats['response_times']) * 1000 if stats['response_times'] else 0
                    print(f"   • {token_range:10} tokens: {stats['total']:4}次 | 成功率: {success_rate:5.1f}% | 平均响应: {avg_time:6.1f}ms")

        if report["error_statistics"]:
            print(f"\n❌ 错误统计:")
            for error, count in list(report["error_statistics"].items())[:10]:  # 只显示前10个错误
                print(f"   • {error}: {count} 次")
            if len(report["error_statistics"]) > 10:
                print(f"   • ... 还有 {len(report['error_statistics']) - 10} 种其他错误")

        # 性能评估
        print(f"\n🏆 性能评估:")
        avg_response = response_stats['average_ms']
        p95_response = response_stats['p95_ms']
        success_rate = summary['success_rate_percent']

        if success_rate >= 99.5 and avg_response <= 500 and p95_response <= 1000:
            print("   ✅ 优秀 - 系统在高并发下表现出色")
        elif success_rate >= 99 and avg_response <= 1000 and p95_response <= 2000:
            print("   ✅ 良好 - 系统性能满足要求")
        elif success_rate >= 95 and avg_response <= 2000:
            print("   ⚠️  一般 - 系统性能有待优化")
        else:
            print("   ❌ 需要优化 - 系统在高并发下存在性能问题")

        print("\n" + "="*100)


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="GuiXiaoXiRag 高并发压力测试工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 基础测试 (100用户, 10分钟, 70%智能查询)
  python tests/stress_test.py

  # 高并发测试 (1000用户, 30分钟, cs_college知识库)
  python tests/stress_test.py --users 1000 --duration 1800

  # 极限测试 (2000用户, 1小时, 自定义查询比例)
  python tests/stress_test.py --users 2000 --duration 3600 --query-ratio 0.8

  # 专项智能查询测试 (500用户, 15分钟, 90%智能查询)
  python tests/stress_test.py --users 500 --duration 900 --query-ratio 0.9 --qa-query-ratio 0.05
        """
    )

    parser.add_argument("--url", default="http://localhost:8002", help="服务器URL (默认: http://localhost:8002)")
    parser.add_argument("--users", type=int, default=100, help="并发用户数 (默认: 100)")
    parser.add_argument("--duration", type=int, default=600, help="测试持续时间(秒) (默认: 600)")
    parser.add_argument("--ramp-up", type=int, default=60, help="负载增加时间(秒) (默认: 60)")
    parser.add_argument("--ramp-down", type=int, default=30, help="负载减少时间(秒) (默认: 30)")

    # 测试比例配置
    parser.add_argument("--query-ratio", type=float, default=0.70, help="智能查询比例 (默认: 0.70)")
    parser.add_argument("--qa-query-ratio", type=float, default=0.15, help="问答查询比例 (默认: 0.15)")
    parser.add_argument("--qa-batch-ratio", type=float, default=0.05, help="批量查询比例 (默认: 0.05)")
    parser.add_argument("--qa-create-ratio", type=float, default=0.05, help="创建问答对比例 (默认: 0.05)")

    # 性能配置
    parser.add_argument("--pool-size", type=int, default=500, help="连接池大小 (默认: 500)")
    parser.add_argument("--per-host", type=int, default=100, help="每主机最大连接数 limit_per_host (默认: 100)")
    parser.add_argument("--timeout", type=int, default=30, help="请求超时时间(秒) (默认: 30)")
    parser.add_argument("--buffer-size", type=int, default=10000, help="结果缓冲区大小 (默认: 10000)")

    # 用户与限流模拟配置
    parser.add_argument("--min-interval-per-user", type=float, default=0.0, help="单用户最小请求间隔秒，用于避免同一用户频繁查询")
    parser.add_argument("--spoof-client-ip", action="store_true", help="为每个虚拟用户设置不同的客户端IP头以绕过IP级限流")
    parser.add_argument("--user-tier", type=str, default="default", help="为所有虚拟用户设置 X-User-Tier（default/free/pro/enterprise）")
    parser.add_argument("--error-sample-limit", type=int, default=50, help="每类错误采样条数上限")
    parser.add_argument("--error-sample-size", type=int, default=500, help="每条错误样本最大字符数")

    # 监控与垃圾回收配置
    parser.add_argument("--metrics-interval", type=int, default=5, help="系统指标采集间隔秒 (默认: 5)")
    parser.add_argument("--progress-interval", type=int, default=30, help="进度报告间隔秒 (默认: 30)")
    parser.add_argument("--gc-interval", type=int, default=100, help="触发垃圾回收的请求计数间隔 (默认: 100)")

    # 输出配置
    parser.add_argument("--output", help="报告输出文件名前缀")
    parser.add_argument("--quiet", action="store_true", help="静默模式，减少输出")

    args = parser.parse_args()

    # 验证参数
    if args.users > 2000:
        logger.warning("⚠️  用户数超过2000，请确保系统资源充足")

    ratio_sum = args.query_ratio + args.qa_query_ratio + args.qa_batch_ratio + args.qa_create_ratio
    if abs(ratio_sum - 1.0) > 0.05:  # 允许5%的误差，其余为健康检查
        logger.warning(f"⚠️  测试比例总和为 {ratio_sum:.2f}，建议调整为接近1.0")

    # 创建测试配置
    config = TestConfig(
        base_url=args.url,
        concurrent_users=args.users,
        test_duration=args.duration,
        ramp_up_time=args.ramp_up,
        ramp_down_time=args.ramp_down,
        query_ratio=args.query_ratio,
        qa_query_ratio=args.qa_query_ratio,
        qa_batch_ratio=args.qa_batch_ratio,
        qa_create_ratio=args.qa_create_ratio,
        health_ratio=0.05,
        connection_pool_size=args.pool_size,
        connection_per_host=args.per_host,
        request_timeout=args.timeout,
        result_buffer_size=args.buffer_size,
        # 用户与限流
        min_interval_per_user=args.min_interval_per_user,
        spoof_client_ip=args.spoof_client_ip,
        user_tier=args.user_tier,
        # 错误样本
        error_sample_limit=args.error_sample_limit,
        error_sample_size=args.error_sample_size,
        # 监控
        metrics_interval=args.metrics_interval,
        progress_report_interval=args.progress_interval,
        gc_interval=args.gc_interval
    )

    if not args.quiet:
        logger.info(f"🚀 准备启动高并发压力测试")
        logger.info(f"📊 配置: {args.users}用户 | {args.duration}秒 | {args.url}")

    # 创建测试运行器
    test_runner = HighConcurrencyStressTest(config)

    try:
        # 初始化
        await test_runner.setup()

        # 运行压力测试
        await test_runner.run_stress_test()

        # 生成报告
        report = test_runner.generate_comprehensive_report()

        # 保存报告
        detail_file, summary_file = test_runner.save_comprehensive_report(report, args.output)

        # 打印摘要
        if not args.quiet:
            test_runner.print_comprehensive_summary(report)

        logger.info("🎉 压力测试完成！")
        if detail_file:
            logger.info(f"📄 详细报告: {detail_file}")
        if summary_file:
            logger.info(f"📄 简化报告: {summary_file}")

    except KeyboardInterrupt:
        logger.info("⚠️  用户中断测试")
    except Exception as e:
        logger.error(f"❌ 测试执行失败: {e}")
        raise
    finally:
        # 清理资源
        await test_runner.cleanup()


if __name__ == "__main__":
    # 设置事件循环策略 (Windows兼容性)
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())
