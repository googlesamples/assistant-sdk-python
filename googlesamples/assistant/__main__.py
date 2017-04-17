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
"""Sample that implements GRPC client for Google Assistant API."""

import argparse
import logging
from six.moves import input

from google.assistant.v1alpha1 import embedded_assistant_pb2
from google.rpc import code_pb2

from . import (assistant_helpers,
               audio_helpers,
               auth_helpers)


EPILOG = """examples:
  # Run the sample with microphone input and speaker output.
  python -m googlesamples.assistant

  # Run the sample with file input and speaker output.
  python -m googlesamples.assistant -i query.riff

  # Run the sample with file input and output.
  python -m googlesamples.assistant -i query.riff -o response.riff
"""

ASSISTANT_OAUTH_SCOPE = 'https://www.googleapis.com/auth/assistant'
ASSISTANT_API_ENDPOINTS = {
    'prod': 'embeddedassistant.googleapis.com',
}
END_OF_UTTERANCE = embedded_assistant_pb2.ConverseResponse.END_OF_UTTERANCE
DIALOG_FOLLOW_ON = embedded_assistant_pb2.Result.DIALOG_FOLLOW_ON
CLOSE_MICROPHONE = embedded_assistant_pb2.Result.CLOSE_MICROPHONE


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EPILOG)
    # TODO(proppy): refactor flag documentation
    parser.add_argument('-i', '--input_audio_file', type=str, default=None,
                        help='Path to input audio file. '
                        'If missing, uses pyaudio capture')
    parser.add_argument('-o', '--output_audio_file', type=str, default=None,
                        help='Path to output audio file. '
                        'If missing, uses pyaudio playback')
    parser.add_argument('--api_endpoint', type=str, default='prod',
                        help='Name or address of Google Assistant API '
                        'service.')
    parser.add_argument('--credentials', type=str,
                        metavar='OAUTH2_CREDENTIALS_FILE',
                        default='.assistant_credentials.json',
                        help='Path to read OAuth2 credentials.')
    parser.add_argument('--ssl_credentials_for_testing',
                        type=str, default=None,
                        help='Path to ssl_certificates.pem; for testing only.')
    parser.add_argument('--grpc_channel_option', type=str, action='append',
                        help='Options used to construct gRPC channel', nargs=2,
                        default=[], metavar=('OPTION_NAME', 'OPTION_VALUE'))
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose logging.')
    args = parser.parse_args()

    # Setup logging.
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    try:
        credentials = auth_helpers.load_credentials(
            args.credentials, scopes=[ASSISTANT_OAUTH_SCOPE])
    except Exception as e:
        logging.error('Error loading credentials: %s', e)
        logging.error('Run auth_helpers to initialize new OAuth2 credentials.')
        return

    endpoint = ASSISTANT_API_ENDPOINTS.get(args.api_endpoint,
                                           args.api_endpoint)
    grpc_channel = auth_helpers.create_grpc_channel(
        endpoint, credentials,
        ssl_credentials_file=args.ssl_credentials_for_testing,
        grpc_channel_options=args.grpc_channel_option)
    logging.info('Connecting to %s', endpoint)

    # Start the Embedded Assistant API client.
    assistant = embedded_assistant_pb2.EmbeddedAssistantStub(grpc_channel)

    interactive = not (args.input_audio_file or args.output_audio_file)
    if interactive:
        # In interactive mode:
        # - Read audio samples from microphone.
        # - Send converse request.
        # - Iterate on converse responses audio data and playback samples.
        user_response_expected = False
        audio_stream = audio_helpers.SdAudioStream()
        # Stores an opaque blob provided in ConverseResponse that,
        # when provided in a follow-up ConverseRequest,
        # gives the Assistant a context marker within the current state
        # of the multi-Converse()-RPC "conversation".
        # This value, along with MicrophoneMode, supports a more natural
        # "conversation" with the Assistant.
        converse_state_bytes = None
        # Stores the current volument percentage.
        # Note: No volume change is currently implemented in this sample
        volume_percentage = 50
        while True:
            if not user_response_expected:
                input('Press Enter to send a new request. ')

            audio_stream.start()
            logging.info('Recording audio request.')

            # This generator yields ConverseRequest to send to the gRPC
            # Google Assistant API.
            converse_requests = assistant_helpers.gen_converse_requests(
                audio_stream,
                converse_state=converse_state_bytes,
                volume_percentage=volume_percentage
            )

            def iter_converse_requests():
                for c in converse_requests:
                    assistant_helpers.log_converse_request_without_audio(c)
                    yield c
                audio_stream.start_playback()

            # This generator yields ConverseResponse proto messages
            # received from the gRPC Google Assistant API.
            for resp in assistant.Converse(iter_converse_requests()):
                assistant_helpers.log_converse_response_without_audio(resp)
                if resp.error.code != code_pb2.OK:
                    logging.error('server error: %s', resp.error.message)
                    break
                if resp.event_type == END_OF_UTTERANCE:
                    logging.info('End of audio request detected')
                    audio_stream.stop_recording()
                if resp.result.spoken_request_text:
                    logging.info('Transcript of user request: "%s".',
                                 resp.result.spoken_request_text)
                    logging.info('Playing assistant response.')
                if len(resp.audio_out.audio_data) > 0:
                    audio_stream.write(resp.audio_out.audio_data)
                if resp.result.spoken_response_text:
                    logging.info(
                        'Transcript of TTS response '
                        '(only populated from IFTTT): "%s".',
                        resp.result.spoken_response_text)
                if resp.result.converse_state:
                    converse_state_bytes = resp.result.converse_state
                if resp.audio_out.volume_percentage != volume_percentage:
                    volume_percentage = resp.audio_out.volume_percentage
                    logging.info('Volume should be set to %s%%'
                                 % volume_percentage)
                if resp.result.microphone_mode == DIALOG_FOLLOW_ON:
                    user_response_expected = True
                    logging.info('Expecting follow-on query from user.')
                elif resp.result.microphone_mode == CLOSE_MICROPHONE:
                    user_response_expected = False
            if not user_response_expected:
                logging.info('Finished playing assistant response.')
            audio_stream.stop()
    else:
        # In non-interactive mode:
        # - Read audio samples from microphone.
        # - Send converse requests.
        # - Iterate on converse responses audio data and playback samples.
        if args.input_audio_file:
            input_stream = audio_helpers.SampleRateLimiter(
                open(args.input_audio_file, 'rb'))
        else:
            input_stream = audio_helpers.PyAudioStream(lock=False)
            input_stream.start()
        if args.output_audio_file:
            output_stream = audio_helpers.WaveStreamWriter(
                open(args.output_audio_file, 'wb'))
        else:
            output_stream = audio_helpers.PyAudioStream(lock=False)
            output_stream.start()

        converse_requests = assistant_helpers.gen_converse_requests(
            input_stream)
        # TODO(proppy): Converge non-interactive handling or split it.
        for resp in assistant.Converse(converse_requests):
            if resp.event_type == END_OF_UTTERANCE:
                logging.info('End of utterance detected')
            if len(resp.audio_out.audio_data) > 0:
                output_stream.write(resp.audio_out.audio_data)
        input_stream.close()
        output_stream.close()


if __name__ == '__main__':
    main()
