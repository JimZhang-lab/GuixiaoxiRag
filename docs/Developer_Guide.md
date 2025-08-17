# GuiXiaoXiRag 开发者指南

## 概述

本指南为 GuiXiaoXiRag 项目的开发者提供详细的开发环境设置、代码规范、架构说明和贡献指南。

## 开发环境设置

### 1. 环境要求

- **Python**: 3.8+ (推荐 3.9)
- **Git**: 2.20+
- **IDE**: VS Code, PyCharm 或其他支持 Python 的 IDE
- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

### 2. 开发环境配置

#### 克隆项目
```bash
git clone <repository-url>
cd server_new
```

#### 创建虚拟环境
```bash
# 使用 venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 使用 conda
conda create -n guixiaoxirag python=3.9
conda activate guixiaoxirag
```

#### 安装依赖
```bash
# 安装生产依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt
```

#### 配置开发环境
```bash
# 复制开发配置
cp .env.example .env.development

# 编辑开发配置
nano .env.development
```

#### 开发配置示例
```bash
# .env.development
DEBUG=true
LOG_LEVEL=DEBUG
HOST=127.0.0.1
PORT=8002

# 使用本地模拟服务
OPENAI_API_BASE=http://localhost:8100/v1
OPENAI_EMBEDDING_API_BASE=http://localhost:8200/v1
OPENAI_CHAT_API_KEY=test_key
OPENAI_EMBEDDING_API_KEY=test_key

# 开发数据库
WORKING_DIR=./knowledgeBase/dev
LOG_DIR=./logs/dev
```

### 3. IDE 配置

#### VS Code 配置
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI Debug",
            "type": "python",
            "request": "launch",
            "program": "main.py",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}",
                "ENV_FILE": ".env.development"
            }
        }
    ]
}
```

#### PyCharm 配置
1. 设置 Python 解释器为虚拟环境
2. 配置代码格式化工具 (Black)
3. 启用 Type Checking
4. 配置运行配置

## 项目结构详解

### 目录结构
```
server_new/
├── api/                    # API业务逻辑层
│   ├── __init__.py
│   ├── query_api.py       # 查询API处理器
│   ├── document_api.py    # 文档管理API
│   ├── knowledge_base_api.py  # 知识库管理API
│   ├── knowledge_graph_api.py # 知识图谱API
│   ├── system_api.py      # 系统管理API
│   ├── intent_recogition_api.py # 意图识别API
│   └── cache_management_api.py  # 缓存管理API
├── routers/               # FastAPI路由层
│   ├── __init__.py
│   ├── query_router.py    # 查询路由
│   ├── document_router.py # 文档管理路由
│   ├── knowledge_base_router.py # 知识库路由
│   ├── knowledge_graph_router.py # 知识图谱路由
│   ├── system_router.py   # 系统管理路由
│   ├── intent_recogition_router.py # 意图识别路由
│   └── cache_management_router.py  # 缓存管理路由
├── model/                 # 数据模型层
│   ├── __init__.py
│   ├── base_models.py     # 基础模型
│   ├── request_models.py  # 请求模型
│   ├── response_models.py # 响应模型
│   ├── document_models.py # 文档模型
│   ├── query_models.py    # 查询模型
│   ├── intent_recogition_models.py # 意图识别模型
│   └── system_models.py   # 系统模型
├── handler/               # 核心处理器
│   ├── __init__.py
│   ├── guixiaoxirag_service.py # 核心服务
│   ├── document_processor.py   # 文档处理器
│   ├── knowledge_base_manager.py # 知识库管理器
│   └── query_processor.py      # 查询处理器
├── core/                  # 核心算法
│   ├── __init__.py
│   ├── rag/              # RAG相关算法
│   ├── intent_recognition/ # 意图识别
│   └── quick_qa_base/    # 快速问答基础
├── common/                # 公共组件
│   ├── __init__.py
│   ├── config.py         # 配置管理
│   ├── utils.py          # 工具函数
│   ├── logging_utils.py  # 日志工具
│   ├── constants.py      # 常量定义
│   ├── file_utils.py     # 文件工具
│   └── performance_config.py # 性能配置
├── middleware/            # 中间件
│   ├── __init__.py
│   ├── cors_middleware.py # CORS中间件
│   ├── logging_middleware.py # 日志中间件
│   ├── metrics_middleware.py # 指标中间件
│   └── security_middleware.py # 安全中间件
├── initialize/            # 初始化模块
│   ├── __init__.py
│   ├── app_initializer.py # 应用初始化
│   ├── middleware_initializer.py # 中间件初始化
│   └── service_initializer.py # 服务初始化
├── tests/                 # 测试目录
│   ├── __init__.py
│   ├── test_api_comprehensive.py # 综合API测试
│   ├── unit/             # 单元测试
│   ├── integration/      # 集成测试
│   └── fixtures/         # 测试数据
├── docs/                  # 文档目录
├── scripts/               # 脚本目录
├── knowledgeBase/         # 知识库存储
├── logs/                  # 日志目录
├── uploads/               # 上传目录
├── main.py               # 应用入口
├── requirements.txt      # 生产依赖
├── requirements-dev.txt  # 开发依赖
├── .env.example         # 配置模板
├── .gitignore           # Git忽略文件
└── README.md            # 项目说明
```

### 模块职责

#### API层 (api/)
- **职责**: 处理业务逻辑，数据验证，错误处理
- **原则**: 单一职责，依赖注入，异常处理
- **模式**: 策略模式，工厂模式

#### 路由层 (routers/)
- **职责**: HTTP请求路由，参数验证，响应格式化
- **原则**: RESTful设计，统一响应格式
- **模式**: 装饰器模式，中间件模式

#### 模型层 (model/)
- **职责**: 数据结构定义，验证规则，序列化
- **原则**: 类型安全，数据验证，文档化
- **工具**: Pydantic，Type Hints

#### 处理器层 (handler/)
- **职责**: 核心业务逻辑，算法调用，数据处理
- **原则**: 高内聚，低耦合，可测试
- **模式**: 单例模式，观察者模式

## 代码规范

### 1. Python 代码规范

#### 基础规范
- 遵循 PEP 8 代码风格
- 使用 Black 进行代码格式化
- 使用 isort 进行导入排序
- 使用 Type Hints 进行类型注解

#### 命名规范
```python
# 类名：大驼峰命名
class QueryProcessor:
    pass

# 函数名：小写下划线
def process_query():
    pass

# 变量名：小写下划线
user_input = "example"

# 常量：大写下划线
MAX_RETRY_COUNT = 3

# 私有成员：前缀下划线
class Example:
    def __init__(self):
        self._private_var = None
        self.__very_private = None
```

#### 文档字符串规范
```python
def process_query(query: str, mode: str = "hybrid") -> Dict[str, Any]:
    """
    处理查询请求
    
    Args:
        query (str): 查询内容
        mode (str, optional): 查询模式. Defaults to "hybrid".
    
    Returns:
        Dict[str, Any]: 查询结果
        
    Raises:
        ValueError: 当查询内容为空时
        HTTPException: 当查询模式不支持时
        
    Examples:
        >>> result = process_query("什么是AI？", "hybrid")
        >>> print(result["answer"])
    """
    pass
```

#### 类型注解规范
```python
from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    mode: Optional[str] = "hybrid"
    top_k: int = 20
    filters: Optional[Dict[str, Any]] = None

async def query_api(
    request: QueryRequest,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """API处理函数"""
    pass
```

### 2. 错误处理规范

#### 异常层次结构
```python
# common/exceptions.py
class GuiXiaoXiRagException(Exception):
    """基础异常类"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class ValidationError(GuiXiaoXiRagException):
    """参数验证错误"""
    pass

class BusinessError(GuiXiaoXiRagException):
    """业务逻辑错误"""
    pass

class ExternalServiceError(GuiXiaoXiRagException):
    """外部服务错误"""
    pass
```

#### 错误处理模式
```python
from common.exceptions import BusinessError, ValidationError
from common.logging_utils import logger_manager

logger = logger_manager.get_logger(__name__)

async def api_function(request: RequestModel):
    """API函数错误处理示例"""
    try:
        # 参数验证
        if not request.query.strip():
            raise ValidationError("查询内容不能为空", "EMPTY_QUERY")
        
        # 业务逻辑处理
        result = await process_business_logic(request)
        
        return {"success": True, "data": result}
        
    except ValidationError as e:
        logger.warning(f"参数验证失败: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
        
    except BusinessError as e:
        logger.error(f"业务逻辑错误: {e.message}")
        raise HTTPException(status_code=500, detail=e.message)
        
    except Exception as e:
        logger.error(f"未知错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="系统内部错误")
```

### 3. 日志规范

#### 日志配置
```python
# common/logging_utils.py
import logging
from typing import Optional

class LoggerManager:
    def __init__(self):
        self.loggers = {}
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取日志记录器"""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            logger.setLevel(logging.INFO)
            
            # 配置处理器
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            self.loggers[name] = logger
        
        return self.loggers[name]

logger_manager = LoggerManager()
```

#### 日志使用规范
```python
from common.logging_utils import logger_manager

logger = logger_manager.get_logger(__name__)

async def example_function(param: str):
    """日志使用示例"""
    logger.info(f"开始处理请求: {param[:50]}...")
    
    try:
        # 业务逻辑
        result = await process_data(param)
        logger.info(f"处理完成，结果长度: {len(result)}")
        return result
        
    except Exception as e:
        logger.error(f"处理失败: {str(e)}", exc_info=True)
        raise
```

## 开发工作流

### 1. 功能开发流程

#### 创建功能分支
```bash
# 从主分支创建功能分支
git checkout main
git pull origin main
git checkout -b feature/new-feature-name
```

#### 开发步骤
1. **需求分析**: 明确功能需求和接口设计
2. **模型定义**: 在 `model/` 中定义数据模型
3. **API实现**: 在 `api/` 中实现业务逻辑
4. **路由添加**: 在 `routers/` 中添加路由定义
5. **测试编写**: 编写单元测试和集成测试
6. **文档更新**: 更新API文档和使用说明

#### 代码提交
```bash
# 添加文件
git add .

# 提交代码
git commit -m "feat: 添加新功能描述

- 详细描述功能变更
- 说明影响范围
- 相关issue编号"

# 推送分支
git push origin feature/new-feature-name
```

### 2. 提交信息规范

#### 提交类型
- `feat`: 新功能
- `fix`: 错误修复
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

#### 提交格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

#### 示例
```
feat(api): 添加批量查询功能

- 实现批量查询API端点
- 支持并行处理多个查询
- 添加超时控制和错误处理
- 更新相关文档和测试

Closes #123
```

### 3. 代码审查

#### 审查清单
- [ ] 代码符合项目规范
- [ ] 功能实现正确
- [ ] 错误处理完善
- [ ] 测试覆盖充分
- [ ] 文档更新及时
- [ ] 性能影响评估
- [ ] 安全性检查

#### 审查工具
```bash
# 代码格式检查
black --check .
isort --check-only .

# 代码质量检查
flake8 .
pylint api/ routers/ model/

# 类型检查
mypy .

# 安全检查
bandit -r .
```

## 测试指南

### 1. 测试结构

```
tests/
├── unit/                  # 单元测试
│   ├── test_api/         # API层测试
│   ├── test_handlers/    # 处理器测试
│   ├── test_models/      # 模型测试
│   └── test_utils/       # 工具函数测试
├── integration/          # 集成测试
│   ├── test_api_integration.py
│   └── test_service_integration.py
├── fixtures/             # 测试数据
│   ├── sample_documents/
│   └── test_data.json
├── conftest.py          # pytest配置
└── __init__.py
```

### 2. 单元测试示例

```python
# tests/unit/test_api/test_query_api.py
import pytest
from unittest.mock import Mock, AsyncMock
from api.query_api import QueryAPI
from model.request_models import QueryRequest

class TestQueryAPI:
    @pytest.fixture
    def query_api(self):
        """创建QueryAPI实例"""
        return QueryAPI()
    
    @pytest.fixture
    def sample_request(self):
        """创建示例请求"""
        return QueryRequest(
            query="什么是人工智能？",
            mode="hybrid",
            top_k=10
        )
    
    @pytest.mark.asyncio
    async def test_query_success(self, query_api, sample_request):
        """测试查询成功场景"""
        # Mock依赖
        query_api.query_processor = AsyncMock()
        query_api.query_processor.process_query.return_value = {
            "answer": "人工智能是...",
            "sources": [],
            "query_time": 1.5
        }
        
        # 执行测试
        result = await query_api.query(sample_request)
        
        # 验证结果
        assert result["success"] is True
        assert "answer" in result["data"]
        assert result["data"]["answer"] == "人工智能是..."
    
    @pytest.mark.asyncio
    async def test_query_empty_input(self, query_api):
        """测试空查询输入"""
        request = QueryRequest(query="", mode="hybrid")
        
        with pytest.raises(HTTPException) as exc_info:
            await query_api.query(request)
        
        assert exc_info.value.status_code == 400
        assert "查询内容不能为空" in str(exc_info.value.detail)
```

### 3. 集成测试示例

```python
# tests/integration/test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from main import app

class TestAPIIntegration:
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)
    
    def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_query_endpoint(self, client):
        """测试查询端点"""
        query_data = {
            "query": "测试查询",
            "mode": "hybrid",
            "top_k": 5
        }
        
        response = client.post("/api/v1/query", json=query_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
```

### 4. 测试运行

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/unit/test_api/

# 运行并生成覆盖率报告
pytest --cov=. --cov-report=html

# 运行性能测试
pytest tests/performance/ -v

# 并行运行测试
pytest -n auto
```

## 性能优化

### 1. 代码性能

#### 异步编程
```python
import asyncio
from typing import List

async def process_multiple_queries(queries: List[str]) -> List[dict]:
    """并行处理多个查询"""
    tasks = [process_single_query(query) for query in queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 处理异常结果
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                "query": queries[i],
                "error": str(result),
                "success": False
            })
        else:
            processed_results.append(result)
    
    return processed_results
```

#### 缓存优化
```python
from functools import lru_cache
from typing import Optional
import hashlib

class CacheManager:
    def __init__(self):
        self.cache = {}
    
    def get_cache_key(self, query: str, mode: str) -> str:
        """生成缓存键"""
        content = f"{query}:{mode}"
        return hashlib.md5(content.encode()).hexdigest()
    
    @lru_cache(maxsize=1000)
    def get_cached_result(self, cache_key: str) -> Optional[dict]:
        """获取缓存结果"""
        return self.cache.get(cache_key)
    
    def set_cache(self, cache_key: str, result: dict, ttl: int = 3600):
        """设置缓存"""
        self.cache[cache_key] = {
            "data": result,
            "timestamp": time.time(),
            "ttl": ttl
        }
```

### 2. 数据库优化

#### 批量操作
```python
async def batch_insert_documents(documents: List[dict]) -> List[str]:
    """批量插入文档"""
    batch_size = 100
    doc_ids = []
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        batch_ids = await insert_document_batch(batch)
        doc_ids.extend(batch_ids)
    
    return doc_ids
```

#### 连接池管理
```python
import asyncio
from typing import AsyncGenerator

class ConnectionPool:
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.pool = asyncio.Queue(maxsize=max_connections)
        self._initialize_pool()
    
    async def get_connection(self) -> AsyncGenerator:
        """获取连接"""
        connection = await self.pool.get()
        try:
            yield connection
        finally:
            await self.pool.put(connection)
```

## 调试技巧

### 1. 日志调试

```python
import logging
from functools import wraps

def debug_log(func):
    """调试装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.debug(f"调用函数: {func.__name__}")
        logger.debug(f"参数: args={args}, kwargs={kwargs}")
        
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"返回结果: {type(result)}")
            return result
        except Exception as e:
            logger.error(f"函数执行失败: {e}", exc_info=True)
            raise
    
    return wrapper

@debug_log
async def example_function(param: str):
    """示例函数"""
    return f"处理结果: {param}"
```

### 2. 性能分析

```python
import time
import cProfile
import pstats
from functools import wraps

def profile_performance(func):
    """性能分析装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # 使用cProfile分析
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            profiler.disable()
            
            # 输出性能统计
            stats = pstats.Stats(profiler)
            stats.sort_stats('cumulative')
            stats.print_stats(10)  # 显示前10个最耗时的函数
            
            execution_time = time.time() - start_time
            print(f"函数 {func.__name__} 执行时间: {execution_time:.4f}秒")
    
    return wrapper
```

### 3. 内存监控

```python
import psutil
import tracemalloc
from typing import Dict, Any

class MemoryMonitor:
    def __init__(self):
        self.start_memory = None
    
    def start_monitoring(self):
        """开始内存监控"""
        tracemalloc.start()
        self.start_memory = psutil.Process().memory_info().rss
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """获取内存使用情况"""
        current_memory = psutil.Process().memory_info().rss
        memory_diff = current_memory - self.start_memory if self.start_memory else 0
        
        # 获取内存快照
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        return {
            "current_memory_mb": current_memory / 1024 / 1024,
            "memory_diff_mb": memory_diff / 1024 / 1024,
            "top_memory_usage": [
                {
                    "file": stat.traceback.format()[0],
                    "size_mb": stat.size / 1024 / 1024
                }
                for stat in top_stats[:5]
            ]
        }
```

## 贡献指南

### 1. 贡献流程

1. **Fork 项目**
2. **创建功能分支**
3. **实现功能**
4. **编写测试**
5. **更新文档**
6. **提交 Pull Request**

### 2. Pull Request 规范

#### PR 标题格式
```
<type>: <description>

例如:
feat: 添加批量文档上传功能
fix: 修复查询缓存失效问题
docs: 更新API文档
```

#### PR 描述模板
```markdown
## 变更类型
- [ ] 新功能
- [ ] 错误修复
- [ ] 文档更新
- [ ] 性能优化
- [ ] 代码重构

## 变更描述
简要描述本次变更的内容和目的。

## 测试
- [ ] 添加了新的测试
- [ ] 所有测试通过
- [ ] 手动测试通过

## 文档
- [ ] 更新了相关文档
- [ ] 添加了代码注释

## 检查清单
- [ ] 代码符合项目规范
- [ ] 没有引入新的安全问题
- [ ] 性能没有明显下降
- [ ] 向后兼容

## 相关Issue
Closes #123
```

### 3. 代码审查标准

#### 功能性
- 功能实现正确
- 边界条件处理
- 错误处理完善

#### 可维护性
- 代码结构清晰
- 命名规范合理
- 注释文档完整

#### 性能
- 算法效率合理
- 资源使用优化
- 缓存策略恰当

#### 安全性
- 输入验证充分
- 权限控制正确
- 敏感信息保护

---

*本开发者指南提供了完整的开发环境设置和最佳实践，帮助开发者高效地参与项目开发。*
