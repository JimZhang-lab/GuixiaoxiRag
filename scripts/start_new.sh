#!/bin/bash
# GuiXiaoXiRag 新服务器启动脚本
# 从项目根目录直接启动 server_new

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录（项目根目录）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_NEW_DIR="$PROJECT_ROOT/server_new"

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 激活 conda 环境
activate_conda() {
    log_info "检查 conda 环境..."

    # 检查是否有 conda
    if command -v conda &> /dev/null; then
        log_success "找到 conda"

        # 激活 guixiaoxi312 环境
        if conda info --envs | grep -q "guixiaoxi312"; then
            log_info "激活 guixiaoxi312 环境..."
            source "$(conda info --base)/etc/profile.d/conda.sh"
            conda activate guixiaoxi312
            log_success "已激活 guixiaoxi312 环境"
        else
            log_warning "未找到 guixiaoxi312 环境，使用默认环境"
        fi
    else
        log_info "未找到 conda，使用系统 Python"
    fi
}

# 检查 Python 版本
check_python() {
    log_info "检查 Python 环境..."

    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log_success "Python 版本: $PYTHON_VERSION"

    # 检查版本是否满足要求
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        log_success "Python 版本满足要求 (>= 3.8)"
    else
        log_error "Python 版本过低，需要 3.8+"
        exit 1
    fi
}

# 检查目录结构
check_directories() {
    log_info "检查目录结构..."
    
    if [ ! -d "$SERVER_NEW_DIR" ]; then
        log_error "server_new 目录不存在: $SERVER_NEW_DIR"
        exit 1
    fi
    log_success "server_new 目录: $SERVER_NEW_DIR"
    
    if [ ! -f "$SERVER_NEW_DIR/main.py" ]; then
        log_error "main.py 文件不存在: $SERVER_NEW_DIR/main.py"
        exit 1
    fi
    log_success "main.py 文件存在"
    
    if [ ! -f "$SERVER_NEW_DIR/requirements.txt" ]; then
        log_error "requirements.txt 文件不存在"
        exit 1
    fi
    log_success "requirements.txt 文件存在"
}

# 检查配置文件
check_config() {
    log_info "检查配置文件..."
    
    if [ -f "$PROJECT_ROOT/.env" ]; then
        log_success "找到配置文件: $PROJECT_ROOT/.env"
    elif [ -f "$PROJECT_ROOT/.env.example" ]; then
        log_warning "未找到 .env 文件，但找到了 .env.example"
        log_info "建议复制 .env.example 为 .env 并修改配置"
        
        read -p "是否现在复制配置文件? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
            log_success "已复制配置文件，请编辑 .env 文件设置您的配置"
        fi
    else
        log_warning "未找到配置文件，将使用默认配置"
    fi
}

# 检查依赖
check_dependencies() {
    log_info "检查 Python 依赖..."
    
    # 检查关键依赖
    if python3 -c "import fastapi" 2>/dev/null; then
        log_success "FastAPI 已安装"
    else
        log_warning "FastAPI 未安装，正在安装依赖..."
        install_dependencies
        return
    fi
    
    if python3 -c "import uvicorn" 2>/dev/null; then
        log_success "Uvicorn 已安装"
    else
        log_warning "Uvicorn 未安装，正在安装依赖..."
        install_dependencies
        return
    fi
    
    log_success "依赖检查完成"
}

# 安装依赖
install_dependencies() {
    log_info "安装 Python 依赖..."
    
    cd "$SERVER_NEW_DIR"
    
    if python3 -m pip install -r requirements.txt; then
        log_success "依赖安装完成"
    else
        log_error "依赖安装失败"
        exit 1
    fi
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    cd "$SERVER_NEW_DIR"
    
    mkdir -p logs
    mkdir -p knowledgeBase
    mkdir -p uploads
    
    log_success "目录创建完成"
}

# 启动服务器
start_server() {
    log_info "启动 GuiXiaoXiRag 服务器..."
    echo "=================================================="

    # 设置环境变量
    export PYTHONPATH="$PROJECT_ROOT:$SERVER_NEW_DIR"

    # 显示 API 文档地址
    echo ""
    log_info "📚 API 文档地址:"
    echo "   - Swagger UI: http://localhost:8002/docs"
    echo "   - ReDoc: http://localhost:8002/redoc"
    echo "   - OpenAPI JSON: http://localhost:8002/openapi.json"
    echo "=================================================="

    # 启动服务器
    if [ "$1" = "--dev" ]; then
        log_info "开发模式启动..."
        cd "$PROJECT_ROOT"
        python3 -m uvicorn server_new.main:app --host 0.0.0.0 --port 8002 --reload
    elif [ "$1" = "--docker" ]; then
        log_info "Docker 模式启动..."
        cd "$SERVER_NEW_DIR"
        docker-compose up -d
    else
        log_info "生产模式启动..."
        cd "$PROJECT_ROOT"
        python3 -m uvicorn server_new.main:app --host 0.0.0.0 --port 8002
    fi
}

# 显示帮助信息
show_help() {
    echo "GuiXiaoXiRag 新服务器启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --dev     开发模式启动（自动重载）"
    echo "  --docker  Docker 模式启动"
    echo "  --help    显示此帮助信息"
    echo "  --check   仅检查环境，不启动服务"
    echo ""
    echo "示例:"
    echo "  $0              # 正常启动"
    echo "  $0 --dev        # 开发模式启动"
    echo "  $0 --docker     # Docker 启动"
    echo "  $0 --check      # 仅检查环境"
}

# 主函数
main() {
    echo "🎯 GuiXiaoXiRag 新服务器启动器"
    echo "=================================================="
    
    # 解析命令行参数
    case "$1" in
        --help|-h)
            show_help
            exit 0
            ;;
        --check)
            CHECK_ONLY=true
            ;;
        --dev|--docker)
            START_MODE="$1"
            ;;
        "")
            START_MODE=""
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
    
    # 执行检查
    activate_conda
    check_python
    check_directories
    check_config
    check_dependencies
    create_directories
    
    if [ "$CHECK_ONLY" = true ]; then
        log_success "环境检查完成，一切正常！"
        exit 0
    fi
    
    # 启动服务器
    start_server "$START_MODE"
}

# 捕获 Ctrl+C
trap 'echo -e "\n👋 启动已取消"; exit 1' INT

# 运行主函数
main "$@"
