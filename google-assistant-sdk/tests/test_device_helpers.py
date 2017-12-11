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

import unittest
import concurrent.futures

from googlesamples.assistant.grpc import device_helpers


def build_device_request(device_id, command, arg):
    return {
        'inputs': [{
            'intent': 'action.devices.EXECUTE',
            'payload': {
                'commands': [{
                    'devices': [
                        {'id': device_id}
                    ],
                    'execution': [{
                        'command': command,
                        'params': {'arg': arg}
                    }]
                }]
            }
        }],
        'requestId': '42'
    }


def build_noop_device_request(device_id):
    return {
        'inputs': [{
            'intent': 'action.devices.EXECUTE',
            'payload': {
                'commands': [{
                    'devices': [
                        {'id': device_id}
                    ],
                    'execution': None,
                }]
            }
        }],
        'requestId': '42'
    }


class DeviceRequestHandlerTest(unittest.TestCase):
    def setUp(self):
        self.handler_called = False

    def handler(self, arg):
        self.handler_called = arg

    def test_success(self):
        device_handler = device_helpers.DeviceRequestHandler(
            'some-device',
        )
        device_handler.command('SOME_COMMAND')(self.handler)
        device_request = build_device_request('some-device',
                                              'SOME_COMMAND',
                                              'some-arg')
        fs = device_handler(device_request)
        self.assertEqual(len(fs), 1)
        concurrent.futures.wait(fs)
        self.assertEqual(self.handler_called, 'some-arg')

    def test_different_device(self):
        device_handler = device_helpers.DeviceRequestHandler(
            'some-device',
        )
        device_handler.command('SOME_COMMAND')(self.handler)
        device_request = build_device_request('other-device',
                                              'SOME_COMMAND',
                                              'some-arg')
        fs = device_handler(device_request)
        self.assertEqual(len(fs), 0)
        self.assertFalse(self.handler_called)

    def test_unknown_command(self):
        device_handler = device_helpers.DeviceRequestHandler(
            'some-device',
        )
        device_handler.command('SOME_COMMAND')(self.handler)
        device_request = build_device_request('some-device',
                                              'OTHER_COMMAND',
                                              'some-arg')
        fs = device_handler(device_request)
        self.assertEqual(len(fs), 1)
        self.assertFalse(self.handler_called)

    def test_noop_execution(self):
        device_handler = device_helpers.DeviceRequestHandler(
            'some-device',
        )
        device_handler.command('SOME_COMMAND')(self.handler)
        device_request = build_noop_device_request('some-device')
        fs = device_handler(device_request)
        self.assertEqual(len(fs), 0)
        self.assertFalse(self.handler_called)

    def test_exception(self):
        err = Exception('some error')

        def failing_command(arg):
            raise err
        device_handler = device_helpers.DeviceRequestHandler(
            'some-device',
        )
        device_handler.command('FAILING_COMMAND')(failing_command)
        device_request = build_device_request('some-device',
                                              'FAILING_COMMAND',
                                              'some-arg')
        fs = device_handler(device_request)
        self.assertEqual(len(fs), 1)
        concurrent.futures.wait(fs)
        self.assertEqual(fs[0].exception(), err)
