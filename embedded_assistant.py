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

from __future__ import division

import argparse
import contextlib
try:
    # python 2.x
    from cStringIO import StringIO
except ImportError:
    # python 3.x
    from io import StringIO
import functools
import signal
import sys
import threading
import time

import google.auth
import google.auth.transport.grpc
import google.auth.transport.requests
import embedded_assistant_pb2
from google.rpc import code_pb2
from grpc.framework.interfaces.face import face
import pyaudio
from six.moves import queue

from auth_helpers import get_credentials_flow

# Audio recording parameters
INPUT_RATE = 16000
OUTPUT_RATE = 24000
CHUNK = int(INPUT_RATE / 10)  # 100ms

# The API has a streaming limit of 60 seconds of audio*, so keep the
# connection alive for that long, plus some more to give the API time to figure
# out the transcription.
# * https://g.co/cloud/speech/limits#content
DEADLINE_SECS = 60 * 3 + 5
SPEECH_SCOPE = 'https://www.googleapis.com/auth/cloud-platform'
ACTIONS_SCOPE = 'https://www.googleapis.com/auth/search-actions'


class read_stream_from_string(object):
    """A read-only stream sourced from a string"""

    def __init__(self, data):
        self._io = StringIO(data)

    def read(self, *args):
        return self._io.read(*args)


def read_audio_from_file(filename, rate, chunk, stop_sending_audio):
    # Yields bytearrays from file of chunk size at sample rate in Hz.
    # After end-of-file, yields zeroes until stop_sending_audio is set.
    # File must be LINEAR16 (raw, no header) mono, recorded at sample rate.
    with open(filename, 'rb') as f:
        while not stop_sending_audio.is_set():
            data = f.read(chunk)
            # If file ends with partial chunk, pad with zeroes.
            yield data + b'\x00' * (chunk - len(data))
            # Print an '.' for each frame sent. (Helps to illustrate
            # streaming.)
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(float(chunk) / float(rate))


def make_channel(host, port):
    """Creates a secure channel with auth credentials from the environment."""
    # Grab application default credentials from the environment
    credentials, _ = google.auth.default(scopes=[SPEECH_SCOPE])

    # Create a secure channel using the credentials.
    http_request = google.auth.transport.requests.Request()
    target = '{}:{}'.format(host, port)

    return google.auth.transport.grpc.secure_authorized_channel(
        credentials, http_request, target)


def _audio_data_generator(buff):
    """A generator that yields all available data in the given buffer.

    Args:
        buff - a Queue object, where each element is a chunk of data.
    Yields:
        A chunk of data that is the aggregate of all chunks of data in `buff`.
        The function will block until at least one data chunk is available.
    """
    stop = False
    while not stop:
        # Use a blocking get() to ensure there's at least one chunk of data.
        data = [buff.get()]

        # Now consume whatever other data's still buffered.
        while True:
            try:
                data.append(buff.get(block=False))
            except queue.Empty:
                break

        # `None` in the buffer signals that the audio stream is closed. Yield
        # the final bit of the buffer and exit the loop.
        if None in data:
            stop = True
            data.remove(None)

        yield b''.join(data)


def _fill_buffer(buff, in_data, frame_count, time_info, status_flags):
    """Continuously collect data from the audio stream, into the buffer."""
    buff.put(in_data)
    return None, pyaudio.paContinue


# [START audio_stream]
@contextlib.contextmanager
def record_or_read_audio(rate, chunk, stop_sending_audio, filename=None):
    """Opens a file or recording stream in a context manager."""
    if filename:
        print('Reading audio from file:', filename)
        yield read_audio_from_file(filename, rate, chunk, stop_sending_audio)
        return

    # Create a thread-safe buffer of audio data
    buff = queue.Queue()

    audio_interface = pyaudio.PyAudio()
    # For troubleshooting purposes, print out which input device PyAudio chose.
    print('PyAudio INPUT device: {}'.format(
        audio_interface.get_default_input_device_info()['name']))
    audio_stream = audio_interface.open(
        format=pyaudio.paInt16,
        # The API currently only supports 1-channel (mono) audio
        # https://goo.gl/z757pE
        channels=1, rate=rate,
        input=True, frames_per_buffer=chunk,
        # Run the audio stream asynchronously to fill the buffer object.
        # This is necessary so that the input device's buffer doesn't overflow
        # while the calling thread makes network requests, etc.
        stream_callback=functools.partial(_fill_buffer, buff),
    )

    print('---------- RECORDING STARTED ----------')

    yield _audio_data_generator(buff)

    audio_stream.stop_stream()
    audio_stream.close()
    # Signal the _audio_data_generator to finish
    buff.put(None)
    audio_interface.terminate()
    print('---------- RECORDING FINISHED ----------')
# [END audio_stream]


def request_stream(data_stream, rate, stop_sending_audio, token=''):
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
        sample_rate_hertz=rate,  # the rate in hertz
        # See http://g.co/cloud/speech/docs/languages
        # for a list of supported languages.
        language_code='en-US',  # a BCP-47 language tag
        auth_token=token,  # OAuth2 access token to use Assistant.
    )
    audio_out_config = embedded_assistant_pb2.AudioOutConfig(
        encoding='LINEAR16',  # raw 16-bit signed little-endian samples
        sample_rate_hertz=OUTPUT_RATE,  # the rate in hertz
        volume_percentage=50,
    )
    converse_config = embedded_assistant_pb2.ConverseConfig(
        audio_in_config=audio_in_config,
        audio_out_config=audio_out_config
    )

    yield embedded_assistant_pb2.ConverseRequest(config=converse_config)

    for data in data_stream:
        if stop_sending_audio.is_set():
            print('request stream stopping at request of server')
            break
        # Subsequent requests can all just have the content
        yield embedded_assistant_pb2.ConverseRequest(audio_in=data)


def listen_print_loop(recognize_stream, stop_sending_audio):
    """Iterates through server responses and prints them.

    The recognize_stream passed is a generator that will block until a response
    is provided by the server. When the transcription response comes, print it.
    """
    total_bytes = 0
    total_chunks = 0
    # Raspberry Pi headphone-jack audio-output may be choppy with
    # PyAudio and snd_bcm2835 if this value is too small.
    frames_per_buffer = OUTPUT_RATE
    audio_interface = pyaudio.PyAudio()
    # For troubleshooting purposes, print out which output device PyAudio
    # chose.
    print('PyAudio OUTPUT device: {}'.format(
        audio_interface.get_default_output_device_info()['name']))

    out_stream = audio_interface.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=OUTPUT_RATE,
        output=True,
        frames_per_buffer=frames_per_buffer
    )
    out_stream.start_stream()

    for resp in recognize_stream:
        if resp.error.code != code_pb2.OK:
            raise RuntimeError('Server error: ' + resp.error.message)

        if resp.event_type == 1:  # END_OF_UTTERANCE
            print('server reported END_OF_UTTERANCE')
            stop_sending_audio.set()

        if len(resp.assistant_text) > 0:
            print('assistant_text: ', resp.assistant_text)

        if len(resp.audio_out.audio_data) > 0:
            # This example plays audio bytes from the server as soon as the
            # bytes are received. This is a simple and naive approach; a better
            # approach might involve buffering some of the audio bytes based on
            # network speed and available memory.
            out_stream.write(resp.audio_out.audio_data)
            total_bytes += len(resp.audio_out.audio_data)
            total_chunks += 1
            # Print '*' for each frame received. (Helps illustrate streaming.)
            sys.stdout.write('*')
            sys.stdout.flush()

    # PyAudio sometimes chops off the end of the audio. As a workaround, we
    # add some silence to the end of the audio playback.
    out_stream.write(b'\x00' * frames_per_buffer * 2)

    print('')
    print('audio_out', total_bytes,
          'total bytes from', total_chunks, 'chunks.')

    out_stream.stop_stream()
    out_stream.close()
    audio_interface.terminate()


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
            scopes=[SPEECH_SCOPE, ACTIONS_SCOPE])
        # TODO(proppy): remove when gRPC authorization is implemented.
        access_token = credentials.token
    else:
        access_token = args.access_token

    # TODO(proppy): construct gRPC channel with credentials.
    service = embedded_assistant_pb2.EmbeddedAssistantStub(
        make_channel('internal-assistant-api', 443))

    # We set this Event when the server tells us to stop sending audio.
    stop_sending_audio = threading.Event()

    # For streaming audio from the microphone, there are three threads.
    # First, a thread that collects audio data as it comes in
    with record_or_read_audio(
            INPUT_RATE, CHUNK, stop_sending_audio,
            args.input_audio_file) as buffered_audio_data:
        # Second, a thread that sends requests with that data
        requests = request_stream(buffered_audio_data, INPUT_RATE,
                                  stop_sending_audio, token=access_token)
        # Third, a thread that listens for transcription responses
        recognize_stream = service.Converse(requests, DEADLINE_SECS)

        # Exit things cleanly on interrupt
        signal.signal(signal.SIGINT, lambda *_: recognize_stream.cancel())

        # Now, put the transcription responses to use.
        try:
            listen_print_loop(recognize_stream, stop_sending_audio)

            recognize_stream.cancel()
        except face.CancellationError:
            # This happens because of the interrupt handler
            pass


if __name__ == '__main__':
    main()
