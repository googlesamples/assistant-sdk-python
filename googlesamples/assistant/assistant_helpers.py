# Copyright (C) 2017 Google Inc.
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

"""Helper functions for the Google Assistant API."""

import logging

from google.assistant.embedded.v1alpha1 import embedded_assistant_pb2


END_OF_UTTERANCE = embedded_assistant_pb2.ConverseResponse.END_OF_UTTERANCE


def log_converse_request_without_audio(converse_request):
    """Log ConverseRequest fields without audio data."""
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        resp_copy = embedded_assistant_pb2.ConverseRequest()
        resp_copy.CopyFrom(converse_request)
        if len(resp_copy.audio_in) > 0:
            size = len(resp_copy.audio_in)
            resp_copy.ClearField('audio_in')
            logging.debug('ConverseRequest: audio_in (%d bytes)',
                          size)
            return
        logging.debug('ConverseRequest: %s', resp_copy)


def log_converse_response_without_audio(converse_response):
    """Log ConverseResponse fields without audio data."""
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        resp_copy = embedded_assistant_pb2.ConverseResponse()
        resp_copy.CopyFrom(converse_response)
        has_audio_data = (resp_copy.HasField('audio_out') and
                          len(resp_copy.audio_out.audio_data) > 0)
        if has_audio_data:
            size = len(resp_copy.audio_out.audio_data)
            resp_copy.audio_out.ClearField('audio_data')
            if resp_copy.audio_out.ListFields():
                logging.debug('ConverseResponse: %s audio_data (%d bytes)',
                              resp_copy,
                              size)
            else:
                logging.debug('ConverseResponse: audio_data (%d bytes)',
                              size)
            return
        logging.debug('ConverseResponse: %s', resp_copy)


def gen_converse_requests(samples,
                          sample_rate,
                          conversation_state=None,
                          volume_percentage=50):
    """Returns a generator of ConverseRequest proto messages from the
       given audio samples.

    Args:
      samples: generator of audio samples.
      sample_rate: audio data sample rate in hertz.
      conversation_state: opaque bytes describing current conversation state.
    """
    audio_in_config = embedded_assistant_pb2.AudioInConfig(
        encoding='LINEAR16',
        sample_rate_hertz=int(sample_rate),
    )
    audio_out_config = embedded_assistant_pb2.AudioOutConfig(
        encoding='LINEAR16',
        sample_rate_hertz=int(sample_rate),
        volume_percentage=volume_percentage,
    )
    state_config = None
    if conversation_state:
        logging.debug('Sending converse_state: %s', conversation_state)
        state_config = embedded_assistant_pb2.ConverseState(
            conversation_state=conversation_state,
        )
    converse_config = embedded_assistant_pb2.ConverseConfig(
        audio_in_config=audio_in_config,
        audio_out_config=audio_out_config,
        converse_state=state_config,
    )
    # The first ConverseRequest must contain the ConverseConfig
    # and no audio data
    yield embedded_assistant_pb2.ConverseRequest(config=converse_config)
    for data in samples:
        # Subsequent requests need audio data, but not config.
        yield embedded_assistant_pb2.ConverseRequest(audio_in=data)
