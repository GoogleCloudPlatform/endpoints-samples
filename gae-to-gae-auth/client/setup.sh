#!/usr/bin/env bash

# This script creates a virtual environment with a fresh version of Python 2.7
# It also installs the requirements needed to run this client script.

if [[ ! -f py27-venv/bin/activate ]]; then
  virtualenv -p python2.7 py27-venv
fi
source py27-venv/bin/activate

pip install --requirement requirements.txt
