where /q git
IF ERRORLEVEL 1 (
    winget install --id Git.Git -e --source winget
    where /q git
    IF ERRORLEVEL 1 (
        EXIT /B
    )
)
where /q python
IF ERRORLEVEL 1 (
    winget install -e --id Python.Python.3
    where /q python
    IF ERRORLEVEL 1 (
        EXIT /B
    )
)
git clone --depth=1 --shallow-submodules --recurse-submodules="fortunestreetmodding.github.io" https://github.com/FortuneStreetModding/CustomStreetWorldTour.git --branch master
python -m pip install --requirement CustomStreetWorldTour/requirements.txt --user
@pause