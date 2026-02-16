# NL2SQL 系统集成验证脚本 (Windows PowerShell)
$ErrorActionPreference = "SilentlyContinue"
$API_URL = "http://localhost:8000"
$FRONTEND_URL = "http://localhost:3000"
$passed = 0
$failed = 0

function Test-Step {
    param($Name, $ScriptBlock)
    Write-Host "`n[测试] $Name" -ForegroundColor Cyan
    try {
        $result = & $ScriptBlock
        if ($result) { Write-Host "  通过" -ForegroundColor Green; $script:passed++; return $true }
    } catch {}
    Write-Host "  失败" -ForegroundColor Red; $script:failed++; return $false
}

Write-Host "=========================================" -ForegroundColor Yellow
Write-Host "NL2SQL 系统集成验证" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Yellow

# 1. 后端服务
Write-Host "`n--- 后端服务 ---" -ForegroundColor Magenta
Test-Step "健康检查" { (Invoke-RestMethod "$API_URL/health").status -eq "ok" } | Out-Null
Test-Step "状态API" { $null -ne (Invoke-RestMethod "$API_URL/api/status").status } | Out-Null
Test-Step "API文档" { (Invoke-WebRequest "$API_URL/docs" -UseBasicParsing).StatusCode -eq 200 } | Out-Null

# 2. 前端服务
Write-Host "`n--- 前端服务 ---" -ForegroundColor Magenta
Test-Step "前端响应" { (Invoke-WebRequest $FRONTEND_URL -UseBasicParsing -TimeoutSec 5).StatusCode -eq 200 } | Out-Null

# 3. Python 依赖
Write-Host "`n--- Python 依赖 ---" -ForegroundColor Magenta
Test-Step "FastAPI" { python -c "import fastapi" 2>$null } | Out-Null
Test-Step "Uvicorn" { python -c "import uvicorn" 2>$null } | Out-Null
Test-Step "PyMySQL" { python -c "import pymysql" 2>$null } | Out-Null
Test-Step "OpenAI" { python -c "import openai" 2>$null } | Out-Null
Test-Step "sqlglot" { python -c "import sqlglot" 2>$null } | Out-Null

# 4. 数据库连接 API
Write-Host "`n--- API 功能 ---" -ForegroundColor Magenta
$dbBody = '{"type":"mysql","host":"127.0.0.1","port":3306,"user":"root","password":"test","database":"test"}'
Test-Step "数据库连接API" {
    $r = Invoke-RestMethod -Uri "$API_URL/api/test-db-connection" -Method POST -Body $dbBody -ContentType "application/json"
    $null -ne $r.success
} | Out-Null

Write-Host "`n=========================================" -ForegroundColor Yellow
$color = if ($failed -eq 0) { "Green" } else { "Red" }
Write-Host "Passed: $passed | Failed: $failed" -ForegroundColor $color
Write-Host "=========================================" -ForegroundColor Yellow
if ($failed -eq 0) {
    Write-Host "`nAll checks passed. System ready." -ForegroundColor Green
    exit 0
}
else {
    Write-Host "`n$failed check(s) failed. Ensure backend/frontend are running." -ForegroundColor Red
    exit 1
}
