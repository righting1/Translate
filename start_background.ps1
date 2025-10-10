# 翻译API项目后台启动脚本 (PowerShell)
# 使用方法: .\start_background.ps1 [start|stop|status|restart]

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "stop", "status", "restart")]
    [string]$Action = "help"
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PidFile = Join-Path $ScriptDir "app.pid"
$LogFile = Join-Path $ScriptDir "app.log"
$StartScript = Join-Path $ScriptDir "start_server.ps1"

function Write-Header {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "   翻译API项目后台管理脚本 (PowerShell)" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

function Test-Python {
    try {
        $pythonVersion = python --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[信息] 检测到Python环境: $pythonVersion" -ForegroundColor Green
            return $true
        }
    } catch {
        # 尝试python3
        try {
            $pythonVersion = python3 --version 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[信息] 检测到Python环境: $pythonVersion" -ForegroundColor Green
                return $true
            }
        } catch {
            # 什么都不做
        }
    }
    Write-Host "[错误] Python未安装或不在PATH中" -ForegroundColor Red
    return $false
}

function Test-EnvFile {
    $envFile = Join-Path $ScriptDir ".env"
    $envExample = Join-Path $ScriptDir ".env.example"

    if (-not (Test-Path $envFile)) {
        if (Test-Path $envExample) {
            Write-Host "[信息] 复制环境配置模板..." -ForegroundColor Yellow
            Copy-Item $envExample $envFile
            Write-Host "[提示] 请编辑.env文件配置API密钥后重新启动" -ForegroundColor Yellow
            return $false
        } else {
            Write-Host "[错误] .env.example文件不存在" -ForegroundColor Red
            return $false
        }
    }
    return $true
}

function Get-RunningPid {
    if (Test-Path $PidFile) {
        try {
            $existingPid = Get-Content $PidFile -Raw
            $existingPid = $existingPid.Trim()

            $process = Get-Process -Id $existingPid -ErrorAction SilentlyContinue
            if ($process -and $process.ProcessName -like "*python*") {
                return $existingPid
            } else {
                Write-Host "[信息] 清理失效的PID文件..." -ForegroundColor Yellow
                Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
            }
        } catch {
            Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        }
    }
    return $null
}

function Start-App {
    Write-Host "[信息] 检查Python环境..." -ForegroundColor Blue
    if (-not (Test-Python)) {
        exit 1
    }

    Write-Host "[信息] 检查环境配置文件..." -ForegroundColor Blue
    if (-not (Test-EnvFile)) {
        exit 1
    }

    Write-Host "[信息] 检查是否已在运行..." -ForegroundColor Blue
    $runningPid = Get-RunningPid
    if ($runningPid) {
        Write-Host "[警告] 应用已在运行 (PID: $runningPid)" -ForegroundColor Yellow
        Write-Host "请先执行: .\start_background.ps1 stop" -ForegroundColor Yellow
        exit 1
    }

    Write-Host "[信息] 安装/更新依赖..." -ForegroundColor Blue
    pip install -r requirements.txt >$null 2>&1

    Write-Host "[信息] 启动FastAPI应用 (后台模式)..." -ForegroundColor Blue

    # 创建启动脚本
    $startScriptContent = @"
cd "$ScriptDir"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload >> "$LogFile" 2>&1
"@

    $startScriptContent | Out-File -FilePath $StartScript -Encoding UTF8 -Force

    # 启动后台进程
    $process = Start-Process -FilePath "powershell.exe" -ArgumentList "-ExecutionPolicy Bypass -File `"$StartScript`"" -NoNewWindow -PassThru

    Write-Host "[信息] 等待应用启动..." -ForegroundColor Blue
    Start-Sleep -Seconds 3

    # 保存PID
    $process.Id | Out-File -FilePath $PidFile -Encoding UTF8 -Force

    Write-Host "[成功] 应用已启动 (PID: $($process.Id))" -ForegroundColor Green
    Write-Host "[信息] API文档: http://127.0.0.1:8000/docs" -ForegroundColor Green
    Write-Host "[信息] 查看日志: Get-Content app.log" -ForegroundColor Green
    Write-Host "[信息] 停止应用: .\start_background.ps1 stop" -ForegroundColor Green

    # 清理临时启动脚本
    Start-Job -ScriptBlock {
        Start-Sleep -Seconds 2
        Remove-Item $using:StartScript -Force -ErrorAction SilentlyContinue
    } | Out-Null
}

function Stop-App {
    $runningPid = Get-RunningPid
    if (-not $runningPid) {
        Write-Host "[信息] 应用未在运行" -ForegroundColor Green
        return
    }

    Write-Host "[信息] 停止应用 (PID: $runningPid)..." -ForegroundColor Blue

    try {
        Stop-Process -Id $runningPid -Force -ErrorAction Stop
        Write-Host "[成功] 应用已停止" -ForegroundColor Green
    } catch {
        Write-Host "[警告] 无法终止进程 $runningPid (可能已停止)" -ForegroundColor Yellow
    }

    if (Test-Path $PidFile) {
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    }
}

function Get-Status {
    $runningPid = Get-RunningPid
    if (-not $runningPid) {
        Write-Host "[状态] 应用未运行" -ForegroundColor Red
        return
    }

    Write-Host "[状态] 应用正在运行 (PID: $runningPid)" -ForegroundColor Green
    Write-Host "[信息] API文档: http://127.0.0.1:8000/docs" -ForegroundColor Green

    # 检查端口
    try {
        $connections = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
        if ($connections) {
            Write-Host "[信息] 监听端口: 8000 (正常)" -ForegroundColor Green
        } else {
            Write-Host "[警告] 端口8000未在监听" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[信息] 无法检查端口状态" -ForegroundColor Yellow
    }
}

function Restart-App {
    Write-Host "[信息] 重启应用..." -ForegroundColor Blue
    Stop-App
    Start-Sleep -Seconds 2
    Start-App
}

function Show-Help {
    Write-Header
    Write-Host "使用方法:" -ForegroundColor White
    Write-Host "  .\start_background.ps1 start    启动应用 (后台运行)" -ForegroundColor White
    Write-Host "  .\start_background.ps1 stop     停止应用" -ForegroundColor White
    Write-Host "  .\start_background.ps1 status   查看应用状态" -ForegroundColor White
    Write-Host "  .\start_background.ps1 restart  重启应用" -ForegroundColor White
    Write-Host ""
    Write-Host "当前状态:" -ForegroundColor White
    Get-Status
}

# 主逻辑
switch ($Action) {
    "start" { Start-App }
    "stop" { Stop-App }
    "status" { Get-Status }
    "restart" { Restart-App }
    "help" { Show-Help }
    default { Show-Help }
}