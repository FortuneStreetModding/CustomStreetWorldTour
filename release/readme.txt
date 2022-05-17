# Installation

Place a Fortune Street iso/wbfs or Boom Street iso/wbfs into the same directory and run the build.bat/build_console.bat on Windows and build.sh/build_console.sh on MacOS.

The difference between build and build_console is that build works only for Dolphin, while the build_console is meant to specifically be used on the console.

If you are on Windows, python will be installed during the build process. You may need to confirm some prompts. 
If you are on MacOS, you need to install python yourself as prerequisite before running the build.sh/build_console.sh.

# Troubleshooting

## Building fails with the Error Message "Unable to start winget"

Go to the Microsoft Store and install the package "App Installer"

## Building fails with the Error Message "QTemporaryDir: Unable to remove due to read-only files"

The fix for this issue is to start Internet Explorer at least once

# Known Issues

- Tour mode does not really work with custom maps. Completed maps are not saved.