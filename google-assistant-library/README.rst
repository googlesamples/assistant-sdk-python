Google Assistant Library for Python
===================================

This package contains high level Python_ bindings for the `Google Assistant Library`_.

It is part of the `Google Assistant SDK`_.

It includes the following features:

- "Ok Google" or "Hey Google" hotword detection
- Audio recording
- Assistant response playback
- Timer and alarm features
- Volume ducking and control
- Conversation state management

See `Introduction to the Google Assistant Library`_ for a step by step guide on how to get started with the library on the Raspberry Pi 3.

Supported configuration
-----------------------

- Python ``>= 2.7``
- Architecture: ``linux-arm7l`` and ``linux-x86_64``

Installing
----------

- You can install using pip_.::

    pip install --upgrade google-assistant-library

Authorization
-------------

- Follow the steps to `configure the Actions Console project and the Google account <httpsb://developers.google.com/assistant/sdk/guides/library/python/embed/config-dev-project-and-account>`_.
- Follow the steps to `register a new device model and download the client secrets file <https://developers.google.com/assistant/sdk/guides/library/python/embed/register-device>`_.
- Generate device credentials using ``google-oauthlib-tool``:

    pip install --upgrade google-auth-oauthlib[tool]
    google-oauthlib-tool --client-secrets path/to/credentials.json --scope https://www.googleapis.com/auth/assistant-sdk-prototype --save --headless

Usage
-----

- Run the demo::

    google-assistant-demo --device_model_id 'my-model-identifier'

- Say "Ok Google" or "Hey Google" followed by a voice query. The demo should
  play back the Assistant's response and log events to the screen.

Reference
---------

- `Reference sample`_ for the Google Assistant Library for Python
- `Google Assistant Library`_ reference

License
-------

See `LICENSE`_ and `LICENSE.third_party`_.

.. _Python: https://www.python.org/
.. _Google Assistant Library: https://developers.google.com/assistant/sdk/reference/library/python
.. _Google Assistant SDK: https://developers.google.com/assistant/sdk
.. _Introduction to the Google Assistant Library: https://developers.google.com/assistant/sdk/guides/library/python/
.. _pip: https://pip.pypa.io/
.. _GitHub releases page: https://github.com/googlesamples/assistant-sdk-python/releases
.. _Google API Console Project credentials section: https://console.developers.google.com/apis/credentials
.. _LICENSE: https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-library/LICENSE
.. _LICENSE.third_party: https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-library/LICENSE.third_party
.. _google/assistant/library/LICENSE.third_party: https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-library/google/assistant/library/LICENSE.third_party
.. _Reference sample: https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-sdk/googlesamples/assistant/library
