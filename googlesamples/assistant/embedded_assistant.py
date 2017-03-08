#
# Copyright (C) 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import threading

import google.auth
import google.auth.transport.grpc
import google.auth.transport.requests
import google.oauth2.credentials
from google.rpc import code_pb2
import grpc

from . import embedded_assistant_pb2
from .recommended_settings import AUDIO_SAMPLE_RATE_HZ, DEADLINE_SECS

END_OF_UTTERANCE = embedded_assistant_pb2.ConverseResponse.END_OF_UTTERANCE
# Embedded Assistant API scope.
ASSISTANT_SCOPE = 'https://www.googleapis.com/auth/assistant'
ASSISTANT_ENDPOINTS = {
    'deprecated': 'internal-assistant-api',
    'dev': 'internal-assistant-api'
}


class EmbeddedAssistant(object):
    """Example client for the gRPC Embedded Assistant API.
    Args:
      credentials(google.oauth2.credentials.Credentials): OAuth2 credentials.
      ssl_credentials_file(str): Path to SSL credentials.pem file (for testing).
      grpc_channel_options([(option_name, option_val)]): gRPC channel options.
    """
    def __init__(self, credentials, ssl_credentials_file=None,
                 grpc_channel_options=None, endpoint='dev'):
        # TODO(proppy): add a flag in __main__
        endpoint = ASSISTANT_ENDPOINTS.get(endpoint, endpoint)
        logging.info('Connecting to %s', endpoint)
        # TODO(proppy): remove when gRPC auth is activated.
        self._credentials = credentials
        http_request = google.auth.transport.requests.Request()
        # TODO(dakota): Move the ssl_credentials stuff to auth_helpers.
        ssl_credentials = None
        if ssl_credentials_file:
            with open(ssl_credentials_file) as f:
                ssl_credentials = grpc.ssl_channel_credentials(f.read())
        channel = google.auth.transport.grpc.secure_authorized_channel(
            credentials, http_request, endpoint,
            ssl_credentials=ssl_credentials, options=grpc_channel_options or [])
        self._service = embedded_assistant_pb2.EmbeddedAssistantStub(channel)
        # We set this Event when the server tells us to stop sending audio.
        self._stop_sending_audio = threading.Event()
        # We set this Event when it is safe to play audio.
        self._start_playback = threading.Event()

    def converse(self, samples):
        """Start a converse request with the assistant

        - Send audio samples for the assistant query.
        - Yield an empty string when end of enturrance is reached.
        - Then Yield the assistant answer audio samples.

        Args:
          requests: generator of audio sample data to send as
            ConverseRequest proto messages.
        Returns: generator of audio sample data received from
          Converseresponse proto messages.
        """
        self._stop_sending_audio.clear()
        self._start_playback.clear()
        # This generator yields ConverseRequest to send to the gRPC
        # Embedded Assistant API.
        requests = self._generate_converse_requests(samples,
                                                    AUDIO_SAMPLE_RATE_HZ)
        # This generator yields ConverseResponse proto messages from
        # the gRPC Embedded Assistant API.
        converse_responses = self._service.Converse(requests,
                                                    DEADLINE_SECS)

        for resp in converse_responses:
            if resp.error.code != code_pb2.OK:
                raise RuntimeError('Server error: ' + resp.error.message)
            if resp.event_type == END_OF_UTTERANCE:
                logging.debug('server reported END_OF_UTTERANCE')
                self._stop_sending_audio.set()
                # notify caller we reached END_OF_UTTERANCE.
                yield ''
            if len(resp.audio_out.audio_data) > 0:
                self._start_playback.wait()
                # yield assistant response audio samples back to caller.
                yield resp.audio_out.audio_data

    def _generate_converse_requests(self, samples, sample_rate):
        """Returns a generator of ConverseRequest proto messages from the
           given audio samples.

        Args:
          samples: generator of audio samples.
          sample_rate: audio data sample rate.
        """
        # TODO(proppy): remove when gRPC auth is activated.
        http_request = google.auth.transport.requests.Request()
        self._credentials.refresh(http_request)
        access_token = self._credentials.token

        audio_in_config = embedded_assistant_pb2.AudioInConfig(
            encoding='LINEAR16',
            sample_rate_hertz=int(sample_rate),
            language_code='en-US',
            auth_token=access_token,
        )
        audio_out_config = embedded_assistant_pb2.AudioOutConfig(
            encoding='LINEAR16',
            sample_rate_hertz=int(sample_rate),
            volume_percentage=50,
        )
        converse_config = embedded_assistant_pb2.ConverseConfig(
            audio_in_config=audio_in_config,
            audio_out_config=audio_out_config
        )
        # The first ConverseRequest must contain the ConverseConfig
        # and no audio data
        yield embedded_assistant_pb2.ConverseRequest(config=converse_config)
        while not self._stop_sending_audio.is_set():
            data = next(samples)
            # Subsequent requests need audio data, but not config.
            yield embedded_assistant_pb2.ConverseRequest(audio_in=data)
        self._start_playback.set()
