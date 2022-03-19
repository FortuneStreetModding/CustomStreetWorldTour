@echo off
git --version
IF ERRORLEVEL 1 (
    ECHO Installing Git...
    winget install --id Git.Git -e --source winget
    IF ERRORLEVEL 1 (
        ECHO Error installing git
        @pause
        EXIT /B
    )
    CALL :RefreshEnv
    git --version
    IF ERRORLEVEL 1 (
        ECHO Error installing git
        @pause
        EXIT /B
    )
    ECHO Git installed successfully
)
python --version
IF ERRORLEVEL 1 (
    ECHO Installing Python...
    winget install -e --id Python.Python.3
    IF ERRORLEVEL 1 (
        ECHO Error installing Python
        @pause
        EXIT /B
    )
    CALL :RefreshEnv
    python --version
    IF ERRORLEVEL 1 (
        ECHO Error installing Python
        @pause
        EXIT /B
    )
    ECHO Python installed successfully
)
git clone --depth=1 --shallow-submodules --recurse-submodules="fortunestreetmodding.github.io" https://github.com/FortuneStreetModding/CustomStreetWorldTour.git --branch s3-test-branch
python -m pip install --requirement CustomStreetWorldTour/requirements.txt --user
IF ERRORLEVEL 0 (
    ECHO Setup finished and ready to build!
    ECHO You can now run CustomStreetWorldTour/build.bat
)
@pause
EXIT /B %ERRORLEVEL%







:RefreshEnv
:: Taken from https://github.com/chocolatey/choco/blob/develop/src/chocolatey.resources/redirects/RefreshEnv.cmd
::
:: RefreshEnv.cmd
::
:: Batch file to read environment variables from registry and
:: set session variables to these values.
::
:: With this batch file, there should be no need to reload command
:: environment every time you want environment changes to propagate

::echo "RefreshEnv.cmd only works from cmd.exe, please install the Chocolatey Profile to take advantage of refreshenv from PowerShell"
echo | set /p dummy="Refreshing environment variables from registry for cmd.exe. Please wait..."

goto main

:: Set one environment variable from registry key
:SetFromReg
    "%WinDir%\System32\Reg" QUERY "%~1" /v "%~2" > "%TEMP%\_envset.tmp" 2>NUL
    for /f "usebackq skip=2 tokens=2,*" %%A IN ("%TEMP%\_envset.tmp") do (
        echo/set "%~3=%%B"
    )
    goto :EOF

:: Get a list of environment variables from registry
:GetRegEnv
    "%WinDir%\System32\Reg" QUERY "%~1" > "%TEMP%\_envget.tmp"
    for /f "usebackq skip=2" %%A IN ("%TEMP%\_envget.tmp") do (
        if /I not "%%~A"=="Path" (
            call :SetFromReg "%~1" "%%~A" "%%~A"
        )
    )
    goto :EOF

:main
    echo/@echo off >"%TEMP%\_env.cmd"

    :: Slowly generating final file
    call :GetRegEnv "HKLM\System\CurrentControlSet\Control\Session Manager\Environment" >> "%TEMP%\_env.cmd"
    call :GetRegEnv "HKCU\Environment">>"%TEMP%\_env.cmd" >> "%TEMP%\_env.cmd"

    :: Special handling for PATH - mix both User and System
    call :SetFromReg "HKLM\System\CurrentControlSet\Control\Session Manager\Environment" Path Path_HKLM >> "%TEMP%\_env.cmd"
    call :SetFromReg "HKCU\Environment" Path Path_HKCU >> "%TEMP%\_env.cmd"

    :: Caution: do not insert space-chars before >> redirection sign
    echo/set "Path=%%Path_HKLM%%;%%Path_HKCU%%" >> "%TEMP%\_env.cmd"

    :: Cleanup
    del /f /q "%TEMP%\_envset.tmp" 2>nul
    del /f /q "%TEMP%\_envget.tmp" 2>nul

    :: capture user / architecture
    SET "OriginalUserName=%USERNAME%"
    SET "OriginalArchitecture=%PROCESSOR_ARCHITECTURE%"

    :: Set these variables
    call "%TEMP%\_env.cmd"

    :: Cleanup
    del /f /q "%TEMP%\_env.cmd" 2>nul

    :: reset user / architecture
    SET "USERNAME=%OriginalUserName%"
    SET "PROCESSOR_ARCHITECTURE=%OriginalArchitecture%"

    echo | set /p dummy="Finished."
    echo .
    goto :EOF