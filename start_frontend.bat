@echo off
chcp 65001 >nul
cd /d "%~dp0\frontend"
echo =========================================
echo 启动 NL2SQL 前端 (0.0.0.0:3000)
echo =========================================
if not exist "node_modules" (
    echo 正在安装前端依赖...
    call npm install
)
echo.
echo 前端地址: http://0.0.0.0:3000
echo 本机访问: http://localhost:3000
echo 局域网访问: http://你的IP:3000
echo =========================================
call npm run dev
pause
