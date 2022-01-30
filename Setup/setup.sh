#!/usr/bin/env sh
bad=0
if ! which git > /dev/null; then
printf 'Git not found, please download at https://git-scm.com/downloads or use a package manager such as homebrew (https://brew.sh)\n'
bad=1
fi
if ! which python3 > /dev/null; then
printf 'Python 3 not found, please download at https://www.python.org/downloads/ or use a package manager such as homebrew (https://brew.sh)\n'
bad=1
fi
if [ "$bad" -eq 1 ]; then
exit 1
fi
git clone --depth=1 --shallow-submodules --recurse-submodules="fortunestreetmodding.github.io" https://github.com/FortuneStreetModding/CustomStreetWorldTour.git --branch master
python3 -m pip install --requirement CustomStreetWorldTour/requirements.txt --user
