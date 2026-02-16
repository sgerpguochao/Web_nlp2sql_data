@echo off
chcp 65001 >nul
echo =========================================
echo 停止 NL2SQL 前后端服务
echo =========================================
echo.

echo [后端] 端口 8000 ...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
    echo   已停止 PID %%a
)
echo.

echo [前端] 端口 3000 ...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":3000" ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
    echo   已停止 PID %%a
)

echo.
echo =========================================
echo 完成
echo =========================================
pause
