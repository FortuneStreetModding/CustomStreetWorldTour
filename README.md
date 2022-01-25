# Custom Street World Tour

![](CustomStreetWorldTourTitle.webp)

## For end users (windows only right now)

1. Download [setup.bat](Setup/setup.bat)
2. Put the `setup.bat` and a vanilla Fortune Street iso/wbfs into a new empty directory
3. Run the `setup.bat` to set up the needed tools automatically
4. Run the `CustomStreetWorldTour/build.bat` to build Custom Street World Tour

## For developers

- You need to have [git](https://git-scm.com/) installed
- You need to have [python](https://www.python.org/) installed (at least version 3.9)
  - During installation of python make sure to check the checkbox "Add Python to PATH"
- You need to have copy of Fortune Street or Boom Street (.iso or .wbfs). This file needs to be in the same directory as this script. Also make sure there is only one original iso/wbfs in this directory.

### Getting Started

1. Clone this repository using git. Do not forget to clone submodules as well.
2. Install the needed python packages using `python -m pip install --requirement requirements.txt`
3. Put a vanilla Fortune Street or Boom Street (.iso or .wbfs) into the same path. The iso image should also not contain any special characters and no spaces.
4. Start the `build.bat` (windows) or `build.sh` (unix) file to run the build.
