Google Assistant Python Sample
==============================

This repository contains a Python sample for the Google Assistant API.

See `Getting Started with the Raspberry Pi 3 <https://developers.google.com/assistant/>`_ for
instructions on how to run the sample on supported hardware.

Prerequisites
-------------

- `Python <https://www.python.org/>`_ (3.x prefered)
- `Google API Console Project <https://console.developers.google.com>`_ w/ Google Assistant API `enabled <https://console.developers.google.com/apis>`_.
- `OAuth client ID credentials <https://console.developers.google.com/apis/credentials>`_ with application type ``Other``.
- Use a new virtualenv (recommended)::

        # python3 (recommended)
        sudo apt-get update
        sudo apt-get install python3-dev python3-venv
        python3 -m venv env
        env/bin/python -m pip install --upgrade pip setuptools
        source env/bin/activate

        # python2
        sudo apt-get update
        sudo apt-get install python-dev python-virtualenv
        virtualenv env --no-site-packages
        env/bin/python -m pip install --upgrade pip setuptools
        source env/bin/activate

Setup
-----

- Install the sample dependencies::

       sudo apt-get install portaudio19-dev libffi-dev libssl-dev

- Install the latest Google Assistant SDK and samples package from `PyPI <https://pypi.python.org/pypi>`_::

       python -m pip install --upgrade google-assistant-sdk[samples]

        - Or if working from this repository's sources, run::

                python -m pip install --upgrade -e ".[samples]"

- Authorize access to the Google Assistant API::

        python -m googlesamples.assistant.auth_helpers --client-secrets client_secret_XXXX.json
        Please go to this URL: ...
        Enter the authorization code:

-  Verify audio setup::

        # Record a 5 sec sample and play it back
        python -m googlesamples.assistant.audio_helpers

Run the Sample
--------------

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

For Maintainers
---------------

See `MAINTAINER.md <MAINTAINER.md>`_ for more documentation on the
development, maintainance and release of the Python package itself.

Contributing
------------

Contributions to this repository are always welcome and highly encouraged.

See `CONTRIBUTING.md <CONTRIBUTING.md>`_ for more information on how to get started.

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
