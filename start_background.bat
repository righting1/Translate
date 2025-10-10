@echo off
REM 翻译API项目后台启动脚本 (Windows CMD)
REM 用法: start_background.bat [start|stop|status|restart]

setlocal ENABLEDELAYEDEXPANSION

set ACTION=%1
if "%ACTION%"=="" set ACTION=help

set SCRIPT_DIR=%~dp0
set PID_FILE=%SCRIPT_DIR%app.pid
set LOG_FILE=%SCRIPT_DIR%app.log

REM 检查 Python 是否可用
call :check_python || goto :eof

REM 分发
if /I "%ACTION%"=="start" goto :start
if /I "%ACTION%"=="stop" goto :stop
if /I "%ACTION%"=="status" goto :status
if /I "%ACTION%"=="restart" goto :restart
goto :help

:check_env
  if exist "%SCRIPT_DIR%.env" goto :env_ok
  if exist "%SCRIPT_DIR%.env.example" (
    echo [信息] 复制环境配置模板 .env.example 到 .env
    copy /Y "%SCRIPT_DIR%.env.example" "%SCRIPT_DIR%.env" >nul
    echo [提示] 请编辑 .env 文件配置 API 密钥后重新启动
    exit /b 1
  ) else (
    echo [错误] 缺少 .env 和 .env.example 文件
    exit /b 1
  )
:env_ok
  exit /b 0

:check_python
  where python >nul 2>&1
  if !ERRORLEVEL! EQU 0 (
    set PY=python
    exit /b 0
  )
  where python3 >nul 2>&1
  if !ERRORLEVEL! EQU 0 (
    set PY=python3
    exit /b 0
  )
  echo [错误] 未找到 Python，请安装并加入 PATH
  exit /b 1

:running_pid
  if not exist "%PID_FILE%" (
    exit /b 1
  )
  set "PID="
  set /p PID=<"%PID_FILE%"
  REM 去除可能的空格
  for /f "tokens=*" %%A in ("%PID%") do set PID=%%~A
  if "%PID%"=="" (
    del /f /q "%PID_FILE%" >nul 2>&1
    exit /b 1
  )
  REM PID 必须是纯数字
  echo %PID%| findstr /R "^[0-9][0-9]*$" >nul 2>&1
  if not !ERRORLEVEL! EQU 0 (
    del /f /q "%PID_FILE%" >nul 2>&1
    exit /b 1
  )
  REM 检查该 PID 是否仍在运行
  tasklist /FI "PID eq %PID%" 2>nul | find /I "%PID%" >nul 2>&1
  if !ERRORLEVEL! EQU 0 exit /b 0
  REM 清理失效 PID 文件
  del /f /q "%PID_FILE%" >nul 2>&1
  exit /b 1

:start
  call :check_env || goto :eof

  if exist "%PID_FILE%" (
    call :running_pid
    if !ERRORLEVEL! EQU 0 (
      set /p PID=<"%PID_FILE%"
      echo [警告] 应用已在运行 (PID: %PID%)
      echo 请先执行: start_background.bat stop
      goto :eof
    ) else (
      REM 清除失效的 PID 文件后继续启动
      del /f /q "%PID_FILE%" >nul 2>&1
    )
  )

  echo [信息] 安装/更新依赖...
  %PY% -m pip install -r "%SCRIPT_DIR%requirements.txt" >nul 2>&1

  echo [信息] 启动 FastAPI 应用 (后台模式)...
  REM 使用 PowerShell 启动并获取 PID，重定向日志到 app.log
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $wd=[IO.Path]::GetFullPath('%SCRIPT_DIR%'); $log=Join-Path $wd 'app.log'; $elog=Join-Path $wd 'app.err.log'; $args='-m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload'; $p=Start-Process -FilePath '%PY%' -ArgumentList $args -WorkingDirectory $wd -RedirectStandardOutput $log -RedirectStandardError $elog -NoNewWindow -PassThru; Start-Sleep -Milliseconds 500; $pidPath=Join-Path $wd 'app.pid'; $p.Id | Out-File -FilePath $pidPath -Encoding ascii -NoNewline;"

  if not exist "%PID_FILE%" (
    echo [错误] 启动失败，未生成 PID 文件。请查看 app.log
    goto :eof
  )

  echo [成功] 应用已启动，API 文档: http://127.0.0.1:8000/docs
  echo [信息] 查看日志: type app.log ^&^& type app.err.log
  goto :eof

:stop
  if not exist "%PID_FILE%" (
    echo [信息] 应用未在运行
    goto :eof
  )
  set /p PID=<"%PID_FILE%"
  echo [信息] 停止应用 (PID: %PID%) ...
  taskkill /PID %PID% /F >nul 2>&1
  if exist "%PID_FILE%" del /f /q "%PID_FILE%" >nul 2>&1
  echo [成功] 应用已停止
  goto :eof


:status
  call :running_pid
  if !ERRORLEVEL! EQU 0 (
    set /p PID=<"%PID_FILE%"
    echo [状态] 运行中 (PID: %PID%)
    echo [信息] API 文档: http://127.0.0.1:8000/docs
    goto :eof
  )
  echo [状态] 未运行
  goto :eof

:restart
  call :stop
  timeout /t 1 >nul
  call :start
  goto :eof

:help
  echo 使用方法:
  echo   start_background.bat start    启动应用(后台)
  echo   start_background.bat stop     停止应用
  echo   start_background.bat status   查看状态
  echo   start_background.bat restart  重启应用
  goto :eof

endlocal
