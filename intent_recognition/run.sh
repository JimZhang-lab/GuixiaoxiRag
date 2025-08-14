#!/bin/bash

# 意图识别服务启动脚本

echo "🚀 启动意图识别服务..."
echo "================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未找到，请先安装Python3"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
python3 -c "import fastapi, uvicorn, pydantic" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️ 缺少依赖，正在安装..."
    pip install fastapi uvicorn pydantic
fi

# 启动服务
echo "🌟 启动服务..."
echo "   • 服务地址: http://localhost:8003"
echo "   • API文档: http://localhost:8003/docs"
echo "   • 健康检查: http://localhost:8003/health"
echo ""
echo "⚡ 按 Ctrl+C 停止服务"
echo "================================"

python3 simple_start.py
