Google Assistant gRPC API bindings for Python
=============================================

This repository contains the generated Python bindings for the `Google Assistant gRPC API <https://developers.google.com/assistant/sdk/reference/rpc/>`_.

It is part of the `Google Assistant SDK <https://developers.google.com/assistant/sdk>`_.

It should be compatible with any POSIX platform with Python.

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

- Install the latest ``google-assistant-grpc`` package from `PyPI <https://pypi.python.org/pypi>`_ with `pip <https://pip.pypa.io/>`_::

    pip install --upgrade google-assistant-grpc

Authorization
-------------

- Download the ``client_secret_XXXXX.json`` file from the `Google API Console Project credentials section <https://console.developers.google.com/apis/credentials>`_ and generate credentials using ``google-oauth-tool``.::

    pip install --upgrade google-auth-oauthlib[tool]
    google-oauthlib-tool --client-secrets path/to/client_secret_XXXXX.json --scope https://www.googleapis.com/auth/assistant-sdk-prototype --save

- Load the credentials using `google.oauth2.credentials <https://google-auth.readthedocs.io/en/latest/reference/google.oauth2.credentials.html>`_.

- Initialize the gRPC channel using `google.auth.transport.grpc <https://google-auth.readthedocs.io/en/latest/reference/google.auth.transport.grpc.html>`_.

Usage
-----

- Initialize the gRPC stubs using ``google.assistant.embedded.v1alpha1.embedded_assistant_pb2_grpc``.::

    import google.assistant.embedded.v1alpha1.embedded_assistant_pb2_grpc
    assistant = embedded_assistant_pb2.EmbeddedAssistantStub(channel)

- Call the `Converse`_ streaming method, it takes a generator of `ConverseRequest`_ and returns a generator of `ConverseResponse`_.::

    converse_responses_generator = assistant.Converse(converse_requests_generator)
    start_acquiring_audio()

- Send a `ConverseRequest`_ message with audio configuration followed by multiple outgoing `ConverseRequest`_ message with the audio data of the Assistant request.::

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
  - Extract audio data of the Assistant response from the stream of `ConverseResponse`_  with an `AudioOut`_ message set.
  - Get conversation metadata from the stream of `ConverseResponse`_ with `ConverseResult`_ message set.

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

- `gRPC reference sample <https://github.com/googlesamples/assistant-sdk-python/tree/master/samples/grpc>`_.
- `Google Assistant gRPC API reference <https://developers.google.com/assistant/sdk/reference/rpc/>`_.

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
