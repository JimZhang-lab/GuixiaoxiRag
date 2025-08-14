# 配置示例

本文档提供了各种配置场景的示例，帮助用户快速配置GuiXiaoXiRag服务。

## 🚀 基础配置

### 最小配置
如果您只想快速启动服务，只需要配置以下必要参数：

```env
# .env 文件
OPENAI_API_BASE=http://localhost:8100/v1
OPENAI_EMBEDDING_API_BASE=http://localhost:8200/v1
OPENAI_CHAT_API_KEY=your_llm_api_key_here
OPENAI_EMBEDDING_API_KEY=your_embedding_api_key_here
```

其他参数将使用默认值：
- `OPENAI_CHAT_MODEL=qwen14b`
- `OPENAI_EMBEDDING_MODEL=embedding_qwen`
- `PORT=8002`
- `HOST=0.0.0.0`

### 完整配置
如果您需要自定义所有参数：

```env
# 应用配置
APP_NAME=My RAG Service
APP_VERSION=1.0.0

# 服务配置
HOST=0.0.0.0
PORT=8002
DEBUG=false
WORKERS=1

# LLM配置
OPENAI_API_BASE=http://localhost:8100/v1
OPENAI_CHAT_API_KEY=your_llm_api_key_here
OPENAI_CHAT_MODEL=qwen14b

# Embedding配置
OPENAI_EMBEDDING_API_BASE=http://localhost:8200/v1
OPENAI_EMBEDDING_API_KEY=your_embedding_api_key_here
OPENAI_EMBEDDING_MODEL=embedding_qwen

# 知识库配置
WORKING_DIR=./knowledgeBase/default
EMBEDDING_DIM=1536
MAX_TOKEN_SIZE=8192

# 日志配置
LOG_LEVEL=INFO
LOG_DIR=./logs

# Streamlit配置
STREAMLIT_HOST=0.0.0.0
STREAMLIT_PORT=8501
STREAMLIT_API_URL=http://localhost:8002
```

## 🌐 多提供商配置

### OpenAI官方API
```env
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_EMBEDDING_API_BASE=https://api.openai.com/v1
OPENAI_CHAT_API_KEY=sk-your-openai-key
OPENAI_EMBEDDING_API_KEY=sk-your-openai-key
OPENAI_CHAT_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
CUSTOM_LLM_PROVIDER=openai
CUSTOM_EMBEDDING_PROVIDER=openai
```

### Azure OpenAI
```env
OPENAI_API_BASE=https://your-resource.openai.azure.com/
OPENAI_EMBEDDING_API_BASE=https://your-resource.openai.azure.com/
OPENAI_CHAT_API_KEY=your-azure-api-key
OPENAI_EMBEDDING_API_KEY=your-azure-api-key
OPENAI_CHAT_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
CUSTOM_LLM_PROVIDER=azure
CUSTOM_EMBEDDING_PROVIDER=azure
AZURE_API_VERSION=2023-12-01-preview
AZURE_DEPLOYMENT_NAME=your-deployment-name
```

### 本地Ollama
```env
OPENAI_API_BASE=http://localhost:11434/v1
OPENAI_EMBEDDING_API_BASE=http://localhost:11434/v1
OPENAI_CHAT_API_KEY=ollama
OPENAI_EMBEDDING_API_KEY=ollama
OPENAI_CHAT_MODEL=qwen2:7b
OPENAI_EMBEDDING_MODEL=nomic-embed-text
CUSTOM_LLM_PROVIDER=ollama
CUSTOM_EMBEDDING_PROVIDER=ollama
```

### 混合配置（不同提供商）
```env
# LLM使用OpenAI
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_CHAT_API_KEY=sk-your-openai-key
OPENAI_CHAT_MODEL=gpt-4
CUSTOM_LLM_PROVIDER=openai

# Embedding使用本地服务
OPENAI_EMBEDDING_API_BASE=http://localhost:8200/v1
OPENAI_EMBEDDING_API_KEY=local_key
OPENAI_EMBEDDING_MODEL=embedding_qwen
CUSTOM_EMBEDDING_PROVIDER=local
```

## 🔧 配置验证

### 通过API验证配置
```bash
# 启动服务后验证配置
curl http://localhost:8002/service/effective-config
```

### 通过CLI验证配置
```bash
# 查看有效配置
python scripts/guixiaoxirag_cli.py service effective-config

# 查看基础配置
python scripts/guixiaoxirag_cli.py service config
```

### 配置诊断
```python
import requests

def diagnose_config():
    """诊断配置问题"""
    try:
        response = requests.get("http://localhost:8002/service/effective-config")
        if response.status_code == 200:
            config = response.json()["data"]
            
            # 检查LLM配置
            if config["llm"]["api_key"] == "未配置":
                print("⚠️ LLM API密钥未配置")
            
            # 检查Embedding配置
            if config["embedding"]["api_key"] == "未配置":
                print("⚠️ Embedding API密钥未配置")
            
            # 检查端口冲突
            if config["port"] == config.get("streamlit_port"):
                print("⚠️ API端口与Streamlit端口冲突")
            
            print("✅ 配置诊断完成")
        else:
            print(f"❌ 无法获取配置: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 配置诊断失败: {e}")

# 运行诊断
diagnose_config()
```

## 🎯 常见配置场景

### 开发环境
```env
DEBUG=true
LOG_LEVEL=DEBUG
WORKERS=1
OPENAI_API_BASE=http://localhost:8100/v1
OPENAI_EMBEDDING_API_BASE=http://localhost:8200/v1
```

### 生产环境
```env
DEBUG=false
LOG_LEVEL=INFO
WORKERS=4
HOST=0.0.0.0
PORT=8002
# 使用真实的API密钥
OPENAI_CHAT_API_KEY=your_production_key
OPENAI_EMBEDDING_API_KEY=your_production_embedding_key
```

### 测试环境
```env
DEBUG=false
LOG_LEVEL=WARNING
WORKERS=1
WORKING_DIR=./test_kb
# 使用测试API密钥
OPENAI_CHAT_API_KEY=test_key
OPENAI_EMBEDDING_API_KEY=test_embedding_key
```

## 📝 配置最佳实践

1. **安全性**：
   - 不要在代码中硬编码API密钥
   - 使用环境变量或配置文件
   - 在生产环境中使用强密钥

2. **性能优化**：
   - 根据硬件资源调整`WORKERS`数量
   - 合理设置`EMBEDDING_DIM`和`MAX_TOKEN_SIZE`
   - 使用本地模型减少网络延迟

3. **监控和日志**：
   - 在生产环境中设置适当的日志级别
   - 定期检查配置有效性
   - 监控API调用频率和成本

4. **备份和恢复**：
   - 备份重要的配置文件
   - 使用版本控制管理配置变更
   - 测试配置恢复流程
