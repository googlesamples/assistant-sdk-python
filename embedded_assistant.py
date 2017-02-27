#!/usr/bin/python
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
"""Sample that implements GRPC client for Embedded Google Assistant API."""

import argparse
import signal
from six import print_
import sys
import threading

import google.auth
import google.auth.transport.grpc
import google.auth.transport.requests
import embedded_assistant_pb2
from google.rpc import code_pb2
from grpc.framework.interfaces.face import face
import pyaudio

from auth_helpers import get_credentials_flow
from audio_helpers import SampleRateLimiter

# Audio parameters
# Audio Input sample rate in Hertz.
AUDIO_INPUT_SAMPLE_RATE = 16000
# Audio Output sample rate in Hertz.
# Note: API supports higher freqs but using the same sample rate
# allows us to share the same audio stream for input and output.
# TODO(proppy): check error message when different sample rate returned.
AUDIO_OUTPUT_SAMPLE_RATE = 16000
# Audio sample size in bytes.
AUDIO_BYTES_PER_SAMPLE = 2
# Audio I/O chunk size in bytes.
AUDIO_CHUNK_BYTES = 1024

# The API has a streaming limit of 60 seconds of audio*, so keep the
# connection alive for that long, plus some more to give the API time to figure
# out the transcription.
# * https://g.co/cloud/speech/limits#content
DEADLINE_SECS = 60 * 3 + 5
ASSISTANT_SCOPE = 'https://www.googleapis.com/auth/assistant'


def make_channel(host, port):
    """Creates a secure channel with auth credentials from the environment."""
    # Grab application default credentials from the environment
    credentials, _ = google.auth.default(scopes=[ASSISTANT_SCOPE])

    # Create a secure channel using the credentials.
    http_request = google.auth.transport.requests.Request()
    target = '{}:{}'.format(host, port)

    return google.auth.transport.grpc.secure_authorized_channel(
        credentials, http_request, target)


def request_stream(input_stream, rate, chunk,
                   stop_sending_audio, start_playback, token=''):
    """Yields `ConverseRequest`s constructed from a recording audio
    stream.

    Args:
        data_stream: A generator that yields raw audio data to send.
        rate: The sampling rate in hertz.
        stop_sending_audio: A threading.Event that should be set once the
            server decides that we should stop sending input audio bytes.
        token: OAuth2 access token as from OAuth2 Playground
    """
    if not token:
        print('No access token provided; Assistant responses are disabled.')
    # The initial request must contain metadata about the stream, so the
    # server knows how to interpret it.
    audio_in_config = embedded_assistant_pb2.AudioInConfig(
        # There are a bunch of config options you can specify. See
        # https://goo.gl/KPZn97 for the full list.
        encoding='LINEAR16',  # raw 16-bit signed little-endian samples
        sample_rate_hertz=rate,  # the sample rate in hertz
        # See http://g.co/cloud/speech/docs/languages
        # for a list of supported languages.
        language_code='en-US',  # a BCP-47 language tag
        auth_token=token,  # OAuth2 access token to use Assistant.
    )
    audio_out_config = embedded_assistant_pb2.AudioOutConfig(
        encoding='LINEAR16',  # raw 16-bit signed little-endian samples
        sample_rate_hertz=AUDIO_OUTPUT_SAMPLE_RATE,  # the sample rate in hertz
        volume_percentage=50,
    )
    converse_config = embedded_assistant_pb2.ConverseConfig(
        audio_in_config=audio_in_config,
        audio_out_config=audio_out_config
    )

    yield embedded_assistant_pb2.ConverseRequest(config=converse_config)
    print('---------- RECORDING STARTED ----------')
    while not stop_sending_audio.is_set():
        data = input_stream.read(chunk)
        # Subsequent requests can all just have the content
        yield embedded_assistant_pb2.ConverseRequest(audio_in=data)
        sys.stdout.write('.')
        sys.stdout.flush()
    print('---------- RECORDING FINISHED ----------')
    start_playback.set()


def listen_print_loop(recognize_stream, audio_stream,
                      stop_sending_audio, start_playback):
    """Iterates through server responses and prints them.

    The recognize_stream passed is a generator that will block until a response
    is provided by the server. When the transcription response comes, print it.
    """
    total_bytes = 0
    total_chunks = 0

    for resp in recognize_stream:
        if resp.error.code != code_pb2.OK:
            raise RuntimeError('Server error: ' + resp.error.message)

        if resp.event_type == 1:  # END_OF_UTTERANCE
            print('server reported END_OF_UTTERANCE')
            stop_sending_audio.set()

        if len(resp.assistant_text) > 0:
            print('assistant_text: ', resp.assistant_text)

        if len(resp.audio_out.audio_data) > 0:
            start_playback.wait()
            # This example plays audio bytes from the server as soon as the
            # bytes are received. This is a simple and naive approach; a better
            # approach might involve buffering some of the audio bytes based on
            # network speed and available memory.
            audio_stream.write(resp.audio_out.audio_data)
            total_bytes += len(resp.audio_out.audio_data)
            total_chunks += 1
            # Print '*' for each frame received. (Helps illustrate streaming.)
            sys.stdout.write('*')
            sys.stdout.flush()

    print('')
    print('audio_out', total_bytes,
          'total bytes from', total_chunks, 'chunks.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('access_token', type=str, nargs='?', default='',
                        help='Access token from OAuth2 Playground. '
                        'If provided, enables Assistant audio responses. '
                        'If missing, no Assistant responses will be returned.')
    parser.add_argument('-s', '--client_secrets', type=str, default=None,
                        help='Path to the client secrets JSON file. '
                        'It can be downloaded from the API Manager section '
                        'of the Google Developers console. '
                        'If provided, starts on the appropriate flow '
                        'to acquire OAuth2 access tokens. '
                        'If missing, the `access_token` flag will be used '
                        'if present')
    parser.add_argument('-i', '--input_audio_file', type=str, default=None,
                        help='Path to input audio file. '
                        'If missing, uses pyaudio capture (usually a mic)')
    args = parser.parse_args()

    access_token = None
    if args.client_secrets:
        credentials = get_credentials_flow(
            args.client_secrets,
            scopes=[ASSISTANT_SCOPE])
        # TODO(proppy): remove when gRPC authorization is implemented.
        access_token = credentials.token
    else:
        access_token = args.access_token

    # TODO(proppy): construct gRPC channel with credentials.
    service = embedded_assistant_pb2.EmbeddedAssistantStub(
        make_channel('internal-assistant-api', 443))

    # We set this Event when the server tells us to stop sending audio.
    stop_sending_audio = threading.Event()
    # We set this Event when it is safe to play audio.
    start_playback = threading.Event()

    audio_interface = pyaudio.PyAudio()
    # For troubleshooting purposes, print out which input device PyAudio chose.
    print('PyAudio device: {}'.format(
        audio_interface.get_default_input_device_info()['name']))
    audio_stream = audio_interface.open(
        format=pyaudio.paInt16,
        # The API currently only supports 1-channel (mono) audio
        # https://goo.gl/z757pE
        channels=1,
        rate=AUDIO_INPUT_SAMPLE_RATE,
        frames_per_buffer=AUDIO_CHUNK_BYTES,
        input=True, output=True
    )

    input_stream = (SampleRateLimiter(open(args.input_audio_file, 'rb'),
                                      AUDIO_INPUT_SAMPLE_RATE,
                                      AUDIO_BYTES_PER_SAMPLE)
                    if args.input_audio_file
                    else audio_stream)
    # thread that sends requests with that data
    requests = request_stream(input_stream,
                              AUDIO_INPUT_SAMPLE_RATE, AUDIO_CHUNK_BYTES,
                              stop_sending_audio, start_playback,
                              token=access_token)
    # thread that listens for transcription responses
    recognize_stream = service.Converse(requests, DEADLINE_SECS)

    # Exit things cleanly on interrupt
    signal.signal(signal.SIGINT, lambda *_: recognize_stream.cancel())

    # Now, put the transcription responses to use.
    try:
        listen_print_loop(recognize_stream, audio_stream,
                          stop_sending_audio, start_playback)
        recognize_stream.cancel()
    except face.CancellationError:
        # This happens because of the interrupt handler
        pass

    input_stream.close()
    audio_interface.terminate()


if __name__ == '__main__':
    main()
