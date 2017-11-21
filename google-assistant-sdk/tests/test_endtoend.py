#!/usr/bin/python
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

import tempfile
import os.path
import subprocess


import builtins


def test_endtoend_pushtotalk():
    temp_dir = tempfile.mkdtemp()
    audio_out_file = os.path.join(temp_dir, 'out.raw')
    out = subprocess.check_output(['python', '-m',
                                   'googlesamples.assistant.grpc.pushtotalk',
                                   '--verbose',
                                   '--device-model-id', 'test-device-model',
                                   '--device-id', 'test-device',
                                   '-i', 'tests/data/whattimeisit.riff',
                                   '-o', audio_out_file],
                                  stderr=subprocess.STDOUT)
    assert 'what time is it' in builtins.str(out).lower()
    assert os.path.getsize(audio_out_file) > 0


def test_endtoend_textinput():
    p = subprocess.Popen(['python', '-m',
                          'googlesamples.assistant.grpc.textinput',
                          '--verbose',
                          '--device-model-id', 'test-device-model',
                          '--device-id', 'test-device'],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    out, err = p.communicate(b'how do you say grapefruit in French?')
    out = builtins.str(out).lower()
    assert err is None
    assert 'grapefruit' in out
    assert 'pamplemousse' in out
