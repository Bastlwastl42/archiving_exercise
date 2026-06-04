#!/bin/bash

set -x
set -o pipefail
set -e

uvx pyinstaller --name archive-exercise --onefile --distpath archive-exercise/usr/bin -p .venv/lib/python3.14/site-packages archive-exercise.py

dpkg-deb --build archive-exercise
