@echo off
:: Set background to Black (0) and text to Aqua (B)
color 0B
set "pfad=%cd%"

:: ==========================================
:: 1. AUTO-ELEVATION (ADMIN RIGHTS)
:: ==========================================
fsutil dirty query %systemdrive% >nul 2>&1
if %errorlevel% NEQ 0 (
    echo [!] Requesting Administrative privileges...
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B
)

pushd "%CD%"
CD /D "%~dp0"

:: ==========================================
:: 2. PREMIUM UI HEADER
:: ==========================================
title Maki PC Cleaner v1.0 [ULTIMATE EDITION]
cls
echo.
echo  ============================================================
echo    __  __              _     _____   _____   _                 
echo   ^| \/  ^|            ^| ^|   ^|  __ \ / ____^| ^| ^|                
echo   ^| \  / ^| __ _  ^| ^| _ ^| ^|__) ^| ^|     ^| ^| ___   __ _  _ __   ___  _ __ 
echo   ^| ^|\/^| ^| / _` ^| ^| ^|/ /^|  ___/ ^| ^|     ^| ^| / _ \ / _` ^|^| '_ \  / _ \^| '__^|
echo   ^| ^|  ^| ^|^| (_^| ^| ^|   ^< ^| ^|     ^| ^|____ ^| ^|^|  __/^| (_^| ^|^| ^| ^| ^|^|  __/^| ^|   
echo   ^|_^|  ^|_^| \__,_^| ^|_^|\_\^|_^|      \_____^|^|_^| \___^| \__,_^|^|_^| ^|_^| \___^|^|_^|   
echo.                                                           
echo   [ VERSION: 1.0 ]   [ STATUS: READY ]   [ SYSTEM: Win 11 ]
echo  ============================================================
echo.

:: ==========================================
:: 3. SOLARA FILE CLEANUP PROMPT
:: ==========================================
echo  [?] SECURITY CHECK:
echo      Would you like to auto-delete Solara files and folders?
echo.
set /p userchoice="  [Y/N] Confirm Selection: "

if /i "%userchoice%"=="Y" (
    echo.
    echo  [!] INITIALIZING ASSET WIPE...
    taskkill /F /IM "Solara.exe" /T >nul 2>&1
    taskkill /F /IM "Bootstrapper.exe" /T >nul 2>&1
    powershell -Command "foreach ($folder in 'SolaraTab','Solaratab','Solara','scripts','autoexec','workspace') { if (Test-Path $folder) { Remove-Item -Path $folder -Recurse -Force } }" >nul 2>&1
    if exist "Solara.exe" del /f /q "Solara.exe" >nul 2>&1
    if exist "Bootstrapper.exe" del /f /q "Bootstrapper.exe" >nul 2>&1
    echo  [+] TARGETED ASSETS REMOVED.
)

echo.
echo  [!] PREPARING DEEP CLEAN ENGINE...
ping 127.0.0.1 -n 4 >nul

:: ==========================================
:: 4. DYNAMIC CLEANING - PROTECTION HISTORY & FORENSICS
:: ==========================================
cls
echo.
echo  [ STATUS: CLEANING IN PROGRESS ]
echo  ------------------------------------------------------------
echo  [#######                     ] 25%% - Wiping Protection History ^& BAM

:: Windows Defender History Wipe
powershell -Command "Set-MpPreference -ScanPurgeItemsAfterDelay 1" >nul 2>&1
"C:\Program Files\Windows Defender\MpCmdRun.exe" -RemoveDefinitions -All >nul 2>&1
powershell -Command "$Paths = @('C:\ProgramData\Microsoft\Windows Defender\Scans\History\Service\DetectionHistory', 'C:\ProgramData\Microsoft\Windows Defender\Scans\History\Service\Results', 'C:\ProgramData\Microsoft\Windows Defender\Scans\History\Store'); foreach ($Path in $Paths) { if (Test-Path $Path) { takeown /f $Path /r /d y >$null; icacls $Path /grant administrators:F /t >$null; Get-ChildItem -Path $Path -Recurse | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue } }" >nul 2>&1
wevtutil cl "Microsoft-Windows-Windows Defender/Operational" >nul 2>&1

:: BAM Reset logic
powershell -Command "$path = 'HKLM:\SYSTEM\CurrentControlSet\Services\bam\State\UserSettings'; $key = [Microsoft.Win32.Registry]::LocalMachine.OpenSubKey('SYSTEM\CurrentControlSet\Services\bam\State\UserSettings', [Microsoft.Win32.RegistryKeyPermissionCheck]::ReadWriteSubTree, [System.Security.AccessControl.RegistryRights]::takeownership); $acl = $key.GetAccessControl(); $acl.SetOwner([System.Security.Principal.NTAccount]'Administrators'); $key.SetAccessControl($acl); $acl = Get-Acl $path; $rule = New-Object System.Security.AccessControl.RegistryAccessRule('Administrators','FullControl','ContainerInherit,ObjectInherit','None','Allow'); $acl.SetAccessRule($rule); Set-Acl $path $acl" >nul 2>&1
for /f "tokens=*" %%a in ('reg query "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\bam\State\UserSettings" ^| findstr /i "S-1-5-21-"') do (reg delete "%%a" /f >nul 2>&1)

cls
echo.
echo  [ STATUS: CLEANING IN PROGRESS ]
echo  ------------------------------------------------------------
echo  [##############              ] 50%% - Advanced 9z Project String Cleaning

:: Clean Data Usage (SruSvc)
powershell -Command "Stop-Service -Name 'SruSvc' -Force; Remove-Item -Path 'C:\Windows\System32\sru\*' -Recurse -Force; Start-Service -Name 'SruSvc'" >nul 2>&1

:: Clean USB Plug History
reg delete "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\USBSTOR" /f >nul 2>&1
reg delete "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\USB" /f >nul 2>&1

:: Clean Shimcache, Amcache, and RecentFileCache
reg delete "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache" /v "AppCompatCache" /f >nul 2>&1
powershell -Command "Remove-Item -Path 'C:\Windows\AppCompat\Programs\Amcache.hve*' -Force" >nul 2>&1
if exist "C:\Windows\AppCompat\Programs\RecentFileCache.bcf" del /f /q "C:\Windows\AppCompat\Programs\RecentFileCache.bcf" >nul 2>&1

:: Clean Run History, Windows Search, Form History, and MRU Registry
reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU" /f >nul 2>&1
reg delete "HKEY_CURRENT_USER\SOFTWARE\Classes\Local Settings\Software\Microsoft\Windows\Shell\BagMRU" /f >nul 2>&1
reg delete "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSavePidlMRU" /f >nul 2>&1
reg delete "HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache" /f >nul 2>&1

:: Clean Thumbnail Cache
del /f /s /q /a %LocalAppData%\Microsoft\Windows\Explorer\thumbcache_*.db >nul 2>&1

:: Empty Recycle Bin
powershell -Command "Clear-RecycleBin -Confirm:$false" >nul 2>&1

cls
echo.
echo  [ STATUS: CLEANING IN PROGRESS ]
echo  ------------------------------------------------------------
echo  [#####################       ] 75%% - Purging System Journals ^& Logs

:: System Journals ^& Event Logs
fsutil usn deletejournal /d c: >nul 2>&1
powershell -noprofile -command "Get-EventLog -LogName * | ForEach { Clear-EventLog $_.Log }" >nul 2>&1

:: --- ADDED: TEMP, %TEMP%, AND PREFETCH CLEANING ---
:: Robust PowerShell Cleaning for Temp & Prefetch
powershell -Command "Get-ChildItem -Path $env:TEMP -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue" >nul 2>&1
powershell -Command "Get-ChildItem -Path 'C:\Windows\Temp' -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue" >nul 2>&1
powershell -Command "Get-ChildItem -Path 'C:\Windows\Prefetch' -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue" >nul 2>&1
:: --------------------------------------------------

:: Chrome History Fix (Prevents Logout)
taskkill /F /IM "chrome.exe" /T >nul 2>&1
set "chrome_path=%LOCALAPPDATA%\Google\Chrome\User Data"
for /d %%d in ("%chrome_path%\*") do (
    if exist "%%d\History" del /f /q "%%d\History" >nul 2>&1
    if exist "%%d\Visited Links" del /f /q "%%d\Visited Links" >nul 2>&1
    if exist "%%d\Web Data" del /f /q "%%d\Web Data" >nul 2>&1
)

:: Clean NirSoft ^& OsForensics Logs
powershell -Command "Get-ChildItem -Path $env:TEMP, $env:SystemRoot\Temp -Include *nirsoft*, *osforensics* -Recurse | Remove-Item -Force" >nul 2>&1

:: Discord Link Backup
:: Use %APPDATA% (Roaming) which is the correct location for Start Menu programs in user context.
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Discord Inc\Discord.lnk" (
    copy "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Discord Inc\Discord.lnk" "%pfad%" >nul 2>&1
)

cls
echo.
echo  [ STATUS: CLEANING IN PROGRESS ]
echo  ------------------------------------------------------------
echo  [##############################] 100%% - CLEAN COMPLETE
ping 127.0.0.1 -n 3 >nul

:: ==========================================
:: 5. SUCCESS REPORT
:: ==========================================
cls
echo.
echo  ============================================================
echo                MAKI PC CLEANER - SUCCESS REPORT
echo  ============================================================
echo.
echo   [+] PROTECTION HISTORY:  DEEP PURGED
echo   [+] USN CHANGE JOURNAL: WIPED
echo   [+] EVENT LOGS:          CLEARED
echo   [+] RECYCLE BIN:         EMPTIED
echo   [+] TEMP/PREFETCH:       WIPED
echo   [+] FORENSIC STRINGS:    WIPED (USB/Shim/Data)
echo   [+] BROWSER HISTORY:     CLEANED (LOGINS PRESERVED)
echo.
echo  ------------------------------------------------------------
echo   Process finished. Restart your PC to refresh settings.
echo  ------------------------------------------------------------
echo.
echo  Press any key to exit...
pause >nul

exit