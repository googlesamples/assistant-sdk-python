Google Assistant Library for Python
===================================

This package contains high level Python_ bindings for the `Google Assistant Library`_.

It is part of the `Google Assistant SDK for devices`_.

It includes the following features:

- "Ok Google" or "Hey Google" hotword detection
- Audio recording
- Assistant response playback
- Timer and alarm features
- Volume ducking and control
- Conversation state management
- Playback of podcasts and news
- Broadcast voice messages

See `Introduction to the Google Assistant Library`_ for a step by step guide on how to get started with the library on Raspberry Pi 3.

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

- Follow the steps to `configure the Actions Console project and the Google account <https://developers.google.com/assistant/sdk/guides/library/python/embed/config-dev-project-and-account>`_.
- Follow the steps to `register a new device model and download the client secrets file <https://developers.google.com/assistant/sdk/guides/library/python/embed/register-device>`_.
- Generate credentials using ``google-oauth-tool``.::

    pip install --upgrade google-auth-oauthlib[tool]
    google-oauthlib-tool --client-secrets path/to/client_secret_XXXXX.json --scope https://www.googleapis.com/auth/assistant-sdk-prototype --scope https://www.googleapis.com/auth/gcm --save --headless

Usage
-----

- Run the demo::

    google-assistant-demo

- Say "Ok Google" or "Hey Google" followed by a voice query. The demo should
  play back the Assistant's response and log events to the screen.

- Register the device and run the demo with device actions::

    google-assistant-demo --project-id PROJECT_ID --device-model-id DEVICE_MODEL

Reference
---------

- `Reference sample`_ for the Google Assistant Library for Python
- `Google Assistant Library`_ reference

License
-------

See `LICENSE`_ and `LICENSE.third_party`_.

.. _Python: https://www.python.org/
.. _Google Assistant Library: https://developers.google.com/assistant/sdk/reference/library/python
.. _Google Assistant SDK for devices: https://developers.google.com/assistant/sdk
.. _Introduction to the Google Assistant Library: https://developers.google.com/assistant/sdk/guides/library/python
.. _pip: https://pip.pypa.io/
.. _GitHub releases page: https://github.com/googlesamples/assistant-sdk-python/releases
.. _LICENSE: https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-library/LICENSE
.. _LICENSE.third_party: https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-library/LICENSE.third_party
.. _google/assistant/library/LICENSE.third_party: https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-library/google/assistant/library/LICENSE.third_party
.. _Reference sample: https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-sdk/googlesamples/assistant/library
