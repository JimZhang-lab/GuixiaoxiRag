# DEBUG日志使用指南

## 📋 概述

GuixiaoxiRag测试套件现在支持详细的DEBUG级别日志，可以帮助开发者深入了解每个测试环节的执行过程，方便调试和问题排查。

## 🔍 启用DEBUG日志

### 方法1: 使用 --verbose 参数

```bash
# 启用详细模式，在控制台和日志文件中显示DEBUG信息
python main.py sync --verbose --no-text-insert
```

### 方法2: 使用专门的DEBUG测试脚本

```bash
# 运行专门的DEBUG测试
python debug_test.py
```

## 📊 DEBUG日志内容

### 1. 系统健康检查详细日志

```
DEBUG - 开始执行 System Health Check
DEBUG - 请求URL: http://localhost:8002/api/v1/health
DEBUG - 超时设置: 30秒
DEBUG - 发送GET请求...
DEBUG - 响应状态码: 200
DEBUG - 响应头: {'date': '...', 'server': 'uvicorn', ...}
DEBUG - 响应时间: 2.068秒
DEBUG - 响应大小: 280字节
DEBUG - 响应数据: {'status': 'healthy', 'timestamp': '...'}
DEBUG - 系统状态: healthy
DEBUG - 服务名称: GuiXiaoXiRag
DEBUG - 版本: 0.1.0
DEBUG - 运行时间: 2830.89秒
DEBUG - 工作目录: data\knowledgeBase/test_kb
```

### 2. QA健康检查详细日志

```
DEBUG - 开始执行 QA Health Check
DEBUG - 请求URL: http://localhost:8002/api/v1/qa/health
DEBUG - QA系统成功状态: True
DEBUG - QA存储状态: healthy
DEBUG - 嵌入状态: ready
DEBUG - 问答对总数: 19
DEBUG - 平均响应时间: 4.2秒
DEBUG - 错误率: 0.0
```

### 3. 创建问答对详细日志

```
DEBUG - 开始执行 Create QA Pair
DEBUG - 生成的问答对: {'question': '...', 'answer': '...'}
DEBUG - 问题: What is test_abc123?
DEBUG - 答案: test_abc123 is a test question for validation purposes.
DEBUG - 分类: sync_test
DEBUG - 置信度: 0.9
DEBUG - 请求头: {'Content-Type': 'application/json'}
DEBUG - 请求体大小: 234字符
DEBUG - 发送POST请求创建问答对...
DEBUG - 创建成功状态: True
DEBUG - 生成的问答对ID: qa_456789
```

### 4. QA查询详细日志

```
DEBUG - 开始执行 QA Query
DEBUG - 查询数据: {'question': 'What is testing', 'top_k': 5}
DEBUG - 查询问题: What is testing
DEBUG - 返回结果数量: 5
DEBUG - 查询成功状态: True
DEBUG - 是否找到匹配: True
DEBUG - 答案: Testing is the process of verifying...
DEBUG - 相似度: 0.95
DEBUG - 置信度: 0.89
DEBUG - 服务器响应时间: 4.6秒
DEBUG - 所有结果数量: 3
DEBUG - 结果1: 相似度=0.95, 问题=What is testing...
DEBUG - 结果2: 相似度=0.87, 问题=How to test...
```

### 5. 文本插入详细日志

```
DEBUG - 开始执行 Insert Text
DEBUG - 注意: 文本插入操作通常需要较长时间（30-60秒）
DEBUG - 生成的文档: {'text': '...', 'doc_id': 'doc_xyz'}
DEBUG - 文档ID: doc_xyz789
DEBUG - 文档语言: English
DEBUG - 知识库: test_kb
DEBUG - 文档内容长度: 87字符
DEBUG - 文档内容: This is a test document doc_xyz789...
DEBUG - 扩展超时时间: 120秒（原超时时间的2倍）
DEBUG - 发送POST请求进行文本插入...
DEBUG - 开始计时，文本插入可能需要较长时间...
DEBUG - 文本插入完成，总耗时: 45.234秒
DEBUG - 插入成功状态: True
DEBUG - 插入的文档ID: doc_xyz789
DEBUG - 创建的文档块数量: 3
DEBUG - 服务器处理时间: 44.8秒
```

### 6. 基本查询详细日志

```
DEBUG - 开始执行 Basic Query
DEBUG - 查询数据: {'query': 'What is artificial intelligence?', 'mode': 'hybrid', 'top_k': 5}
DEBUG - 查询内容: What is artificial intelligence?
DEBUG - 查询模式: hybrid
DEBUG - 返回结果数量: 5
DEBUG - 基本查询响应结构: ['success', 'message', 'data']
DEBUG - 查询成功状态: True
DEBUG - 查询结果长度: 1234字符
DEBUG - 查询结果预览: Artificial intelligence (AI) is a branch of computer science...
DEBUG - 使用的查询模式: hybrid
DEBUG - 服务器响应时间: 28.7秒
DEBUG - 上下文源数量: 2
```

### 7. 异常处理详细日志

```
DEBUG - 请求超时: HTTPSConnectionPool(host='localhost', port=8002): Read timed out.
DEBUG - 连接错误: HTTPSConnectionPool(host='localhost', port=8002): Max retries exceeded
DEBUG - JSON解析失败: Expecting value: line 1 column 1 (char 0)
DEBUG - 原始响应: <html><body>Internal Server Error</body></html>
DEBUG - 未知异常: 'NoneType' object has no attribute 'json'
DEBUG - 异常类型: AttributeError
DEBUG - 异常堆栈: Traceback (most recent call last):...
```

## 🛠️ 调试技巧

### 1. 查看特定测试的详细信息

```bash
# 只运行系统健康检查，查看详细日志
python debug_test.py
```

### 2. 分析响应时间

DEBUG日志会记录每个请求的详细时间信息：
- 请求发送时间
- 响应接收时间
- 总耗时
- 服务器处理时间

### 3. 检查请求和响应数据

DEBUG日志包含完整的：
- 请求URL和参数
- 请求头信息
- 响应头信息
- 响应数据内容
- 数据解析结果

### 4. 监控系统状态

通过DEBUG日志可以监控：
- 服务运行状态
- 系统资源使用
- 数据库连接状态
- 缓存命中率

## 📁 日志文件位置

DEBUG日志会同时输出到：

1. **控制台**: 实时显示（使用 --verbose 参数）
2. **日志文件**: `logs/test_YYYYMMDD_HHMMSS.log`

### 日志文件格式

```
2025-08-22 00:30:56 - SyncTestRunner - DEBUG - 开始执行 System Health Check
2025-08-22 00:30:56 - SyncTestRunner - DEBUG - 请求URL: http://localhost:8002/api/v1/health
2025-08-22 00:30:56 - SyncTestRunner - DEBUG - 超时设置: 30秒
```

格式说明：
- `时间戳` - 精确到秒
- `Logger名称` - 标识日志来源
- `日志级别` - DEBUG/INFO/WARNING/ERROR
- `日志内容` - 具体的调试信息

## 🔧 故障排除

### 1. DEBUG日志不显示

**问题**: 运行测试时看不到DEBUG日志

**解决方案**:
```bash
# 确保使用 --verbose 参数
python main.py sync --verbose

# 或者检查日志文件
cat logs/test_*.log | grep DEBUG
```

### 2. 日志文件过大

**问题**: DEBUG日志文件太大

**解决方案**:
```bash
# 测试后自动清理
python main.py sync --verbose --clean-after

# 或者只清理日志
python main.py --clean-only
```

### 3. 特定测试的DEBUG信息

**问题**: 只想看某个测试的详细信息

**解决方案**:
```bash
# 使用专门的DEBUG测试脚本
python debug_test.py

# 或者在日志文件中搜索
grep "System Health Check" logs/test_*.log -A 20
```

## 📈 性能分析

DEBUG日志可以帮助分析性能瓶颈：

### 1. 响应时间分析

```bash
# 从日志中提取响应时间
grep "响应时间" logs/test_*.log
```

### 2. 超时问题诊断

```bash
# 查找超时相关的日志
grep -i "timeout\|超时" logs/test_*.log
```

### 3. 错误模式识别

```bash
# 查找所有错误日志
grep "ERROR\|异常\|失败" logs/test_*.log
```

## 🎯 最佳实践

1. **开发阶段**: 始终使用 `--verbose` 参数
2. **生产测试**: 只在需要时启用DEBUG日志
3. **问题排查**: 结合控制台输出和日志文件
4. **性能监控**: 定期分析响应时间趋势
5. **日志管理**: 定期清理旧的日志文件

---

**提示**: DEBUG日志包含大量详细信息，建议在开发和调试阶段使用，生产环境中可以关闭以提高性能。
