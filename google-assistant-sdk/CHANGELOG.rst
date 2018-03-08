Changelog
=========

0.4.4
-----
- Fix DeviceHandler initialization issue.
- Add example action packages for custom device actions.
- Better feedback on device registration.


0.4.3
-----
- Fix Python 2.7/3.6 compatibility for ``pushtotalk`` and ``hotword`` sample.


0.4.2
-----
- Add client type for ``pushtotalk`` registration.


0.4.1
-----
- Update outdated ``hotword`` sample.


0.4.0
-----
- Add Device actions handling to samples.
- Update ``pushtotalk`` sample to ``v1alpha2`` of Google Assistant Service.
- Add language selection to ``pushtotalk`` sample.
- New ``textinput`` sample for the Google Assistant Service.
- New ``devicetool`` tool for device registration.


0.3.3
-----
- Update Google Assistant Library from 0.0.2 to 0.0.3


0.3.2
-----
- Bump urllib3 dependency.


0.3.1
-----
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
