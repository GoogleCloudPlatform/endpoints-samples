#!/usr/bin/env bash
# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# This script creates a virtual environment with a fresh version of Python 2.7
# It also installs the requirements needed to run this client script.

if [[ ! -f py3-venv/bin/activate ]]; then
  virtualenv -p python3 py3-venv
fi
source py3-venv/bin/activate

pip install --requirement requirements.txt
