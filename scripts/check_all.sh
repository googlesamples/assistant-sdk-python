#!/bin/sh
# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -ex

SRC_DIR=$(readlink -f $(dirname $0)/..)
TEST_DIR=$(mktemp -d)

sudo apt-get update
sudo apt-get install -yq python3-dev python3.4-venv portaudio19-dev libffi-dev libssl-dev
python3 -m venv ${TEST_DIR}
${TEST_DIR}/bin/python -m pip install --upgrade pip

cd ${SRC_DIR}
${TEST_DIR}/bin/pip install .[MAIN]
${TEST_DIR}/bin/python setup.py test
# TODO(proppy): move in a separate check
${TEST_DIR}/bin/python setup.py flake8

