#!/usr/bin/env sh
bad=0
if ! which python3 > /dev/null; then
printf 'Python 3 not found, please download at https://www.python.org/downloads/ or use a package manager such as homebrew (https://brew.sh)\n'
bad=1
fi
if [ "$bad" -eq 1 ]; then
exit 1
fi
python3 -m pip install --requirement requirements.txt --user
python3 build.py
