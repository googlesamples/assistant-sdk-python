Google Assistant gRPC API Sample for Python
===========================================

This repository contains a reference sample for the ``google-assistant-grpc`` Python package.

Prerequisites
-------------

- `Python <https://www.python.org/>`_ (>= 3.4 recommended).
- A `Google API Console Project <https://console.developers.google.com>`_.
- A `Google Account <https://myaccount.google.com/>`_.

Setup
-----

- Follow `the steps to configure the project and the google account <https://developers.google.com/assistant/sdk/prototype/getting-started-other-platforms/config-dev-project-and-account>`_.

- Install Python 3

    - Ubuntu/Debian GNU/Linux::

        sudo apt-get update
        sudo apt-get install python3 python3-venv
	
    - `MacOSX, Windows, Other <https://www.python.org/downloads/>`_

- Create a new virtualenv (recommended)::

    python3 -m venv env
    env/bin/python -m pip install --upgrade pip setuptools
    source env/bin/activate

- Install the sample dependencies::

    sudo apt-get install libffi-dev
    pip install --upgrade -r requirements.txt

Authorization
-------------

- Download the ``client_secret_XXXXX.json`` file from the `Google API Console Project credentials section <https://console.developers.google.com/apis/credentials>`_ and generate credentials using ``google-oauth-tool``.::

    pip install --upgrade google-auth-oauthlib[tool]
    google-oauthlib-tool --client-secrets path/to/client_secret_XXXXX.json --scope https://www.googleapis.com/auth/assistant-sdk-prototype --save

Run the sample
--------------

-  Verify audio setup::

    # Record a 5 sec sample and play it back
    python -m googlesamples.assistant.audio_helpers

- Record a voice query and the program should play back the Google Assistant's answer::

    python -m googlesamples.assistant

-  Record and send pre-recorded audio to the Assistant::

    python -m googlesamples.assistant -i in.wav

- Save Assistant response to a file::

    python -m googlesamples.assistant -o out.wav

Troubleshooting
---------------

- Verify ALSA setup::

    # Play a test sound
    speaker-test -t wav

    # Record and play back some audio using ALSA command-line tools
    arecord --format=S16_LE --duration=5 --rate=16k --file-type=raw out.raw
    aplay --format=S16_LE --rate=16k --file-type=raw out.raw

- Run the sample with verbose logging enabled::

    python -m googlesamples.assistant --verbose

- If Assistant audio is choppy, try adjusting the sound device's block size::

    # If using a USB speaker or dedicated soundcard, set block size to "0"
    # to automatically adjust the buffer size
    python -m googlesamples.assistant.audio_helpers --audio-block-size=0

    # If using the line-out 3.5mm audio jack on the device, set block size
    # to a value larger than the `ConverseResponse` audio payload size
    python -m googlesamples.assistant.audio_helpers --audio-block-size=3200

    # Run the Assistant sample using the best block size value found above
    python -m googlesamples.assistant --audio-block-size=value

- If Assistant audio is truncated, try adjusting the sound device's flush size::

    # Set flush size to a value larger than the audio block size. You can
    # run the sample using the --audio-flush-size flag as well.
    python -m googlesamples.assistant.audio_helpers --audio-block-size=3200 --audio-flush-size=6400

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
