#!/bin/bash
"""
GuiXiaoXiRag FastAPI 服务快速启动脚本
"""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查Python环境
check_python() {
    if ! command -v python &> /dev/null; then
        print_error "Python未安装或不在PATH中"
        exit 1
    fi
    
    python_version=$(python --version 2>&1 | cut -d' ' -f2)
    print_success "Python版本: $python_version"
}

# 检查依赖
check_dependencies() {
    print_info "检查Python依赖..."
    
    if ! python -c "import fastapi, uvicorn, httpx" &> /dev/null; then
        print_warning "缺少必要依赖，正在安装..."
        pip install -r requirements.txt
        if [ $? -eq 0 ]; then
            print_success "依赖安装完成"
        else
            print_error "依赖安装失败"
            exit 1
        fi
    else
        print_success "依赖检查通过"
    fi
}

# 启动服务
start_service() {
    print_info "启动GuiXiaoXiRag FastAPI服务..."
    echo
    
    # 默认参数
    HOST=${HOST:-"0.0.0.0"}
    PORT=${PORT:-8002}
    WORKERS=${WORKERS:-1}
    LOG_LEVEL=${LOG_LEVEL:-"info"}
    
    # 如果传入了参数，使用传入的参数
    if [ $# -gt 0 ]; then
        python main.py "$@"
    else
        python main.py --host $HOST --port $PORT --workers $WORKERS --log-level $LOG_LEVEL
    fi
}

# 主函数
main() {
    echo "🚀 GuiXiaoXiRag FastAPI 服务启动脚本"
    echo "=================================="
    
    # 检查环境
    check_python
    check_dependencies
    
    echo
    print_info "启动配置:"
    echo "   • 主机: ${HOST:-0.0.0.0}"
    echo "   • 端口: ${PORT:-8002}"
    echo "   • 进程数: ${WORKERS:-1}"
    echo "   • 日志级别: ${LOG_LEVEL:-info}"
    echo
    
    # 启动服务
    start_service "$@"
}

# 如果直接运行此脚本
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
