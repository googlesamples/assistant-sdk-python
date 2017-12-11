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

"""Helper functions for the Device Actions."""

import concurrent.futures
import logging
import sys


key_inputs_ = 'inputs'
key_intent_ = 'intent'
key_payload_ = 'payload'
key_commands_ = 'commands'
key_id_ = 'id'


class DeviceRequestHandler(object):
    """Asynchronous dispatcher for Device actions commands.

    Dispatch commands to the given device handlers.

    Args:
      device_id: device id to match command against

    Example:
      # Use as as decorator to register handler.
      device_handler = DeviceRequestHandler('my-device')
      @device_handler.command('INTENT_NAME')
      def handler(param):
          pass
    """

    def __init__(self, device_id):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.device_id = device_id
        self.handlers = {}

    def __call__(self, device_request):
        """Handle incoming device request.

        Returns: List of concurrent.futures for each command execution.
        """
        fs = []
        if key_inputs_ in device_request:
            for input in device_request[key_inputs_]:
                if input[key_intent_] == 'action.devices.EXECUTE':
                    for command in input[key_payload_][key_commands_]:
                        fs.extend(self.submit_commands(**command))
        return fs

    def command(self, intent):
        """Register a device action handlers."""
        def decorator(fn):
            self.handlers[intent] = fn
        return decorator

    def submit_commands(self, devices, execution):
        """Submit device command executions.

        Returns: a list of concurrent.futures for scheduled executions.
        """
        fs = []
        for device in devices:
            if device[key_id_] != self.device_id:
                logging.warning('Ignoring command for unknown device: %s'
                                % device[key_id_])
                continue
            if not execution:
                logging.warning('Ignoring noop execution')
                continue
            for command in execution:
                f = self.executor.submit(
                    self.dispatch_command, **command
                )
                fs.append(f)
        return fs

    def dispatch_command(self, command, params=None):
        """Dispatch device commands to the appropriate handler."""
        try:
            if command in self.handlers:
                self.handlers[command](**params)
            else:
                logging.warning('Unsupported command: %s: %s',
                                command, params)
        except Exception as e:
            logging.warning('Error during command execution',
                            exc_info=sys.exc_info())
            raise e
