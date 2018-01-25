Google Assistant SDK for Python
===============================

This package contains a collection of samples and tools to help you
get started with the `Google Assistant SDK`_ using `Python`_.

Installing
----------

- You can install using `pip`_::

    pip install --upgrade google-assistant-sdk[samples]

Usage
-----

google-oauthlib-tool
~~~~~~~~~~~~~~~~~~~~

This tool creates test credentials to authorize devices to call the
Google Assistant API when prototyping.

- `Follow the steps <https://developers.google.com/assistant/sdk/guides/configure-developer-project>`_ to configure a Google API Console Project and a Google account to use with the Google Assistant SDK.

- Download the ``client_secret_XXXXX.json`` file from the `Google API Console Project credentials section <https://console.developers.google.com/apis/credentials>`_ in the current directory.

- Generate credentials using ``google-oauth-tool``::

    pip install --upgrade google-auth-oauthlib[tool]
    google-oauthlib-tool --client-secrets client_secret_XXXXX.json --scope https://www.googleapis.com/auth/assistant-sdk-prototype --save --headless

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

googlesamples-assistant-devicetool
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This tool allows you to register Google Assistant device models and
instances and associate them with Device Actions traits.

- Install the sample's dependencies::

    sudo apt-get install portaudio19-dev libffi-dev libssl-dev
    pip install --upgrade google-assistant-sdk[samples]

- Show the CLI tool usage::

    googlesamples-assistant-devicetool --help

- Register a new device model and new device instance (after replacing the 'placeholder values' between quotes)::

   googlesamples-assistant-devicetool register --model 'my-model-identifier' \
                                               --type LIGHT --trait action.devices.traits.OnOff \
                                               --manufacturer 'Assistant SDK developer' \
                                               --product-name 'Assistant SDK light' \
                                               --description 'Assistant SDK light device' \
                                               --device 'my-device-identifier' \
                                               --nickname 'My Assistant Light'

- Register or overwrite the device model with the supported traits (after replacing the 'placeholder values' between quotes)::

   googlesamples-assistant-devicetool register-model --model 'my-model-identifier' \
                                                     --type LIGHT --trait action.devices.traits.OnOff \
                                                     --manufacturer 'Assistant SDK developer' \
                                                     --product-name 'Assistant SDK light' \
                                                     --description 'Assistant SDK light device'

*Note: The model identifier must be globally unique.*

- Register or overwrite the device instance using the device model (after replacing the 'placeholder values' between quotes)::

    googlesamples-assistant-devicetool register-device --device 'my-device-identifier' \
                                                       --model 'my-model-identifier' \
                                                       --nickname 'My Assistant Light'

*Note: The device instance identifier should be unique within the Google Developer Project associated with the device.*

- Verify that the device model and instance have been registered correctly::

    googlesamples-assistant-devicetool get --model 'my-model-identifier'
    googlesamples-assistant-devicetool get --device 'my-device-identifier'

- List all device models and instances::

    googlesamples-assistant-devicetool list --model
    googlesamples-assistant-devicetool list --device

googlesamples-assistant-pushtotalk
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This reference sample implements a simple but functional client for the `Google Assistant Service`_.

- Install the sample's dependencies::

    sudo apt-get install portaudio19-dev libffi-dev libssl-dev
    pip install --upgrade google-assistant-sdk[samples]

- Run the push to talk sample. The sample records a voice query after a key press and plays back the Google Assistant's answer::

    googlesamples-assistant-pushtotalk --device-model-id 'my-device-model' --device-id 'my-device-identifier'

- Try some Google Assistant voice query like "What time is it?" or "Who am I?".

- Try a device action query like "Turn <nickname / model product name> on".

- Run in verbose mode to see the gRPC communication with the Google Assistant API::

    googlesamples-assistant-pushtotalk --device-model-id 'my-device-model' --device-id 'my-device-identifier' -v

googlesamples-assistant-hotword
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This reference sample implements a simple but functional client for the `Google Assistant Library`_ (``linux_arm7l`` and ``linux_x86_64``).

- Install the ``google-assistant-library`` package::

    pip install --upgrade google-assistant-library
    pip install --upgrade google-assistant-sdk[samples]

- Try the hotword sample::

    googlesamples-assistant-hotword --device_model_id 'my-model-identifier'

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
.. _Google Assistant Service: https://developers.google.com/assistant/sdk/reference/rpc
.. _Google Assistant Library: https://developers.google.com/assistant/sdk/reference/library/python
