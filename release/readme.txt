# Installation

Place a Fortune Street iso/wbfs or Boom Street iso/wbfs into the same directory and run the build.bat/build_console.bat on Windows and build.sh/build_console.sh on MacOS.

The difference between build and build_console is that build works only for Dolphin, while the build_console is meant to specifically be used on the console.

If you are on Windows, python will be installed during the build process. You may need to confirm some prompts. 
If you are on MacOS, you need to install python yourself as prerequisite before running the build.sh/build_console.sh.

# Troubleshooting

## Building fails with the error message: 'winget' is not recognized as an internal or external command, operable program or batch file.

Go to the Microsoft Store and install the package "App Installer"

## Building fails with the error message: QTemporaryDir: Unable to remove "C:\\Users\\...." most likely due to the presence of read-only-files.

Start Internet Explorer. A dialog should pop up which says "Set up Internet Explorer". Use the recommended settings and click OK. Now you can close Internet Explorer and try again.

## Building fails with the error message: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:997)>

Check this link: https://www.dev2qa.com/how-to-fix-python-error-certificate-verify-failed-unable-to-get-local-issuer-certificate-in-mac-os/

# Known Issues

- Tour mode does not really work with custom maps. Completed maps are not saved.
- In Wiimmfi mode some boards may become locked and not selectable.