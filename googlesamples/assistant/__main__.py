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
import logging
import tqdm
from six.moves import input

from . import (embedded_assistant,
               audio_helpers,
               auth_helpers)

EPILOG = """examples:
  # Authorize the sample to access the Embedded Assistant API:
  python -m googlesamples.assistant --authorize /path/to/client_secret.json

  # Run the sample with microphone input and speaker output.
  python -m googlesamples.assistant

  # Run the sample with file input and speaker output.
  python -m googlesamples.assistant -i query.riff

  # Run the sample with file input and output.
  python -m googlesamples.assistant -i query.riff -o response.riff
"""

ASSISTANT_OAUTH_SCOPE = 'https://www.googleapis.com/auth/assistant'
ASSISTANT_API_ENDPOINTS = {
    'deprecated': 'internal-assistant-api',
    'dev': 'internal-assistant-api',
}


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=EPILOG)
    # TODO(proppy): refactor flag documentation
    parser.add_argument('--authorize', type=str,
                        metavar='CLIENT_SECRET_JSON_FILE', default=None,
                        help='Initialize the embedded assistant credentials. '
                        'If missing, existing credentials will be used.')
    parser.add_argument('-i', '--input_audio_file', type=str, default=None,
                        help='Path to input audio file. '
                        'If missing, uses pyaudio capture')
    parser.add_argument('-o', '--output_audio_file', type=str, default=None,
                        help='Path to output audio file. '
                        'If missing, uses pyaudio playback')
    parser.add_argument('--api_endpoint', type=str, default='deprecated',
                        help='Name or address of Embedded Assistant API '
                        'service.')
    parser.add_argument('--credentials', type=str,
                        metavar='OAUTH2_CREDENTIALS_FILE',
                        default='.embedded_assistant_credentials.json',
                        help='Path to store and read OAuth2 credentials '
                        'generated with the `--authorize` flag.')
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

    if args.authorize:
        # In Authorize mode:
        # - Start an interactive OAuth2 authorization flow.
        # - Save new OAuth2 credentials locally.
        # - Exit.
        credentials = auth_helpers.credentials_flow_interactive(
            args.authorize, scopes=[ASSISTANT_OAUTH_SCOPE])
        auth_helpers.save_credentials(args.credentials, credentials)
        logging.info('OAuth credentials initialized: %s', args.credentials)
        logging.info('Run the sample without the `--authorize` flag '
                     'to start the embedded assistant')
        return

    try:
        credentials = auth_helpers.load_credentials(
            args.credentials, scopes=[ASSISTANT_OAUTH_SCOPE])
    except Exception as e:
        logging.error('Error loading credentials: %s', e)
        logging.error('Run the sample with the `--authorize` flag '
                      'to initialize new OAuth2 credentials.')
        return

    endpoint = ASSISTANT_API_ENDPOINTS.get(args.api_endpoint,
                                           args.api_endpoint)
    grpc_channel = auth_helpers.create_grpc_channel(
        endpoint, credentials,
        ssl_credentials_file=args.ssl_credentials_for_testing,
        grpc_channel_options=args.grpc_channel_option)
    logging.info('Connecting to %s', endpoint)

    # Start the Embedded Assistant API client.
    assistant = embedded_assistant.EmbeddedAssistant(grpc_channel,
                                                     credentials=credentials)

    def iter_with_progress(title, gen):
        with tqdm.tqdm(unit='B', unit_scale=True, position=0) as t:
            t.set_description(title)
            for d in gen:
                t.update(len(d))
                yield d

    interactive = not (args.input_audio_file or args.output_audio_file)
    if interactive:
        # In interactive mode:
        # - Read audio samples from microphone.
        # - Send converse request.
        # - Wait for END_OF_UTTERANCE (This is optional).
        # - Iterate on converse responses audio data and playback samples.
        while True:
            audio_stream = audio_helpers.PyAudioStream()
            input_samples = iter_with_progress('Recording: ', audio_stream)
            # TODO(proppy): wait for input at the beginning of the loop.
            input('Press Enter to start a new conversation ')
            converse_responses = assistant.converse(input_samples)
            assistant.wait_end_of_utterance(converse_responses)
            print('End of utterance detected.')
            output_samples = assistant.iter_converse_responses_audio(
                converse_responses)
            for s in iter_with_progress('Playing', output_samples):
                audio_stream.write(s)
            audio_stream.close()
    else:
        # In non-interactive mode:
        # - Read audio samples from microphone.
        # - Send converse request.
        # - Wait for END_OF_UTTERANCE (This is optional).
        # - Iterate on converse responses audio data and playback samples.
        if args.input_audio_file:
            input_stream = audio_helpers.SampleRateLimiter(
                open(args.input_audio_file, 'rb'))
        else:
            input_stream = audio_helpers.PyAudioStream()
        if args.output_audio_file:
            output_stream = audio_helpers.WaveStreamWriter(
                open(args.output_audio_file, 'wb'))
        else:
            output_stream = audio_helpers.PyAudioStream()
        # Read audio sample from input stream.
        input_samples = iter_with_progress('Recording: ', input_stream)
        converse_responses = assistant.converse(input_samples)
        output_samples = assistant.iter_converse_responses_audio(
            converse_responses)
        for s in iter_with_progress('Playing ', output_samples):
            output_stream.write(s)
        input_stream.close()
        output_stream.close()


if __name__ == '__main__':
    main()
