#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本演示程序
展示启动脚本的功能和效果
"""

import os
import subprocess
import time
from pathlib import Path

def demo_bash_script():
    """演示Bash脚本功能"""
    print("🚀 演示 Bash 启动脚本")
    print("=" * 50)
    
    script_path = Path("start_app.sh")
    if not script_path.exists():
        print("❌ start_app.sh 不存在")
        return
    
    print("📋 可用命令:")
    print("  ./start_app.sh              # 启动应用")
    print("  ./start_app.sh --check      # 检查环境")
    print("  ./start_app.sh --help       # 显示帮助")
    print()
    
    # 演示帮助信息
    print("🔍 显示帮助信息:")
    try:
        result = subprocess.run(["./start_app.sh", "--help"], 
                              capture_output=True, text=True, timeout=10)
        print(result.stdout)
    except Exception as e:
        print(f"❌ 执行失败: {e}")

def demo_python_script():
    """演示Python脚本功能"""
    print("\n🐍 演示 Python 启动脚本")
    print("=" * 50)
    
    script_path = Path("quick_start.py")
    if not script_path.exists():
        print("❌ quick_start.py 不存在")
        return
    
    print("📋 可用命令:")
    print("  python3 quick_start.py              # 启动应用")
    print("  python3 quick_start.py --check      # 检查环境")
    print("  python3 quick_start.py --help       # 显示帮助")
    print()
    
    # 演示帮助信息
    print("🔍 显示帮助信息:")
    try:
        result = subprocess.run(["python3", "quick_start.py", "--help"], 
                              capture_output=True, text=True, timeout=10)
        print(result.stdout)
    except Exception as e:
        print(f"❌ 执行失败: {e}")

def demo_features():
    """演示脚本特性"""
    print("\n✨ 脚本特性展示")
    print("=" * 50)
    
    features = [
        "🔍 自动环境检查 - 检查Python版本、应用文件、虚拟环境",
        "📦 依赖验证 - 验证streamlit、pandas、openpyxl等关键包",
        "🌐 智能端口管理 - 自动检测8507→8508→8509可用端口",
        "🚀 一键启动 - 激活环境、启动应用、打开浏览器",
        "🎨 彩色输出 - 不同类型消息使用不同颜色显示",
        "❌ 友好错误处理 - 详细错误信息和解决建议",
        "🔧 跨平台支持 - Linux、macOS、Windows全覆盖",
        "⚡ 快速诊断 - --check参数仅检查环境不启动应用"
    ]
    
    for feature in features:
        print(f"  {feature}")
        time.sleep(0.2)

def demo_file_structure():
    """展示文件结构"""
    print("\n📁 项目文件结构")
    print("=" * 50)
    
    files = [
        ("app.py", "主应用文件", "✅"),
        ("start_app.sh", "Bash启动脚本", "✅" if Path("start_app.sh").exists() else "❌"),
        ("quick_start.py", "Python启动脚本", "✅" if Path("quick_start.py").exists() else "❌"),
        ("start_app.bat", "Windows启动脚本", "✅" if Path("start_app.bat").exists() else "❌"),
        ("启动脚本使用说明.md", "使用说明文档", "✅" if Path("启动脚本使用说明.md").exists() else "❌"),
        ("douyin_cleaner_env/", "虚拟环境目录", "✅" if Path("douyin_cleaner_env").exists() else "❌"),
        ("requirements.txt", "依赖包列表", "✅" if Path("requirements.txt").exists() else "❌"),
    ]
    
    for filename, description, status in files:
        print(f"  {status} {filename:<25} - {description}")

def demo_usage_examples():
    """展示使用示例"""
    print("\n💡 使用示例")
    print("=" * 50)
    
    examples = [
        {
            "title": "🚀 快速启动（推荐）",
            "commands": [
                "./start_app.sh",
                "# 或",
                "python3 quick_start.py"
            ]
        },
        {
            "title": "🔍 环境检查",
            "commands": [
                "./start_app.sh --check",
                "# 或", 
                "python3 quick_start.py --check"
            ]
        },
        {
            "title": "❓ 获取帮助",
            "commands": [
                "./start_app.sh --help",
                "# 或",
                "python3 quick_start.py --help"
            ]
        },
        {
            "title": "🪟 Windows用户",
            "commands": [
                "# 双击运行 start_app.bat",
                "# 或在命令提示符中：",
                "start_app.bat"
            ]
        }
    ]
    
    for example in examples:
        print(f"\n{example['title']}:")
        for cmd in example['commands']:
            print(f"  {cmd}")

def main():
    """主演示函数"""
    print("🎯 抖音电商数据清洗工具 - 快速启动脚本演示")
    print("=" * 60)
    
    # 检查当前目录
    current_dir = Path.cwd()
    print(f"📍 当前目录: {current_dir}")
    
    if not Path("app.py").exists():
        print("❌ 未在正确目录中运行，请切换到项目根目录")
        return
    
    # 演示各个功能
    demo_features()
    demo_file_structure()
    demo_usage_examples()
    demo_bash_script()
    demo_python_script()
    
    print("\n🎉 演示完成！")
    print("💡 提示：选择适合您系统的启动脚本开始使用数据清洗工具")

if __name__ == "__main__":
    main()
