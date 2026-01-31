@echo off
:: 设置项目根目录，确保模块导入正确
set PYTHONPATH=%~dp0

:: 1. 读取 config.ini 配置文件
set "CONFIG_FILE=%~dp0config.ini"
set "PYTHON_EXE="

if exist "%CONFIG_FILE%" (
    :: 解析 ini 文件，跳过 ; 开头的注释行
    for /f "usebackq eol=; tokens=1,* delims==" %%A in ("%CONFIG_FILE%") do (
        if /i "%%A"=="python_path" set "PYTHON_EXE=%%B"
    )
)

echo 🚀 Alicia 正在为你启动全能重命名工具...

:: 2. 逻辑判断与启动
if not defined PYTHON_EXE (
    echo [提示] 未在 config.ini 找到 python_path，将尝试使用系统默认 Python...
    python "%~dp0main.py"
) else (
    :: 如果配置为 "python"，直接运行
    if /i "%PYTHON_EXE%"=="python" (
        python "%~dp0main.py"
    ) else (
        :: 如果是路径，检查文件是否存在
        if exist "%PYTHON_EXE%" (
            "%PYTHON_EXE%" "%~dp0main.py"
        ) else (
            echo [警告] 找不到配置的路径: "%PYTHON_EXE%"
            echo 正在回退使用系统默认 Python...
            python "%~dp0main.py"
        )
    )
)

pause