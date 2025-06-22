#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音电商数据清洗工具 - Python快速启动脚本
作者: 数据清洗工程师
版本: v1.0
功能: 自动环境检查、依赖验证、端口管理、应用启动
"""

import os
import sys
import subprocess
import socket
import time
import webbrowser
import platform
from pathlib import Path
from typing import List, Optional

# 颜色定义
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class DataCleanerLauncher:
    """数据清洗工具启动器"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.venv_name = "douyin_cleaner_env"
        self.venv_path = self.script_dir / self.venv_name
        self.app_file = "app.py"
        self.preferred_ports = [8507, 8508, 8509, 8510, 8511]
        self.required_packages = ["streamlit", "pandas", "openpyxl"]
    
    def print_colored(self, message: str, color: str = Colors.NC, prefix: str = ""):
        """打印带颜色的消息"""
        print(f"{color}{prefix}{Colors.NC} {message}")
    
    def print_info(self, message: str):
        self.print_colored(message, Colors.BLUE, "[INFO]")
    
    def print_success(self, message: str):
        self.print_colored(message, Colors.GREEN, "[SUCCESS]")
    
    def print_warning(self, message: str):
        self.print_colored(message, Colors.YELLOW, "[WARNING]")
    
    def print_error(self, message: str):
        self.print_colored(message, Colors.RED, "[ERROR]")
    
    def print_header(self):
        """打印启动头部信息"""
        print(f"{Colors.PURPLE}================================{Colors.NC}")
        print(f"{Colors.PURPLE}🧹 抖音电商数据清洗工具{Colors.NC}")
        print(f"{Colors.PURPLE}🚀 Python快速启动脚本 v1.0{Colors.NC}")
        print(f"{Colors.PURPLE}================================{Colors.NC}")
    
    def check_system(self) -> bool:
        """检查系统环境"""
        self.print_info("检查系统环境...")
        
        # 检查操作系统
        system = platform.system()
        if system in ["Linux", "Darwin"]:
            self.print_success(f"操作系统: {system} (支持)")
        else:
            self.print_warning(f"操作系统: {system} (可能不完全支持)")
        
        # 检查Python版本
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        if sys.version_info >= (3, 8):
            self.print_success(f"Python版本: {python_version}")
        else:
            self.print_error(f"Python版本过低: {python_version}，需要Python 3.8+")
            return False
        
        # 检查应用文件
        app_path = self.script_dir / self.app_file
        if not app_path.exists():
            self.print_error(f"未找到 {self.app_file} 文件")
            self.print_info(f"当前目录: {self.script_dir}")
            return False
        
        self.print_success("系统环境检查完成")
        return True
    
    def check_venv(self) -> bool:
        """检查虚拟环境"""
        self.print_info("检查虚拟环境...")
        
        if not self.venv_path.exists():
            self.print_error(f"虚拟环境 '{self.venv_name}' 不存在")
            self.print_info("请先创建虚拟环境：")
            print(f"  python3 -m venv {self.venv_name}")
            print(f"  source {self.venv_name}/bin/activate  # Linux/Mac")
            print(f"  {self.venv_name}\\Scripts\\activate     # Windows")
            print(f"  pip install -r requirements.txt")
            return False
        
        self.print_success(f"虚拟环境存在: {self.venv_name}")
        return True
    
    def get_venv_python(self) -> Optional[str]:
        """获取虚拟环境的Python路径"""
        if platform.system() == "Windows":
            python_path = self.venv_path / "Scripts" / "python.exe"
        else:
            python_path = self.venv_path / "bin" / "python"
        
        if python_path.exists():
            self.print_success(f"Python路径: {python_path}")
            return str(python_path)
        else:
            self.print_error("虚拟环境Python不存在")
            return None
    
    def verify_dependencies(self, python_path: str) -> bool:
        """验证依赖包"""
        self.print_info("验证关键依赖包...")
        
        missing_packages = []
        
        for package in self.required_packages:
            try:
                result = subprocess.run(
                    [python_path, "-c", f"import {package}; print({package}.__version__)"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    version = result.stdout.strip()
                    self.print_success(f"{package}: {version}")
                else:
                    missing_packages.append(package)
                    self.print_error(f"{package}: 未安装")
            except Exception as e:
                missing_packages.append(package)
                self.print_error(f"{package}: 检查失败 - {e}")
        
        if missing_packages:
            self.print_error(f"缺少依赖包: {', '.join(missing_packages)}")
            self.print_info("请安装缺少的依赖包：")
            print(f"  {python_path} -m pip install {' '.join(missing_packages)}")
            return False
        
        self.print_success("所有依赖包验证通过")
        return True
    
    def check_port(self, port: int) -> bool:
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result != 0  # 0表示连接成功（端口被占用）
        except Exception:
            return True  # 异常时假设端口可用
    
    def find_available_port(self) -> Optional[int]:
        """找到可用端口"""
        self.print_info("检查可用端口...")
        
        for port in self.preferred_ports:
            if self.check_port(port):
                self.print_success(f"找到可用端口: {port}")
                return port
            else:
                self.print_warning(f"端口 {port} 已被占用")
        
        self.print_error("所有首选端口都被占用")
        return None
    
    def open_browser(self, url: str):
        """打开浏览器"""
        self.print_info("尝试打开浏览器...")
        try:
            webbrowser.open(url)
            self.print_success("浏览器已打开")
        except Exception as e:
            self.print_warning(f"无法自动打开浏览器: {e}")
            self.print_info(f"请手动访问: {url}")
    
    def start_streamlit(self, python_path: str, port: int):
        """启动Streamlit应用"""
        self.print_info("启动Streamlit应用...")
        
        # 设置环境变量
        env = os.environ.copy()
        env.update({
            'STREAMLIT_SERVER_PORT': str(port),
            'STREAMLIT_SERVER_ADDRESS': 'localhost',
            'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false'
        })
        
        url = f"http://localhost:{port}"
        self.print_success(f"应用启动中...")
        self.print_success(f"访问地址: {Colors.CYAN}{url}{Colors.NC}")
        
        # 延迟打开浏览器
        import threading
        timer = threading.Timer(3.0, self.open_browser, args=[url])
        timer.start()
        
        # 启动命令
        cmd = [python_path, "-m", "streamlit", "run", self.app_file, 
               "--server.port", str(port), "--server.address", "localhost"]
        
        try:
            subprocess.run(cmd, cwd=self.script_dir, env=env)
        except KeyboardInterrupt:
            self.print_info("应用已停止")
        except Exception as e:
            self.print_error(f"启动失败: {e}")
    
    def show_usage(self):
        """显示使用说明"""
        print(f"{Colors.CYAN}使用说明:{Colors.NC}")
        print("  python quick_start.py              # 启动应用")
        print("  python quick_start.py --help       # 显示帮助")
        print("  python quick_start.py --check      # 仅检查环境")
        print("")
        print(f"{Colors.CYAN}常见问题:{Colors.NC}")
        print("  1. 虚拟环境不存在: 请先创建虚拟环境")
        print("  2. 依赖包缺失: pip install -r requirements.txt")
        print("  3. 端口被占用: 脚本会自动寻找可用端口")
        print("  4. 权限问题: 确保有执行权限")
    
    def run(self, args: List[str]):
        """主运行函数"""
        # 处理命令行参数
        if "--help" in args or "-h" in args:
            self.print_header()
            self.show_usage()
            return
        
        check_only = "--check" in args
        
        self.print_header()
        
        # 环境检查
        if not self.check_system():
            sys.exit(1)
        
        if not self.check_venv():
            sys.exit(1)
        
        python_path = self.get_venv_python()
        if not python_path:
            sys.exit(1)
        
        if not self.verify_dependencies(python_path):
            sys.exit(1)
        
        if check_only:
            self.print_success("环境检查完成，一切正常！")
            return
        
        # 端口管理
        port = self.find_available_port()
        if not port:
            sys.exit(1)
        
        # 启动应用
        self.print_info("准备启动数据清洗工具...")
        print()
        self.print_success("🎉 启动成功！请在浏览器中使用数据清洗工具")
        self.print_info("💡 按 Ctrl+C 停止应用")
        print()
        
        self.start_streamlit(python_path, port)

def main():
    """主函数"""
    launcher = DataCleanerLauncher()
    try:
        launcher.run(sys.argv[1:])
    except KeyboardInterrupt:
        launcher.print_info("脚本执行被中断")
        sys.exit(1)
    except Exception as e:
        launcher.print_error(f"执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
