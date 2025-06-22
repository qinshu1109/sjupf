#!/bin/bash
# -*- coding: utf-8 -*-
# 电商数据智能评分系统启动脚本
# 功能：启动基于score_select.py的Streamlit Web应用

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 工作目录
WORK_DIR="/media/qinshu/969EB28D733D99C4/图片"
VENV_NAME="douyin_cleaner_env"
VENV_PATH="$WORK_DIR/$VENV_NAME"

# 应用信息
APP_NAME="电商数据智能评分系统"
APP_FILE="scoring_app.py"
SCORE_FILE="score_select.py"

# 端口范围
START_PORT=8510
END_PORT=8515

echo -e "${CYAN}🎯 $APP_NAME 启动器${NC}"
echo -e "${CYAN}================================================${NC}"

# 检查参数
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo -e "${YELLOW}使用说明：${NC}"
    echo "  $0                    # 启动评分系统"
    echo "  $0 --check           # 检查环境状态"
    echo "  $0 --help            # 显示帮助信息"
    echo ""
    echo -e "${YELLOW}功能说明：${NC}"
    echo "  - 8大评分算法：长尾截断、佣金分段、余弦衰减等"
    echo "  - 节日模式感知：自动检测45天内节日并调整权重"
    echo "  - 多文件处理：支持CSV/XLSX批量上传"
    echo "  - TOP50筛选：智能去重和排序"
    exit 0
fi

# 环境检查函数
check_environment() {
    echo -e "${BLUE}🔍 环境检查${NC}"
    echo "----------------------------------------"
    
    # 检查工作目录
    if [[ ! -d "$WORK_DIR" ]]; then
        echo -e "${RED}❌ 工作目录不存在: $WORK_DIR${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ 工作目录: $WORK_DIR${NC}"
    
    # 检查虚拟环境
    if [[ ! -d "$VENV_PATH" ]]; then
        echo -e "${RED}❌ 虚拟环境不存在: $VENV_PATH${NC}"
        echo -e "${YELLOW}💡 请先运行数据清洗工具创建虚拟环境${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ 虚拟环境: $VENV_PATH${NC}"
    
    # 检查核心文件
    cd "$WORK_DIR"
    if [[ ! -f "$APP_FILE" ]]; then
        echo -e "${RED}❌ 应用文件不存在: $APP_FILE${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ 应用文件: $APP_FILE${NC}"
    
    if [[ ! -f "$SCORE_FILE" ]]; then
        echo -e "${RED}❌ 评分脚本不存在: $SCORE_FILE${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ 评分脚本: $SCORE_FILE${NC}"
    
    return 0
}

# 检查依赖函数
check_dependencies() {
    echo -e "${BLUE}📦 依赖检查${NC}"
    echo "----------------------------------------"
    
    # 激活虚拟环境
    source "$VENV_PATH/bin/activate"
    
    # 检查Python包
    local missing_packages=()
    
    if ! python -c "import streamlit" 2>/dev/null; then
        missing_packages+=("streamlit")
    fi
    
    if ! python -c "import pandas" 2>/dev/null; then
        missing_packages+=("pandas")
    fi
    
    if ! python -c "import numpy" 2>/dev/null; then
        missing_packages+=("numpy")
    fi
    
    if ! python -c "import openpyxl" 2>/dev/null; then
        missing_packages+=("openpyxl")
    fi
    
    if [[ ${#missing_packages[@]} -gt 0 ]]; then
        echo -e "${RED}❌ 缺少依赖包: ${missing_packages[*]}${NC}"
        echo -e "${YELLOW}💡 请先运行数据清洗工具安装依赖${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ 所有依赖包已安装${NC}"
    return 0
}

# 查找可用端口函数
find_available_port() {
    for port in $(seq $START_PORT $END_PORT); do
        if ! netstat -tuln 2>/dev/null | grep -q ":$port "; then
            echo $port
            return 0
        fi
    done
    return 1
}

# 启动应用函数
start_application() {
    echo -e "${BLUE}🚀 启动应用${NC}"
    echo "----------------------------------------"
    
    # 切换到工作目录
    cd "$WORK_DIR"
    
    # 激活虚拟环境
    source "$VENV_PATH/bin/activate"
    
    # 查找可用端口
    PORT=$(find_available_port)
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}❌ 无法找到可用端口 ($START_PORT-$END_PORT)${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ 使用端口: $PORT${NC}"
    echo -e "${YELLOW}🌐 应用地址: http://localhost:$PORT${NC}"
    echo ""
    echo -e "${PURPLE}📊 $APP_NAME 功能特性：${NC}"
    echo -e "  • 8大评分算法智能筛选"
    echo -e "  • 节日模式自动感知"
    echo -e "  • 多文件批量处理"
    echo -e "  • TOP50结果输出"
    echo ""
    echo -e "${CYAN}🎯 正在启动应用...${NC}"
    echo -e "${YELLOW}💡 按 Ctrl+C 停止应用${NC}"
    echo ""
    
    # 启动Streamlit应用
    streamlit run "$APP_FILE" --server.port=$PORT --server.headless=true --browser.gatherUsageStats=false
}

# 主执行逻辑
main() {
    # 仅检查环境
    if [[ "$1" == "--check" ]]; then
        check_environment
        if [[ $? -eq 0 ]]; then
            check_dependencies
            if [[ $? -eq 0 ]]; then
                echo -e "${GREEN}🎉 环境检查通过，可以启动应用${NC}"
            fi
        fi
        exit $?
    fi
    
    # 完整启动流程
    echo -e "${YELLOW}⏳ 正在检查环境...${NC}"
    
    # 环境检查
    check_environment
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}💥 环境检查失败${NC}"
        exit 1
    fi
    
    # 依赖检查
    check_dependencies
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}💥 依赖检查失败${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}🎉 环境检查完成，准备启动应用${NC}"
    echo ""
    
    # 启动应用
    start_application
}

# 错误处理
trap 'echo -e "\n${YELLOW}👋 应用已停止${NC}"; exit 0' INT

# 执行主函数
main "$@"
