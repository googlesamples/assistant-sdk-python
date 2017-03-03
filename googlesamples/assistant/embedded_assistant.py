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

from . import embedded_assistant_pb2
from .recommended_settings import AUDIO_SAMPLE_RATE_HZ, DEADLINE_SECS

END_OF_UTTERANCE = embedded_assistant_pb2.ConverseResponse.END_OF_UTTERANCE


class EmbeddedAssistant(object):
    """Example client for the gRPC Embedded Assistant API.
    Args:
      grpc_channel(grpc.Channel): gRPC channel via which to send
        Embedded Assistant API RPC requests.
      credentials(google.oauth2.credentials.Credentials): OAuth2 credentials.
    """
    def __init__(self, grpc_channel, credentials=None):
        # TODO(proppy): remove when gRPC auth is activated.
        self._credentials = credentials
        self._service = embedded_assistant_pb2.EmbeddedAssistantStub(
            grpc_channel)
        # We set this Event when the server tells us to stop sending audio.
        self._stop_sending_audio = threading.Event()
        # We set this Event when it is safe to play audio.
        self._start_playback = threading.Event()

    def converse(self, samples, sample_rate=AUDIO_SAMPLE_RATE_HZ,
                 deadline=DEADLINE_SECS):
        """Send ConverseRequests to the assistant

        Args:
          samples: generator of audio sample data to send as
            ConverseRequest proto messages.
          sample_rate: sample rate in hertz of the audio data.
          deadline: gRPC deadline in seconds.
        Returns: generator of ConverseResponse proto messages.
        """
        self._stop_sending_audio.clear()
        self._start_playback.clear()

        # This generator yields ConverseRequest to send to the gRPC
        # Embedded Assistant API.
        converse_requests = self._gen_converse_requests(samples, sample_rate)
        # This generator yields ConverseResponse proto messages
        # received from the gRPC Embedded Assistant API.
        converse_responses = self._service.Converse(converse_requests,
                                                    deadline)
        # Iterate over ConverseResponse proto messages and yield them
        # back to the caller.
        for resp in converse_responses:
            if resp.error.code != code_pb2.OK:
                raise RuntimeError('Server error: ' + resp.error.message)
            if resp.event_type == END_OF_UTTERANCE:
                logging.debug('server reported END_OF_UTTERANCE')
                self._stop_sending_audio.set()
            if len(resp.audio_out.audio_data) > 0:
                self._start_playback.wait()
                # yield assistant response audio samples back to caller.
            yield resp

    def _gen_converse_requests(self, samples, sample_rate):
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

    def wait_end_of_utterance(self, converse_responses):
        """Helper to iterate on converse responses until END_OF_UTTERANCE.

        Usage of this helper is optional and client code can also
        iterate on the ConverseResponse returned by `converse()` for
        more control.

        Args: generator of ConverseResponse proto messages returned by
          `converse()`.
        """
        for resp in converse_responses:
            if resp.event_type == END_OF_UTTERANCE:
                break

    @staticmethod
    def iter_converse_responses_audio(converse_responses):
        """Helper to iterate on audio samples in converse responses.

        Usage of this helper is optional and client code can also
        iterate on the ConverseResponse returned by `converse()` for
        more control.

        Args: generator of ConverseResponse proto messages.
        Returns: generator of audio samples.

        """
        for resp in converse_responses:
            if len(resp.audio_out.audio_data) > 0:
                yield resp.audio_out.audio_data
