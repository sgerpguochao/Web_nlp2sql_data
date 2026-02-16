@echo off
chcp 65001 >nul
cd /d "%~dp0\backend"
echo =========================================
echo 启动 NL2SQL 后端 API 服务器 (0.0.0.0:8000)
echo =========================================

set CONDA_ENV_NAME=web_sql
set HOST=0.0.0.0
set PORT=8000

where conda >nul 2>&1
if %errorlevel% equ 0 (
    echo 检测到 Conda，激活环境: %CONDA_ENV_NAME%
    call conda activate %CONDA_ENV_NAME%
    if errorlevel 1 (
        echo [警告] 环境 %CONDA_ENV_NAME% 不存在，使用默认 Python
        echo 创建: conda create -n %CONDA_ENV_NAME% python=3.10
    )
) else (
    echo 使用系统 Python
)

echo.
echo 成功启动时将显示:
echo   API: http://0.0.0.0:8000/api
echo   文档: http://0.0.0.0:8000/docs
echo 本机: http://localhost:8000
echo 局域网: http://你的IP:8000
echo =========================================
python app.py
pause
