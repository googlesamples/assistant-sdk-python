Changelog
=========

0.3.2
--------
- Bump urllib3 dependency.


0.3.1
--------
- Bump dependencies to use new ``google-assistant-grpc`` package (faster install).


0.3.0
-----
- Move grpc bindings to the `google-assistant-grpc <https://pypi.python.org/pypi/google-assistant-grpc>`_ package.
- Moved reference grpc sample to ``googlesamples.assistant.grpc.pushtotalk`` with `updated instructions <https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-sdk/googlesamples/assistant/grpc>`_.
- Replaced ``auth_helpers`` with ``google-oauthlibtool``:

  - Follow the `updated instructions <https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-grpc#authorization>`_ to generate and use new credentials.

- Add ``--once`` flag to pushtotalk grpc sample (@r-clancy).
- Fix typo in IFTTT handling in pushtotalk grpc sample (@kadeve).
- Add ``google-assistant-library`` package `installation instructions <https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-library>`_ and `sample <https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-sdk/googlesamples/assistant/library>`_. 


0.2.1
-----
- Fix audio helpers.


0.2.0
-----
- Add basic travis config.
- Add retry logic.
- Implement volume control.


0.1.0
-----
- Initial release.
