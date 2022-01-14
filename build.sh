#!/usr/bin/env sh
git submodule init
git submodule update
python3 -m pip install --requirement requirements.txt --user
python3 build.py

