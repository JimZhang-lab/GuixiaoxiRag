# API 文档

本目录包含 GuiXiaoXiRag FastAPI 服务的完整 API 文档和使用示例。

## 📋 文档目录

### 📚 API 参考
- **[API 参考文档](API_REFERENCE.md)** - 完整的 API 接口文档
- **[API 使用示例](API_EXAMPLES.md)** - 实用的调用示例和代码

### 🌐 在线文档
- **Swagger UI**: [http://localhost:8002/docs](http://localhost:8002/docs) - 交互式 API 文档
- **ReDoc**: [http://localhost:8002/redoc](http://localhost:8002/redoc) - 美观的 API 文档

## 🚀 快速开始

### 1. 启动服务
```bash
python main.py
```

### 2. 访问 API 文档
打开浏览器访问：
- 交互式文档：http://localhost:8002/docs
- 文档界面：http://localhost:8002/redoc

### 3. 基本 API 调用
```bash
# 健康检查
curl http://localhost:8002/health

# 插入文档
curl -X POST "http://localhost:8002/insert/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "这是一个测试文档"}'

# 查询知识库
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "测试", "mode": "hybrid"}'
```

## 📊 API 分类

### 🔧 系统管理
- 健康检查：`GET /health`
- 系统状态：`GET /system/status`
- 系统重置：`POST /system/reset`

### 📚 文档管理
- 插入文本：`POST /insert/text`
- 批量插入：`POST /insert/texts`
- 文件上传：`POST /insert/file`
- 批量文件：`POST /insert/files`

### 🔍 智能查询
- 基础查询：`POST /query`
- 批量查询：`POST /query/batch`
- 查询模式：`GET /query/modes`

### 🗄️ 知识库管理
- 列出知识库：`GET /knowledge-bases`
- 创建知识库：`POST /knowledge-bases`
- 切换知识库：`POST /service/switch-kb`

### 🌍 语言管理
- 支持语言：`GET /languages`
- 设置语言：`POST /languages/set`

### 📊 监控运维
- 性能指标：`GET /metrics`
- 知识图谱：`POST /knowledge-graph`
- 图谱统计：`GET /knowledge-graph/stats`

## 🔗 相关文档

- [快速开始](../getting-started/QUICK_START.md)
- [配置指南](../getting-started/CONFIGURATION_GUIDE.md)
- [功能指南](../features/README.md)
- [返回主文档](../README.md)

## 💡 使用建议

1. **开发调试**: 使用 Swagger UI 进行交互式测试
2. **集成开发**: 参考 API 示例文档中的代码
3. **生产部署**: 查看部署指南了解最佳实践
4. **问题排查**: 参考故障排除指南解决常见问题
