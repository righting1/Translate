@echo off
REM ����API��Ŀ��̨�����ű� (Windows CMD)
REM �÷�: start_background.bat [start|stop|status|restart]

setlocal ENABLEDELAYEDEXPANSION

set ACTION=%1
if "%ACTION%"=="" set ACTION=help

set SCRIPT_DIR=%~dp0
set PID_FILE=%SCRIPT_DIR%app.pid
set LOG_FILE=%SCRIPT_DIR%app.log

REM ��� Python �Ƿ����
call :check_python || goto :eof

REM �ַ�
if /I "%ACTION%"=="start" goto :start
if /I "%ACTION%"=="stop" goto :stop
if /I "%ACTION%"=="status" goto :status
if /I "%ACTION%"=="restart" goto :restart
goto :help

:check_env
  if exist "%SCRIPT_DIR%.env" goto :env_ok
  if exist "%SCRIPT_DIR%.env.example" (
    echo [��Ϣ] ���ƻ�������ģ�� .env.example �� .env
    copy /Y "%SCRIPT_DIR%.env.example" "%SCRIPT_DIR%.env" >nul
    echo [��ʾ] ��༭ .env �ļ����� API ��Կ����������
    exit /b 1
  ) else (
    echo [����] ȱ�� .env �� .env.example �ļ�
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
  echo [����] δ�ҵ� Python���밲װ������ PATH
  exit /b 1

:running_pid
  if not exist "%PID_FILE%" (
    exit /b 1
  )
  set "PID="
  set /p PID=<"%PID_FILE%"
  REM ȥ�����ܵĿո�
  for /f "tokens=*" %%A in ("%PID%") do set PID=%%~A
  if "%PID%"=="" (
    del /f /q "%PID_FILE%" >nul 2>&1
    exit /b 1
  )
  REM PID �����Ǵ�����
  echo %PID%| findstr /R "^[0-9][0-9]*$" >nul 2>&1
  if not !ERRORLEVEL! EQU 0 (
    del /f /q "%PID_FILE%" >nul 2>&1
    exit /b 1
  )
  REM ���� PID �Ƿ���������
  tasklist /FI "PID eq %PID%" 2>nul | find /I "%PID%" >nul 2>&1
  if !ERRORLEVEL! EQU 0 exit /b 0
  REM ����ʧЧ PID �ļ�
  del /f /q "%PID_FILE%" >nul 2>&1
  exit /b 1

:start
  call :check_env || goto :eof

  if exist "%PID_FILE%" (
    call :running_pid
    if !ERRORLEVEL! EQU 0 (
      set /p PID=<"%PID_FILE%"
      echo [����] Ӧ���������� (PID: %PID%)
      echo ����ִ��: start_background.bat stop
      goto :eof
    ) else (
      REM ���ʧЧ�� PID �ļ����������
      del /f /q "%PID_FILE%" >nul 2>&1
    )
  )

  echo [��Ϣ] ��װ/��������...
  %PY% -m pip install -r "%SCRIPT_DIR%requirements.txt" >nul 2>&1

  echo [��Ϣ] ���� FastAPI Ӧ�� (��̨ģʽ)...
  REM ʹ�� PowerShell ��������ȡ PID���ض�����־�� app.log
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $wd=[IO.Path]::GetFullPath('%SCRIPT_DIR%'); $log=Join-Path $wd 'app.log'; $elog=Join-Path $wd 'app.err.log'; $args='-m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload'; $p=Start-Process -FilePath '%PY%' -ArgumentList $args -WorkingDirectory $wd -RedirectStandardOutput $log -RedirectStandardError $elog -NoNewWindow -PassThru; Start-Sleep -Milliseconds 500; $pidPath=Join-Path $wd 'app.pid'; $p.Id | Out-File -FilePath $pidPath -Encoding ascii -NoNewline;"

  if not exist "%PID_FILE%" (
    echo [����] ����ʧ�ܣ�δ���� PID �ļ�����鿴 app.log
    goto :eof
  )

  echo [�ɹ�] Ӧ����������API �ĵ�: http://127.0.0.1:8000/docs
  echo [��Ϣ] �鿴��־: type app.log ^&^& type app.err.log
  goto :eof

:stop
  if not exist "%PID_FILE%" (
    echo [��Ϣ] Ӧ��δ������
    goto :eof
  )
  set /p PID=<"%PID_FILE%"
  echo [��Ϣ] ֹͣӦ�� (PID: %PID%) ...
  taskkill /PID %PID% /F >nul 2>&1
  if exist "%PID_FILE%" del /f /q "%PID_FILE%" >nul 2>&1
  echo [�ɹ�] Ӧ����ֹͣ
  goto :eof


:status
  call :running_pid
  if !ERRORLEVEL! EQU 0 (
    set /p PID=<"%PID_FILE%"
    echo [״̬] ������ (PID: %PID%)
    echo [��Ϣ] API �ĵ�: http://127.0.0.1:8000/docs
    goto :eof
  )
  echo [״̬] δ����
  goto :eof

:restart
  call :stop
  timeout /t 1 >nul
  call :start
  goto :eof

:help
  echo ʹ�÷���:
  echo   start_background.bat start    ����Ӧ��(��̨)
  echo   start_background.bat stop     ֹͣӦ��
  echo   start_background.bat status   �鿴״̬
  echo   start_background.bat restart  ����Ӧ��
  goto :eof

endlocal
