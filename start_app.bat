@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 抖音电商数据清洗工具 - Windows快速启动脚本
REM 作者: 数据清洗工程师
REM 版本: v1.0

echo ================================
echo 🧹 抖音电商数据清洗工具
echo 🚀 Windows快速启动脚本 v1.0
echo ================================
echo.

REM 配置变量
set "VENV_NAME=douyin_cleaner_env"
set "APP_FILE=app.py"
set "PREFERRED_PORTS=8507 8508 8509 8510 8511"

REM 检查Python
echo [INFO] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python未安装或不在PATH中
    echo 请安装Python 3.8+并添加到PATH
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python版本: %PYTHON_VERSION%

REM 检查应用文件
if not exist "%APP_FILE%" (
    echo [ERROR] 未找到 %APP_FILE% 文件
    echo 当前目录: %CD%
    pause
    exit /b 1
)

REM 检查虚拟环境
echo [INFO] 检查虚拟环境...
if not exist "%VENV_NAME%" (
    echo [ERROR] 虚拟环境 '%VENV_NAME%' 不存在
    echo 请先创建虚拟环境：
    echo   python -m venv %VENV_NAME%
    echo   %VENV_NAME%\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

echo [SUCCESS] 虚拟环境存在: %VENV_NAME%

REM 激活虚拟环境
echo [INFO] 激活虚拟环境...
call "%VENV_NAME%\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] 虚拟环境激活失败
    pause
    exit /b 1
)

echo [SUCCESS] 虚拟环境已激活

REM 验证依赖包
echo [INFO] 验证关键依赖包...
set "MISSING_PACKAGES="

python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    set "MISSING_PACKAGES=!MISSING_PACKAGES! streamlit"
    echo [ERROR] streamlit: 未安装
) else (
    for /f %%i in ('python -c "import streamlit; print(streamlit.__version__)"') do echo [SUCCESS] streamlit: %%i
)

python -c "import pandas" >nul 2>&1
if errorlevel 1 (
    set "MISSING_PACKAGES=!MISSING_PACKAGES! pandas"
    echo [ERROR] pandas: 未安装
) else (
    for /f %%i in ('python -c "import pandas; print(pandas.__version__)"') do echo [SUCCESS] pandas: %%i
)

python -c "import openpyxl" >nul 2>&1
if errorlevel 1 (
    set "MISSING_PACKAGES=!MISSING_PACKAGES! openpyxl"
    echo [ERROR] openpyxl: 未安装
) else (
    for /f %%i in ('python -c "import openpyxl; print(openpyxl.__version__)"') do echo [SUCCESS] openpyxl: %%i
)

if not "!MISSING_PACKAGES!"=="" (
    echo [ERROR] 缺少依赖包:!MISSING_PACKAGES!
    echo 请安装缺少的依赖包：
    echo   pip install!MISSING_PACKAGES!
    pause
    exit /b 1
)

echo [SUCCESS] 所有依赖包验证通过

REM 查找可用端口
echo [INFO] 检查可用端口...
set "AVAILABLE_PORT="

for %%p in (%PREFERRED_PORTS%) do (
    netstat -an | find "127.0.0.1:%%p" >nul 2>&1
    if errorlevel 1 (
        set "AVAILABLE_PORT=%%p"
        echo [SUCCESS] 找到可用端口: %%p
        goto :found_port
    ) else (
        echo [WARNING] 端口 %%p 已被占用
    )
)

:found_port
if "%AVAILABLE_PORT%"=="" (
    echo [ERROR] 所有首选端口都被占用
    pause
    exit /b 1
)

REM 启动应用
echo [INFO] 准备启动数据清洗工具...
echo.
echo [SUCCESS] 🎉 启动成功！请在浏览器中使用数据清洗工具
echo [INFO] 💡 按 Ctrl+C 停止应用
echo [SUCCESS] 访问地址: http://localhost:%AVAILABLE_PORT%
echo.

REM 延迟打开浏览器
start "" timeout /t 3 /nobreak >nul 2>&1 && start "" "http://localhost:%AVAILABLE_PORT%"

REM 启动Streamlit
streamlit run "%APP_FILE%" --server.port=%AVAILABLE_PORT% --server.address=localhost

pause
