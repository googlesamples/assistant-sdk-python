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

import json
import tempfile
import os
import os.path
import pytest
import subprocess
import uuid


import builtins
PROJECT_ID = os.environ.get('PROJECT_ID', 'dummy-project-id')


@pytest.fixture(scope='session')
def device_model():
    device_model_id = 'assistant-sdk-test-model-%s' % str(uuid.uuid1())
    subprocess.check_call(['python', '-m',
                           'googlesamples.assistant.grpc.devicetool',
                           '--project-id', PROJECT_ID,
                           'register-model', '--model', device_model_id,
                           '--type', 'LIGHT',
                           '--trait', 'action.devices.traits.OnOff',
                           '--manufacturer', 'assistant-sdk-test',
                           '--product-name', 'assistant-sdk-test'])
    yield device_model_id
    subprocess.check_call(['python', '-m',
                           'googlesamples.assistant.grpc.devicetool',
                           '--project-id', PROJECT_ID,
                           'delete', '--model', device_model_id])


@pytest.fixture(scope='session')
def device_instance(device_model):
    device_instance_id = 'assistant-sdk-test-device-%s' % str(uuid.uuid1())
    subprocess.check_call(['python', '-m',
                           'googlesamples.assistant.grpc.devicetool',
                           '--project-id', PROJECT_ID,
                           'register-device', '--model', device_model,
                           '--client-type', 'SERVICE',
                           '--device', device_instance_id])
    yield device_instance_id
    subprocess.check_call(['python', '-m',
                           'googlesamples.assistant.grpc.devicetool',
                           '--project-id', PROJECT_ID,
                           'delete', '--device', device_instance_id])


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


def test_registration_pushtotalk(device_model):
    temp_dir = tempfile.mkdtemp()
    audio_out_file = os.path.join(temp_dir, 'out.raw')
    # Use an non-existing device config file intentionally
    # to force device registration.
    device_config = os.path.join(temp_dir, 'device_config.json')
    out = subprocess.check_output(['python', '-m',
                                   'googlesamples.assistant.grpc.pushtotalk',
                                   '--verbose',
                                   '--project-id', PROJECT_ID,
                                   '--device-model-id', device_model,
                                   '--device-config', device_config,
                                   '-i', 'tests/data/whattimeisit.riff',
                                   '-o', audio_out_file],
                                  stderr=subprocess.STDOUT)
    assert 'what time is it' in builtins.str(out).lower()
    assert os.path.getsize(audio_out_file) > 0
    with open(device_config) as f:
        config = json.load(f)
        assert ('device registered: %s' % config['id']
                in builtins.str(out).lower())
        out = subprocess.check_output(
            ['python', '-m',
             'googlesamples.assistant.grpc.devicetool',
             '--project-id', PROJECT_ID,
             'get', '--device', config['id']],
            stderr=subprocess.STDOUT
        )
        assert ('device instance id: %s' % config['id']
                in builtins.str(out).lower())
        subprocess.check_call(['python', '-m',
                               'googlesamples.assistant.grpc.devicetool',
                               '--project-id', PROJECT_ID,
                               'delete', '--device', config['id']])


def test_endtoend_textinput(device_model, device_instance):
    p = subprocess.Popen(['python', '-m',
                          'googlesamples.assistant.grpc.textinput',
                          '--verbose',
                          '--device-model-id', device_model,
                          '--device-id', device_instance],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    out, err = p.communicate(b'how do you say grapefruit in French?')
    out = builtins.str(out).lower()
    assert err is None
    assert 'grapefruit' in out
    assert 'pamplemousse' in out


def test_onoff_device_action(device_model):
    temp_dir = tempfile.mkdtemp()
    audio_out_file = os.path.join(temp_dir, 'out.raw')
    # Use an non-existing device config file intentionally
    # to force device registration.
    device_config = os.path.join(temp_dir, 'device_config.json')
    out = subprocess.check_output(['python', '-m',
                                   'googlesamples.assistant.grpc.pushtotalk',
                                   '--verbose',
                                   '--project-id', PROJECT_ID,
                                   '--device-model-id', device_model,
                                   '--device-config', device_config,
                                   '-i', 'tests/data/turnon.riff',
                                   '-o', audio_out_file],
                                  stderr=subprocess.STDOUT)
    assert 'turning device on' in builtins.str(out).lower()
    assert os.path.getsize(audio_out_file) > 0
