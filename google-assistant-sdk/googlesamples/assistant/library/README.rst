Python samples for the Google Assistant library
===============================================

This repository contains a reference sample for the ``google-assistant-library`` Python package_.

It demonstrates:
- Initialization of the Assistant
- Basic event handling including hotword detection.

.. _package: https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-library

Prerequisites
-------------

- `Python <https://www.python.org/>`_ >= 2.7
- SBC with ``linux-arm7l`` (eg: Rasbperry Pi 3) or ``linux-x86-64`` architecture.
- An `Actions Console Project <https://console.actions.google.com/>`_
- A `Google account <https://myaccount.google.com/>`_

Setup
-----

- Install Python 3

  - Ubuntu/Debian GNU/Linux::

      sudo apt-get update
      sudo apt-get install python3 python3-venv

- Create a new virtual environment (recommended)::

    python3 -m venv env
    env/bin/python -m pip install --upgrade pip setuptools wheel
    source env/bin/activate

Authorization
-------------

- Follow the steps to `configure the Actions Console project and the Google account <httpsb://developers.google.com/assistant/sdk/guides/library/python/embed/config-dev-project-and-account>`_.
- Follow the steps to `register a new device model and download the client secrets file <https://developers.google.com/assistant/sdk/guides/library/python/embed/register-device>`_.
- Generate device credentials using ``google-oauthlib-tool``:

    pip install --upgrade google-auth-oauthlib[tool]
    google-oauthlib-tool --client-secrets path/to/credentials.json --scope https://www.googleapis.com/auth/assistant-sdk-prototype --save --headless

Run the sample
--------------

- Install the sample dependencies using pip_::

    pip install --upgrade -r requirements.txt

.. _pip: https://pip.pypa.io/
.. _GitHub releases page: https://github.com/googlesamples/assistant-sdk-python/releases

- Run the hotword sample. The sample waits for the "Ok Google" hotword, then records a voice query and plays back the Google Assistant's answer::

    python -m hotword --device_model_id 'my-model-identifier'

Troubleshooting
---------------

- If audio is not working, verify the ALSA setup::

    # Play a test sound
    speaker-test -t wav

    # Record and play back some audio using ALSA command-line tools
    arecord --format=S16_LE --duration=5 --rate=16000 --file-type=raw out.raw
    aplay --format=S16_LE --rate=16000 --file-type=raw out.raw

See also the `troubleshooting section <https://developers.google.com/assistant/sdk/guides/library/troubleshooting>`_ of the official documentation.

License
-------

Copyright (C) 2017 Google Inc.

Licensed to the Apache Software Foundation (ASF) under one or more contributor
license agreements.  See the NOTICE file distributed with this work for
additional information regarding copyright ownership.  The ASF licenses this
file to you under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License.  You may obtain a copy of
the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
License for the specific language governing permissions and limitations under
the License.

