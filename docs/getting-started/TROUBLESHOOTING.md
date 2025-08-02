# GuiXiaoXiRag FastAPI 故障排除指南

## 🚨 常见问题与解决方案

### 🔧 服务启动问题

#### Q1: 服务启动失败，提示端口被占用
**错误信息**: `Error: [Errno 98] Address already in use`

**解决方案**:
```bash
# 查看端口占用情况
lsof -i :8002
netstat -tulpn | grep 8002

# 杀死占用端口的进程
kill -9 <PID>

# 或使用不同端口启动
python main.py --port 8003
```

#### Q2: 导入模块失败
**错误信息**: `ModuleNotFoundError: No module named 'guixiaoxiRag'`

**解决方案**:
```bash
# 检查Python环境
which python
python --version

# 激活正确的环境
conda activate guixiaoxirag

# 重新安装依赖
pip install -r requirements.txt

# 检查模块路径
python -c "import sys; print(sys.path)"
```

#### Q3: 大模型服务连接失败
**错误信息**: `Connection refused` 或 `Service unavailable`

**解决方案**:
```bash
# 检查大模型服务状态
curl http://localhost:8100/v1/models
curl http://localhost:8200/v1/models

# 检查配置文件
cat .env | grep OPENAI

# 测试网络连接
telnet localhost 8100
telnet localhost 8200
```

### 📁 文件处理问题

#### Q4: 文件上传失败
**错误信息**: `File size exceeds limit` 或 `Unsupported file format`

**解决方案**:
```bash
# 检查文件大小（默认限制50MB）
ls -lh your_file.pdf

# 检查支持的文件格式
# 支持: .txt, .md, .pdf, .docx, .doc, .json, .xml, .csv

# 修改文件大小限制（在.env中）
MAX_FILE_SIZE=104857600  # 100MB
```

#### Q5: PDF文件内容提取失败
**错误信息**: `Failed to extract text from PDF`

**解决方案**:
```bash
# 安装额外的PDF处理依赖
pip install PyPDF2 pdfplumber

# 检查PDF文件是否损坏
python -c "
import PyPDF2
with open('your_file.pdf', 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    print(f'Pages: {len(reader.pages)}')
"
```

### 🔍 查询问题

#### Q6: 查询返回空结果
**可能原因**: 
- 知识库为空
- 查询内容与文档不匹配
- 向量化未完成

**解决方案**:
```bash
# 检查知识库状态
curl http://localhost:8002/knowledge-graph/stats

# 检查是否有文档
curl http://localhost:8002/knowledge-bases

# 重新插入测试文档
curl -X POST "http://localhost:8002/insert/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "测试文档内容"}'

# 等待处理完成后再查询
sleep 10
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "测试", "mode": "hybrid"}'
```

#### Q7: 查询响应时间过长
**解决方案**:
```bash
# 使用更快的查询模式
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "your_question", "mode": "naive", "top_k": 5}'

# 检查系统资源
top
free -h
df -h

# 优化查询参数
curl -X POST "http://localhost:8002/query/optimized" \
  -H "Content-Type: application/json" \
  -d '{"query": "your_question", "performance_level": "fast"}'
```

### 💾 存储问题

#### Q8: 磁盘空间不足
**错误信息**: `No space left on device`

**解决方案**:
```bash
# 检查磁盘使用情况
df -h

# 清理日志文件
find ./logs -name "*.log" -mtime +7 -delete

# 清理临时文件
rm -rf /tmp/guixiaoxirag_*

# 压缩旧的知识库
tar -czf backup_$(date +%Y%m%d).tar.gz knowledgeBase/
```

#### Q9: 知识库损坏
**错误信息**: `Database corruption detected`

**解决方案**:
```bash
# 备份当前知识库
cp -r knowledgeBase/current knowledgeBase/backup_$(date +%Y%m%d)

# 重置知识库
curl -X POST "http://localhost:8002/system/reset"

# 从备份恢复
curl -X POST "http://localhost:8002/knowledge-bases" \
  -H "Content-Type: application/json" \
  -d '{"name": "restored", "description": "从备份恢复"}'
```

### 🔧 性能问题

#### Q10: 内存使用过高
**解决方案**:
```bash
# 监控内存使用
watch -n 1 'free -h && ps aux | grep python | head -5'

# 减少embedding维度（在.env中）
EMBEDDING_DIM=768  # 从1536降低到768

# 限制并发处理
python main.py --workers 1

# 启用内存优化模式
curl -X POST "http://localhost:8002/performance/optimize" \
  -H "Content-Type: application/json" \
  -d '{"mode": "basic"}'
```

#### Q11: CPU使用率过高
**解决方案**:
```bash
# 检查CPU使用情况
htop

# 使用更少的worker进程
python main.py --workers 1

# 启用查询缓存
# 在.env中添加
ENABLE_CACHE=true
CACHE_TTL=3600
```

### 🌐 网络问题

#### Q12: API请求超时
**解决方案**:
```bash
# 增加超时时间
curl -X POST "http://localhost:8002/query" \
  --max-time 300 \
  -H "Content-Type: application/json" \
  -d '{"query": "your_question"}'

# 检查网络延迟
ping localhost
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8002/health"

# 使用本地模式减少网络调用
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "your_question", "mode": "local"}'
```

## 🔍 诊断工具

### 系统状态检查
```bash
# 完整的系统状态
curl http://localhost:8002/system/status

# 性能指标
curl http://localhost:8002/metrics

# 健康检查
curl http://localhost:8002/health

# 查看日志
curl "http://localhost:8002/logs?lines=50"
```

### 日志分析
```bash
# 查看错误日志
tail -f logs/guixiaoxirag_service.log | grep ERROR

# 查看访问日志
tail -f logs/access.log

# 分析慢查询
grep "slow" logs/guixiaoxirag_service.log
```

### 性能测试
```bash
# 简单性能测试
time curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'

# 并发测试（需要安装ab）
ab -n 100 -c 10 http://localhost:8002/health
```

## 📞 获取帮助

### 日志收集
在报告问题时，请提供以下信息：

```bash
# 系统信息
uname -a
python --version
pip list | grep -E "(fastapi|uvicorn|guixiaoxiRag)"

# 服务状态
curl http://localhost:8002/system/status

# 错误日志
tail -100 logs/guixiaoxirag_service.log
```

### 问题报告模板
```
**环境信息**:
- 操作系统: 
- Python版本: 
- 服务版本: 

**问题描述**:
- 具体错误信息: 
- 复现步骤: 
- 期望结果: 

**日志信息**:
```

### 联系方式
- 提交Issue到项目仓库
- 查看项目文档: `/docs`
- 查看API文档: `http://localhost:8002/docs`

## 🔗 相关文档

- [快速开始指南](QUICK_START.md)
- [配置指南](CONFIGURATION_GUIDE.md)
- [部署指南](DEPLOYMENT_GUIDE.md)
- [API文档](../api/README.md)
