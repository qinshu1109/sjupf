#!/bin/bash
# -*- coding: utf-8 -*-
#
# 抖音电商数据清洗工具 - 快速启动脚本
# 作者: 数据清洗工程师
# 版本: v1.0
# 功能: 自动环境检查、依赖验证、端口管理、应用启动
#

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_NAME="douyin_cleaner_env"
VENV_PATH="$SCRIPT_DIR/$VENV_NAME"
APP_FILE="app.py"
PREFERRED_PORTS=(8507 8508 8509 8510 8511)

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}🧹 抖音电商数据清洗工具${NC}"
    echo -e "${PURPLE}🚀 快速启动脚本 v1.0${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# 检查系统环境
check_system() {
    print_info "检查系统环境..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_success "操作系统: Linux (支持)"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_success "操作系统: macOS (支持)"
    else
        print_warning "操作系统: $OSTYPE (可能不完全支持)"
    fi
    
    # 检查Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python版本: $PYTHON_VERSION"
    else
        print_error "Python3 未安装，请先安装Python 3.8+"
        exit 1
    fi
    
    # 检查工作目录
    if [[ ! -f "$SCRIPT_DIR/$APP_FILE" ]]; then
        print_error "未找到 $APP_FILE 文件，请确认脚本在正确目录中运行"
        print_info "当前目录: $SCRIPT_DIR"
        exit 1
    fi
    
    print_success "系统环境检查完成"
}

# 检查并激活虚拟环境
check_and_activate_venv() {
    print_info "检查虚拟环境..."
    
    if [[ ! -d "$VENV_PATH" ]]; then
        print_error "虚拟环境 '$VENV_NAME' 不存在"
        print_info "请先创建虚拟环境："
        echo "  python3 -m venv $VENV_NAME"
        echo "  source $VENV_NAME/bin/activate"
        echo "  pip install -r requirements.txt"
        exit 1
    fi
    
    # 激活虚拟环境
    source "$VENV_PATH/bin/activate"
    print_success "虚拟环境已激活: $VENV_NAME"
    
    # 验证Python路径
    PYTHON_PATH=$(which python)
    print_info "Python路径: $PYTHON_PATH"
}

# 验证依赖包
verify_dependencies() {
    print_info "验证关键依赖包..."
    
    local required_packages=("streamlit" "pandas" "openpyxl")
    local missing_packages=()
    
    for package in "${required_packages[@]}"; do
        if python -c "import $package" 2>/dev/null; then
            local version=$(python -c "import $package; print($package.__version__)" 2>/dev/null || echo "未知版本")
            print_success "$package: $version"
        else
            missing_packages+=("$package")
            print_error "$package: 未安装"
        fi
    done
    
    if [[ ${#missing_packages[@]} -gt 0 ]]; then
        print_error "缺少依赖包: ${missing_packages[*]}"
        print_info "请安装缺少的依赖包："
        echo "  pip install ${missing_packages[*]}"
        exit 1
    fi
    
    print_success "所有依赖包验证通过"
}

# 检查端口可用性
check_port() {
    local port=$1
    if command -v netstat &> /dev/null; then
        netstat -tuln | grep ":$port " &> /dev/null
        return $?
    elif command -v ss &> /dev/null; then
        ss -tuln | grep ":$port " &> /dev/null
        return $?
    else
        # 如果没有netstat或ss，尝试连接端口
        timeout 1 bash -c "</dev/tcp/localhost/$port" &> /dev/null
        return $?
    fi
}

# 找到可用端口
find_available_port() {
    print_info "检查可用端口..."
    
    for port in "${PREFERRED_PORTS[@]}"; do
        if ! check_port $port; then
            print_success "找到可用端口: $port"
            echo $port
            return 0
        else
            print_warning "端口 $port 已被占用"
        fi
    done
    
    print_error "所有首选端口都被占用，请手动指定端口"
    exit 1
}

# 启动Streamlit应用
start_streamlit() {
    local port=$1
    print_info "启动Streamlit应用..."
    
    # 设置环境变量
    export STREAMLIT_SERVER_PORT=$port
    export STREAMLIT_SERVER_ADDRESS="localhost"
    export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
    
    print_info "启动命令: streamlit run $APP_FILE --server.port=$port"
    print_success "应用启动中..."
    print_success "访问地址: ${CYAN}http://localhost:$port${NC}"
    
    # 延迟打开浏览器
    (sleep 3 && open_browser "http://localhost:$port") &
    
    # 启动应用
    streamlit run "$APP_FILE" --server.port="$port" --server.address="localhost"
}

# 打开浏览器
open_browser() {
    local url=$1
    print_info "尝试打开浏览器..."
    
    if command -v xdg-open &> /dev/null; then
        xdg-open "$url" &> /dev/null &
    elif command -v open &> /dev/null; then
        open "$url" &> /dev/null &
    elif command -v firefox &> /dev/null; then
        firefox "$url" &> /dev/null &
    elif command -v google-chrome &> /dev/null; then
        google-chrome "$url" &> /dev/null &
    else
        print_warning "无法自动打开浏览器，请手动访问: $url"
    fi
}

# 显示使用说明
show_usage() {
    echo -e "${CYAN}使用说明:${NC}"
    echo "  ./start_app.sh              # 启动应用"
    echo "  ./start_app.sh --help       # 显示帮助"
    echo "  ./start_app.sh --check      # 仅检查环境"
    echo ""
    echo -e "${CYAN}常见问题:${NC}"
    echo "  1. 权限错误: chmod +x start_app.sh"
    echo "  2. 虚拟环境不存在: 请先创建虚拟环境"
    echo "  3. 依赖包缺失: pip install -r requirements.txt"
    echo "  4. 端口被占用: 脚本会自动寻找可用端口"
}

# 主函数
main() {
    # 处理命令行参数
    case "${1:-}" in
        --help|-h)
            print_header
            show_usage
            exit 0
            ;;
        --check)
            print_header
            check_system
            check_and_activate_venv
            verify_dependencies
            print_success "环境检查完成，一切正常！"
            exit 0
            ;;
    esac
    
    # 主流程
    print_header
    
    # 环境检查
    check_system
    check_and_activate_venv
    verify_dependencies
    
    # 端口管理
    AVAILABLE_PORT=$(find_available_port)
    
    # 启动应用
    print_info "准备启动数据清洗工具..."
    echo ""
    print_success "🎉 启动成功！请在浏览器中使用数据清洗工具"
    print_info "💡 按 Ctrl+C 停止应用"
    echo ""
    
    start_streamlit $AVAILABLE_PORT
}

# 错误处理
trap 'print_error "脚本执行被中断"; exit 1' INT TERM

# 执行主函数
main "$@"
