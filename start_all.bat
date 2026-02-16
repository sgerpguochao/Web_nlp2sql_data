@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo =========================================
echo NL2SQL 数据生成系统 - 启动前后端
echo =========================================
echo.
echo 将打开两个窗口：后端(8000)、前端(3000)
echo 成功后可访问: http://localhost:3000
echo 局域网访问: http://你的IP:3000
echo.

start "NL2SQL 后端" cmd /k "cd /d %~dp0\backend && (call conda activate web_sql 2>nul) && set HOST=0.0.0.0 && set PORT=8000 && python app.py"
timeout /t 3 >nul
start "NL2SQL 前端" cmd /k "cd /d %~dp0\frontend && npm run dev"
echo.
echo 已启动！请等待几秒后访问 http://localhost:3000
echo.
pause
