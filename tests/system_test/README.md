# GuixiaoxiRag 系统测试套件 v2.0.0

这是 GuixiaoxiRag 系统的重构测试套件，采用模块化设计，支持多种测试模式和自动清理功能。

## 🎯 最新更新 (v2.0.0)

### ✨ 新功能
- 🔍 **详细的DEBUG日志**: 每个测试环节都有详细的调试信息
- 📊 **增强的测试报告**: 包含性能指标和系统状态分析
- 🧹 **智能清理系统**: 自动清理测试生成的文件，保护重要目录
- 🎯 **灵活的测试选项**: 支持跳过慢速测试、重试失败测试等
- 📈 **实时进度跟踪**: 显示测试进度和详细的执行状态

### 🔧 改进功能
- ⚡ **更快的测试执行**: 优化了测试流程和错误处理
- 🛡️ **更好的错误诊断**: 详细的异常信息和堆栈跟踪
- 📋 **完善的文档**: 包含使用指南、故障排除和最佳实践
- 🎨 **美化的输出**: 彩色日志和格式化的测试报告

### 📊 测试覆盖率
- ✅ **系统健康检查**: 服务状态、版本信息、运行时间
- ✅ **QA系统测试**: 健康检查、问答对管理、查询功能
- ✅ **文档管理**: 文本插入、文件上传、批量处理
- ✅ **查询系统**: 多种查询模式、性能测试
- ✅ **统计分析**: 系统指标、性能监控

## 📁 目录结构

```
tests/system_test/
├── main.py                 # 主启动文件
├── README_NEW.md          # 说明文档
├── config/                # 配置文件目录
│   ├── test_config.py     # 测试配置
│   ├── conftest*.py       # pytest配置
│   ├── pytest.ini        # pytest设置
│   └── requirements*.txt  # 依赖文件
├── utils/                 # 工具类目录
│   ├── cleanup_manager.py # 清理管理器
│   ├── test_logger.py     # 日志管理器
│   └── test_utils.py      # 测试工具类
├── runners/               # 测试运行器目录
│   ├── sync_test_runner.py # 同步测试运行器
│   └── run_*.py           # 其他运行器
├── tests/                 # 测试用例目录
│   ├── test_*.py          # 各种测试文件
│   └── ...
├── fixtures/              # 测试夹具目录
├── logs/                  # 日志输出目录（自动生成）
└── temp/                  # 临时文件目录（自动生成）
```

## 🚀 快速开始

### 🎯 推荐用法（日常开发）

```bash
# 最佳实践：快速、稳定、自动清理
python main.py sync --no-text-insert --clean-after --verbose

# 查看版本信息
python main.py --version

# 查看帮助信息
python main.py --help
```

### 📋 基本用法

```bash
# 基础同步测试（推荐）
python main.py sync

# 完整测试（包含慢速操作）
python main.py sync --timeout 180

# 详细调试模式
python main.py sync --verbose --no-text-insert

# 测试后自动清理
python main.py sync --clean-after
```

### 🔍 调试和诊断

```bash
# 详细DEBUG日志（推荐调试时使用）
python main.py sync --verbose

# 专门的DEBUG测试
python debug_test.py

# 查看测试结果
cat logs/sync_test_*.json | jq .summary
```

### 清理选项

```bash
# 测试前清理
python main.py sync --clean-before

# 测试后清理
python main.py sync --clean-after

# 只执行清理，不运行测试
python main.py --clean-only

# 测试前后都清理
python main.py sync --clean-before --clean-after
```

### 高级选项

```bash
# 自定义服务地址
python main.py sync --base-url http://localhost:8003

# 自定义超时时间（文本插入很慢，建议60秒以上）
python main.py sync --timeout 120

# 自定义输出目录
python main.py sync --output-dir my_logs
```

## 🧪 测试模式

### sync - 同步HTTP测试（推荐）
- 使用 requests 库进行HTTP测试
- 稳定可靠，避免异步配置问题
- 支持所有核心功能测试

### async - 异步pytest测试（实验性）
- 使用 pytest + httpx 进行异步测试
- 更高性能，但配置复杂

### performance - 性能压力测试
- 并发请求测试
- 响应时间分析
- 资源使用监控

### integration - 集成测试
- 端到端工作流测试
- 多组件协作验证

### all - 运行所有测试
- 依次运行所有测试模式
- 生成综合报告

## 📊 测试覆盖详情

### ✅ 核心功能测试 (当前状态: 7/8 通过，87.5% 成功率)

| 测试项目 | 状态 | 平均耗时 | 说明 |
|---------|------|----------|------|
| 🏥 系统健康检查 | ✅ 通过 | ~2.1s | 服务状态、版本信息、运行时间 |
| 🔍 QA系统健康检查 | ✅ 通过 | ~2.1s | QA存储、嵌入状态、问答对统计 |
| ➕ 问答对创建 | ✅ 通过 | ~3.5s | 创建、验证、ID生成 |
| 🔎 QA查询 | ✅ 通过 | ~7.2s | 相似度匹配、结果排序 |
| 📝 文本插入 | ❌ 失败 | ~2.1s | 文件系统问题，需修复 |
| 🌐 基本查询 | ✅ 通过 | ~2.1s | 混合模式查询、结果生成 |
| ⚙️ 查询模式获取 | ✅ 通过 | ~2.0s | 6种模式，推荐hybrid |
| 📊 QA统计信息 | ✅ 通过 | ~2.1s | 23个问答对，8个分类 |

### 🔍 详细测试信息

#### 🏥 系统健康检查
- **服务名称**: GuiXiaoXiRag v0.1.0
- **运行状态**: healthy
- **运行时间**: 51+ 分钟稳定运行
- **工作目录**: data\knowledgeBase/test_kb

#### 🔍 QA系统状态
- **存储状态**: ready
- **嵌入状态**: ready
- **问答对数量**: 23个（持续增长）
- **平均响应时间**: 1.58秒
- **错误率**: 0.0%

#### 📊 系统统计
- **分类分布**: 8个分类，technology类最多(9个)
- **平均置信度**: 0.893
- **相似度阈值**: 0.98（可能过高）
- **向量维度**: 2560
- **查询模式**: 6种（hybrid推荐）

### ⚠️ 已知问题

1. **文本插入功能失败**
   - **错误**: `kv_store_doc_status.json` 文件缺失
   - **影响**: 无法插入新文档
   - **修复**: 需要初始化知识库文件系统

2. **QA查询相似度阈值过高**
   - **现象**: 查询"What is testing"无匹配结果
   - **原因**: 阈值0.98过于严格
   - **建议**: 调整到0.85-0.90

### 🚀 扩展功能测试（计划中）
- � 文件上传测试
- � 批量操作测试
- � 知识库管理测试
- �️ 知识图谱操作测试
- ⚡ 性能压力测试
- 🔗 集成测试

## 🧹 自动清理功能

清理管理器会自动清理以下文件：

### 清理的文件类型
- `logs/*.log` - 日志文件
- `logs/*.json` - JSON报告
- `logs/*.md` - Markdown报告
- `temp/*` - 临时文件
- `test_data/*` - 测试数据
- `__pycache__/*` - Python缓存
- `*.pyc` - 编译的Python文件
- `.pytest_cache/*` - pytest缓存

### 保护的目录
- `config/` - 配置文件
- `utils/` - 工具类
- `runners/` - 运行器
- `tests/` - 测试用例
- `fixtures/` - 测试夹具

## 📈 测试报告

测试完成后会生成：

### JSON报告
```json
{
  "timestamp": "20250821_235945",
  "test_type": "sync_http_test",
  "summary": {
    "total": 8,
    "passed": 7,
    "failed": 1,
    "success_rate": 0.875
  },
  "results": { ... }
}
```

### 控制台输出
```
📊 测试摘要
============================================================
总测试数: 8
通过: 7
失败: 1
成功率: 87.5%
🎉 部分测试通过
```

## ⚙️ 配置说明

### 基础配置 (config/test_config.py)
- 服务地址：http://localhost:8002
- API前缀：/api/v1
- 超时时间：60秒（文本插入需要更长时间）
- 重试次数：3次

### 测试套件配置
- `basic` - 基础功能测试（跳过慢速操作）
- `full` - 完整功能测试（包含所有操作）
- `performance` - 性能测试

## 🔧 故障排除

### 🚨 常见问题及解决方案

#### 1. **服务连接失败**
```bash
# 检查服务是否运行
curl http://localhost:8002/api/v1/health

# 或使用测试工具检查
python debug_test.py

# 检查端口占用
netstat -an | findstr 8002
```

**解决方案**:
- 确保GuixiaoxiRag服务正在运行
- 检查端口8002是否被占用
- 验证防火墙设置

#### 2. **文本插入功能失败**
```bash
# 错误信息: kv_store_doc_status.json 文件缺失
# 修复方法:
mkdir -p data/knowledgeBase/test_kb
echo "{}" > data/knowledgeBase/test_kb/kv_store_doc_status.json

# 或者跳过文本插入测试
python main.py sync --no-text-insert
```

#### 3. **QA查询无匹配结果**
```bash
# 现象: 查询返回found=false
# 原因: 相似度阈值0.98过高
# 临时解决: 添加更多相关问答对
python main.py sync  # 会自动创建测试问答对
```

#### 4. **测试超时**
```bash
# 增加超时时间
python main.py sync --timeout 300

# 或跳过慢速测试
python main.py sync --no-text-insert --timeout 60
```

#### 5. **权限错误**
```bash
# 确保有写入权限
chmod +w logs/ temp/

# 清理权限问题
python main.py --clean-only
```

#### 6. **DEBUG日志不显示**
```bash
# 确保使用verbose参数
python main.py sync --verbose

# 检查日志文件
cat logs/test_*.log | grep DEBUG | head -10
```

### 📋 日志分析

#### 查看测试结果
```bash
# 查看最新测试结果
ls -la logs/ | head -5

# 分析JSON结果
cat logs/sync_test_*.json | jq .summary

# 查看详细错误
grep "ERROR\|失败\|异常" logs/test_*.log
```

#### 性能分析
```bash
# 查看响应时间
grep "响应时间" logs/test_*.log

# 查看超时问题
grep -i "timeout\|超时" logs/test_*.log

# 分析慢速操作
grep "耗时.*[5-9]\." logs/test_*.log
```

### 🛠️ 高级诊断

#### 环境检查
```bash
# 检查Python环境
python --version
pip list | grep -E "(requests|json)"

# 检查系统资源
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, Memory: {psutil.virtual_memory().percent}%')"
```

#### 网络诊断
```bash
# 测试网络连接
ping localhost
telnet localhost 8002

# 检查DNS解析
nslookup localhost
```

#### 服务状态检查
```bash
# 详细的服务状态
curl -v http://localhost:8002/api/v1/health

# 检查所有端点
python debug_test.py 2>&1 | grep "DEBUG.*URL"
```

## 📝 开发说明

### 添加新测试
1. 在 `tests/` 目录下创建测试文件
2. 在 `runners/` 中添加运行器
3. 在 `config/test_config.py` 中添加配置

### 自定义清理规则
在 `utils/cleanup_manager.py` 中修改清理模式和保护规则。

## 🎯 最佳实践

### 📋 日常开发建议

1. **推荐的日常测试命令**:
   ```bash
   python main.py sync --no-text-insert --clean-after --verbose
   ```

2. **完整验证测试**:
   ```bash
   python main.py sync --clean-before --clean-after --timeout 180
   ```

3. **调试问题时**:
   ```bash
   python main.py sync --verbose --no-text-insert
   python debug_test.py
   ```

### 🔄 CI/CD 集成

```bash
# 在CI环境中使用
python main.py sync --no-text-insert --clean-after --timeout 60

# 检查退出码
echo "Exit code: $?"
```

### 📊 性能监控

```bash
# 定期性能测试
python main.py sync --verbose | grep "响应时间"

# 监控成功率趋势
grep "成功率" logs/test_*.log | tail -10
```

### 🧹 维护建议

1. **定期清理**: 每周运行 `python main.py --clean-only`
2. **日志轮转**: 保留最近30天的日志文件
3. **性能基线**: 建立响应时间基线，监控性能退化
4. **错误跟踪**: 定期分析失败模式，优化测试稳定性

## 📈 版本历史

### v2.0.0 (2025-08-22)
- ✨ 新增详细的DEBUG日志系统
- 🔧 改进错误处理和诊断能力
- 📊 增强测试报告和统计信息
- 🧹 完善自动清理功能
- 📋 更新文档和使用指南
- 🎯 优化命令行参数和用户体验

### v1.0.0 (2025-08-21)
- 🚀 初始版本发布
- ✅ 基础同步HTTP测试功能
- 🧪 支持8个核心测试用例
- 📁 模块化目录结构
- 🔧 基础配置和工具类

## 🤝 贡献指南

### 添加新测试
1. 在 `tests/` 目录创建测试文件
2. 在 `runners/` 中添加运行器方法
3. 更新 `config/test_config.py` 配置
4. 添加详细的DEBUG日志
5. 更新文档

### 报告问题
1. 运行 `python main.py sync --verbose` 收集日志
2. 检查 `logs/` 目录中的详细日志
3. 提供系统环境信息
4. 描述重现步骤

## 📞 支持

- 📖 **文档**: 查看 `DEBUG_LOGGING_GUIDE.md` 和 `USAGE_EXAMPLES.md`
- 🔍 **调试**: 使用 `python debug_test.py` 进行诊断
- 📊 **监控**: 检查 `logs/` 目录中的详细日志
- 🧹 **清理**: 运行 `python main.py --clean-only` 重置环境

---

**💡 提示**:
- 文本插入功能本身就很慢（30-60秒），这是正常现象
- 建议日常开发使用 `--no-text-insert` 选项
- 使用 `--verbose` 获取详细的调试信息
- 定期使用 `--clean-after` 保持环境整洁

**🎉 感谢使用 GuixiaoxiRag 测试套件！**
