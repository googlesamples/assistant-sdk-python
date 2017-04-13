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

from google.rpc import code_pb2

from . import embedded_assistant_pb2
from .recommended_settings import AUDIO_SAMPLE_RATE_HZ, DEADLINE_SECS

END_OF_UTTERANCE = embedded_assistant_pb2.ConverseResponse.END_OF_UTTERANCE


class EmbeddedAssistant(object):
    """Example client for the gRPC Google Assistant API.
    Args:
      grpc_channel(grpc.Channel): gRPC channel via which to send
        Google Assistant API RPC requests.
    """
    def __init__(self, grpc_channel):
        self._service = embedded_assistant_pb2.EmbeddedAssistantStub(
            grpc_channel)
        # We set this Event when the server tells us to stop sending audio.
        self._stop_sending_audio = threading.Event()
        # We set this Event when it is safe to play audio.
        self._start_playback = threading.Event()
        # Stores an opaque blob provided in ConverseResponse that,
        # when provided in a follow-up ConverseRequest,
        # gives the Assistant a context marker within the current state
        # of the multi-Converse()-RPC "conversation".
        # This value, along with MicrophoneMode, supports a more natural
        # "conversation" with the Assistant.
        self._converse_state = b''
        self._volume_percentage = 50

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
        # Google Assistant API.
        converse_requests = self._gen_converse_requests(iter(samples),
                                                        sample_rate)
        # This generator yields ConverseResponse proto messages
        # received from the gRPC Google Assistant API.
        converse_responses = self._service.Converse(converse_requests,
                                                    deadline)
        # Iterate over ConverseResponse proto messages and yield them
        # back to the caller.
        for resp in converse_responses:
            self._log_response_without_audio(resp)
            if resp.error.code != code_pb2.OK:
                raise RuntimeError('Server error: ' + resp.error.message)
            if resp.event_type == END_OF_UTTERANCE:
                logging.debug('server reported END_OF_UTTERANCE')
                self._stop_sending_audio.set()
            if len(resp.audio_out.audio_data) > 0:
                self._start_playback.wait()
            if resp.result.converse_state:
                logging.debug('Saving converse_state: %s',
                              resp.result.converse_state)
                self._converse_state = resp.result.converse_state
            if resp.audio_out.volume_percentage != self._volume_percentage:
                logging.info('Volume should be set to %s%%'
                             % self._volume_percentage)
                # NOTE: No volume change is currently implemented.
                self._volume_percentage = resp.audio_out.volume_percentage
            # yield ConverseResponse back to caller.
            yield resp

    @staticmethod
    def _log_response_without_audio(converse_response):
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            resp_copy = embedded_assistant_pb2.ConverseResponse()
            resp_copy.CopyFrom(converse_response)
            resp_copy.ClearField('audio_out')
            if resp_copy.ListFields():
                logging.debug('ConverseResponse (without audio): %s',
                              resp_copy)

    def _gen_converse_requests(self, samples, sample_rate):
        """Returns a generator of ConverseRequest proto messages from the
           given audio samples.

        Args:
          samples: generator of audio samples.
          sample_rate: audio data sample rate.
        """
        audio_in_config = embedded_assistant_pb2.AudioInConfig(
            encoding='LINEAR16',
            sample_rate_hertz=int(sample_rate),
        )
        audio_out_config = embedded_assistant_pb2.AudioOutConfig(
            encoding='LINEAR16',
            sample_rate_hertz=int(sample_rate),
            volume_percentage=self._volume_percentage,
        )
        state_config = None
        if self._converse_state:
            logging.debug('Sending converse_state: %s', self._converse_state)
            state_config = embedded_assistant_pb2.State(
                converse_state=self._converse_state,
            )
        converse_config = embedded_assistant_pb2.ConverseConfig(
            audio_in_config=audio_in_config,
            audio_out_config=audio_out_config,
            state=state_config,
        )
        # The first ConverseRequest must contain the ConverseConfig
        # and no audio data
        yield embedded_assistant_pb2.ConverseRequest(config=converse_config)
        while not self._stop_sending_audio.is_set():
            data = next(samples)
            # Subsequent requests need audio data, but not config.
            yield embedded_assistant_pb2.ConverseRequest(audio_in=data)
        self._start_playback.set()
