Google Assistant Service Bindings for Python
=============================================

This package contains the generated Python_ bindings for the `Google Assistant Service`_.
It is part of the `Google Assistant SDK`_.

This package should be compatible with POSIX platforms supporting gRPC_ and Python_.

.. _Python: https://www.python.org/
.. _gRPC: https://www.grpc.io
.. _Google Assistant Service: https://developers.google.com/assistant/sdk/guides/service/python/
.. _Google Assistant SDK: https://developers.google.com/assistant/sdk

Installing
----------

- You can install using `pip <https://pip.pypa.io/>`_.::

    pip install --upgrade google-assistant-grpc

Authorization
-------------

- `Follow the steps <https://developers.google.com/assistant/sdk/guides/service/python/embed/config-dev-project-and-account>`_ to configure a Google API Console Project and a Google account to use with the Google Assistant SDK.

- Download the ``client_secret_XXXXX.json`` file from the `Google API Console Project credentials section <https://console.developers.google.com/apis/credentials>`_ and generate credentials using ``google-oauth-tool``.::

    pip install --upgrade google-auth-oauthlib[tool]
    google-oauthlib-tool --client-secrets path/to/client_secret_XXXXX.json --scope https://www.googleapis.com/auth/assistant-sdk-prototype --save --headless

- Load the credentials using `google.oauth2.credentials <https://google-auth.readthedocs.io/en/latest/reference/google.oauth2.credentials.html>`_.::

    import io
    import google.oauth2.credentials

    with io.open('/path/to/credentials.json', 'r') as f:
        credentials = google.oauth2.credentials.Credentials(token=None,
                                                            **json.load(f))

- Initialize the gRPC channel using `google.auth.transport.grpc <https://google-auth.readthedocs.io/en/latest/reference/google.auth.transport.grpc.html>`_.

Usage
-----

- Initialize the gRPC stubs using ``google.assistant.embedded.v1alpha1.embedded_assistant_pb2_grpc``.::

    import google.assistant.embedded.v1alpha1.embedded_assistant_pb2_grpc
    assistant = embedded_assistant_pb2.EmbeddedAssistantStub(channel)

- Call the `Converse`_ streaming method. It takes a generator of `ConverseRequest`_ and returns a generator of `ConverseResponse`_.::

    converse_responses_generator = assistant.Converse(converse_requests_generator)
    start_acquiring_audio()

- Send a `ConverseRequest`_ message with audio configuration parameters followed by multiple outgoing `ConverseRequest`_ messages containing the audio data of the Assistant request.::

    import google.assistant.embedded.v1alpha1.embedded_assistant_pb2

    def generate_converse_requests():
        yield embedded_assistant_pb2.ConverseConfig(
            audio_in_config=embedded_assistant_pb2.AudioInConfig(
                encoding='LINEAR16',
                sample_rate_hertz=16000,
            ),
            audio_out_config=embedded_assistant_pb2.AudioOutConfig(
                encoding='LINEAR16',
                sample_rate_hertz=16000,
            ),
        )
        for data in acquire_audio_data():
            yield embedded_assistant_pb2.ConverseRequest(audio_in=data)

- Handle the incoming stream of `ConverseResponse`_ messages:

  - Stop recording when receiving a `ConverseResponse`_ with the `EventType`_ message set to ``END_OF_UTTERANCE``.
  - Get conversation metadata from the stream of `ConverseResponse`_ messages. (with the `ConverseResult`_ field set).
  - Extract the audio data of the Assistant response from the stream of `ConverseResponse`_ messages (with the `AudioOut`_ field set).

::

    for converse_response in converse_response_generator:
        if resp.event_type == END_OF_UTTERANCE:
           stop_acquiring_audio()
        if resp.result.spoken_request_text:
           print(resp.result.spoken_request_text)
        if len(resp.audio_out.audio_data) > 0:
           playback_audio_data(resp.audio_out.audio_data)


.. _Converse: https://developers.google.com/assistant/sdk/reference/rpc/google.assistant.embedded.v1alpha1#embeddedassistant
.. _ConverseRequest: https://developers.google.com/assistant/sdk/reference/rpc/google.assistant.embedded.v1alpha1#google.assistant.embedded.v1alpha1.ConverseRequest
.. _ConverseResponse: https://developers.google.com/assistant/sdk/reference/rpc/google.assistant.embedded.v1alpha1#google.assistant.embedded.v1alpha1.ConverseResponse
.. _EventType: https://developers.google.com/assistant/sdk/reference/rpc/google.assistant.embedded.v1alpha1#eventtype
.. _AudioOut: https://developers.google.com/assistant/sdk/reference/rpc/google.assistant.embedded.v1alpha1#google.assistant.embedded.v1alpha1.AudioOut
.. _ConverseResult: https://developers.google.com/assistant/sdk/reference/rpc/google.assistant.embedded.v1alpha1#converseresult

Reference
---------

- `gRPC reference sample <https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-sdk/googlesamples/assistant/grpc>`_.
- `Google Assistant Service reference <https://developers.google.com/assistant/sdk/reference/rpc/>`_.

For Maintainers
---------------

See `MAINTAINER.md <MAINTAINER.md>`_ for more documentation on the
development, maintainance and release of the Python package itself.

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
