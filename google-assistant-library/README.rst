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

See `Getting Started with the Raspberry Pi and Python`_ for a step by step guide on how to get started with the library on Raspberry Pi 3.

Supported configuration
-----------------------

- Python ``>= 3.4``
- Architecture: ``linux-arm7l``

Installing
----------

- Download the latest ``linux_arm7l`` wheel for the ``google_assistant_library`` from the `GitHub releases page`_.
- Install the package and its dependencies using pip_::

    pip install --upgrade google_assistant_library-0.0.2-py2.py3-none-linux_armv7l.whl

Authorization
-------------

- `Follow the steps`_ to configure a Google API Console Project and a Google account to use with the Google Assistant SDK.

- Download the ``client_secret_XXXXX.json`` file from the `Google API Console Project credentials section`_ and generate credentials using ``google-oauth-tool``.::

    pip install --upgrade google-auth-oauthlib[tool]
    google-oauthlib-tool --client-secrets path/to/client_secret_XXXXX.json --scope https://www.googleapis.com/auth/assistant-sdk-prototype --save --headless

Usage
-----

- Run the demo::

    google-assistant-demo

- Say "Ok Google", followed by a voice query. The demo should
  play back the Assistant's response and log events to the screen.

Reference
---------

- `Reference sample`_ for the Google Assistant Library for Python
- `Google Assistant Library`_ reference

License
-------

See `LICENSE`_ and `LICENSE.third_party`_.

.. _Python: https://www.python.org/
.. _Google Assistant Library: https://developers.google.com/assistant/sdk/reference/library/
.. _Google Assistant SDK: https://developers.google.com/assistant/sdk
.. _Getting Started Guide for Raspberry Pi: https://developers.google.com/assistant/sdk/prototype/getting-started-pi-python/>
.. _pip: https://pip.pypa.io/
.. _GitHub releases page: https://github.com/googlesamples/assistant-sdk-python/releases
.. _Follow the steps: https://developers.google.com/assistant/sdk/prototype/getting-started-other-platforms/config-dev-project-and-account
.. _Google API Console Project credentials section: https://console.developers.google.com/apis/credentials
.. _LICENSE: https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-library/LICENSE
.. _google/assistant/library/LICENSE.third_party: https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-library/google/assistant/library/LICENSE.third_party
.. _sample: https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-sdk/googlesample/assistant/library
