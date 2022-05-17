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
python3 build.py \
        --output-version 1.0 \
        --csmm-version 1.7.5 \
        --resources-mirror "https://nikkums.io/cswt/1.0/CSWT1Files.zip" \
        --resources-mirror "https://drive.google.com/u/2/uc?id=1NvI7Y7o9vAC7ibBkGt1m4qozfkMm-_Jq&export=download&confirm=1" \
        --boards-list-file "CustomStreetWorldTour.yaml" \
        --overwrite-extracted-directory
