@echo off
git --version
IF ERRORLEVEL 1 (
    Echo Installing Git...
    winget install --id Git.Git -e --source winget
    IF ERRORLEVEL 1 (
        Echo Error installing git
        @pause
        EXIT /B
    )
    call ..\RefreshEnv.cmd
    git --version
    IF ERRORLEVEL 1 (
        Echo Error installing git
        @pause
        EXIT /B
    )
    Echo Git installed successfully
)
python --version
IF ERRORLEVEL 1 (
    Echo Installing Python...
    winget install -e --id Python.Python.3
    IF ERRORLEVEL 1 (
        Echo Error installing Python
        @pause
        EXIT /B
    )
    call ..\RefreshEnv.cmd
    python --version
    IF ERRORLEVEL 1 (
        Echo Error installing Python
        @pause
        EXIT /B
    )
    Echo Python installed successfully
)
git clone --depth=1 --shallow-submodules --recurse-submodules="fortunestreetmodding.github.io" https://github.com/FortuneStreetModding/CustomStreetWorldTour.git --branch master
python -m pip install --requirement CustomStreetWorldTour/requirements.txt --user
IF ERRORLEVEL 0 (
    Echo Setup finished and ready to build!
    Echo You can now run CustomStreetWorldTour/build.bat
)
@pause