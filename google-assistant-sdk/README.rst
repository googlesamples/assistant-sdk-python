Google Assistant SDK for Python
===============================

This package contains a collection of samples and tools to help you
get started with the `Google Assistant SDK`_ using `Python`_.

Installing
----------

- You can install using `pip`_::

    pip install --upgrade google-assistant-sdk

Usage
-----

google-oauthlib-tool
~~~~~~~~~~~~~~~~~~~~

This tool creates test credentials to authorize devices to call the
Google Assistant API when prototyping.

- `Follow the steps <https://developers.google.com/assistant/sdk/prototype/getting-started-other-platforms/config-dev-project-and-account>`_ to configure a Google API Console Project and a Google account to use with the Google Assistant SDK.

- Download the ``client_secret_XXXXX.json`` file from the `Google API Console Project credentials section <https://console.developers.google.com/apis/credentials>`_ and generate credentials::

    pip install --upgrade google-auth-oauthlib[tool]
    google-oauthlib-tool --client-secrets path/to/client_secret_XXXXX.json --scope https://www.googleapis.com/auth/assistant-sdk-prototype --save --headless

googlesamples-assistant-audiotest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This tool verifies device setup for audio recording and playback.

- Install the sample's dependencies::

    sudo apt-get install portaudio19-dev libffi-dev libssl-dev
    pip install --upgrade google-assistant-sdk[samples]

- Record 10 seconds of audio samples and play them back::

    googlesamples-assistant-audiotest --record-time 10

- Adjust the sound device block size and flush size for a soundcard with limited throughput::

    googlesamples-assistant-audiotest --record-time 10 --audio-block-size=3200 --audio-flush-size=6400

The same ``--audio-block-size`` and ``--audio-flush-size`` options can
be used on the ``gRPC`` samples included in the SDK.

googlesamples-assistant-pushtotalk
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This reference sample implements a simple but functional client for the `Google Assistant gRPC API`_.

- Install the sample's dependencies::

    sudo apt-get install portaudio19-dev libffi-dev libssl-dev
    pip install --upgrade google-assistant-sdk[samples]

- Try the push to talk sample::

    googlesamples-assistant-pushtotalk

googlesamples-assistant-hotword
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This reference sample implements a simple but functional client for the `Google Assistant library`_.

- Download the latest ``linux_arm7l`` wheel for the ``google_assistant_library`` from the `GitHub releases page`_.
- Install the ``google_assistant_library`` wheel and the samples dependencies using pip_::

    pip install --upgrade google_assistant_library-0.0.2-py2.py3-none-linux_armv7l.whl
    pip install --upgrade google-assistant-sdk[samples]

- Try the hotword sample::

    googlesamples-assistant-hotword

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

.. _Python: https://python.org/
.. _pip: https://pip.pypa.io/
.. _Google Assistant SDK: https://developers.google.com/assistant/sdk
.. _Google Assistant gRPC API: https://developers.google.com/assistant/sdk/reference/rpc
.. _Google Assistant library: https://developers.google.com/assistant/sdk/reference/library/python
.. _GitHub releases page: https://github.com/googlesamples/assistant-sdk-python/releases

