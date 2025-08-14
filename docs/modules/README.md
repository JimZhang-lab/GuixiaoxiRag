# 模块文档

本目录包含 GuiXiaoXiRag 各个独立模块的详细文档。

## 📁 模块列表

### 🧠 [意图识别服务](INTENT_RECOGNITION.md)
- **位置**: `intent_recognition/`
- **功能**: 查询意图识别、安全检查、查询增强
- **类型**: 独立微服务
- **端口**: 8003
- **状态**: ✅ 可用

**快速启动**:
```bash
cd intent_recognition
python3 simple_start.py
```

**API端点**:
- `/health` - 健康检查
- `/info` - 服务信息  
- `/analyze` - 意图分析

## 🔗 相关文档

- [项目架构](../project/PROJECT_ARCHITECTURE.md)
- [API参考](../api/API_REFERENCE.md)
- [快速开始](../getting-started/QUICK_START.md)

## 📝 模块开发指南

### 创建新模块
1. 在项目根目录创建模块文件夹
2. 实现模块核心功能
3. 添加API接口（如需要）
4. 编写模块文档
5. 更新本README

### 文档规范
- 模块文档命名: `MODULE_NAME.md`
- 包含功能说明、API接口、使用示例
- 提供快速启动指南
- 说明依赖关系和配置要求
