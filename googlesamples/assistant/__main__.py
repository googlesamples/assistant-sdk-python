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

from . import (embedded_assistant,
               audio_helpers,
               auth_helpers,
               recommended_settings)

EPILOG = """examples:
  # embedded_assistant.py --authorize /path/to/client_secret.json
  Initialize new OAuth2 credentials with the given client secret file:
  (can be downloaded from the API Manager in Google Developers console)
  - start an interactive OAuth2 authorization flow
  - save new OAuth2 credentials locally
  (location can be specified with the --credentials flag)
  - exit

  # embedded_assistant.py
  Run the Embedded Assistant sample with microphone input:
  - use the credentials created with the --authorize flag
  - record voice query from microphone
  - play assistant response on speaker
  - exit

  # embedded_assistant.py -i /path/to/query.riff
  Run the Embedded Assistant sample with file input:
  - use the credentials created with the --authorize flag
  - read voice query from the given file
  (using the -i flag)
  - play assistant response on speaker
  - exit
"""


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
    parser.add_argument('--credentials', type=str,
                        metavar='OAUTH2_CREDENTIALS_FILE',
                        default='.embedded_assistant_credentials.json',
                        help='Path to store and read OAuth2 credentials '
                        'generated with the `--authorize` flag.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose logging.')
    args = parser.parse_args()

    # Setup logging.
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Get assistant API credentials.
    if args.authorize:
        credentials = auth_helpers.credentials_flow_interactive(
            args.authorize,
            scopes=[embedded_assistant.ASSISTANT_SCOPE])
        auth_helpers.save_credentials(args.credentials, credentials)
        logging.info('OAuth credentials initialized: %s', args.credentials)
        logging.info('Run the sample without the `--authorize` flag '
                     'to start the embedded assistant')
        return

    try:
        credentials = auth_helpers.load_credentials(
            args.credentials,
            scopes=[embedded_assistant.ASSISTANT_SCOPE])
    except Exception as e:
        logging.error('Error loading credentials: %s', e)
        logging.error('Run the sample with the `--authorize` flag '
                      'to initialize new OAuth2 credentials.')
        return

    # Setup audio input stream.
    if args.input_audio_file:
        input_stream = audio_helpers.SampleRateLimiter(
            open(args.input_audio_file, 'rb'),
            recommended_settings.AUDIO_SAMPLE_RATE,
            recommended_settings.AUDIO_BYTES_PER_SAMPLE)
    else:
        input_stream = audio_helpers.SharedAudioStream(
            recommended_settings.AUDIO_SAMPLE_RATE,
            recommended_settings.AUDIO_BYTES_PER_SAMPLE,
            recommended_settings.AUDIO_CHUNK_BYTES)

    # Setup audio output stream.
    if args.output_audio_file:
        output_stream = audio_helpers.WaveStreamWriter(
            open(args.output_audio_file, 'wb'),
            recommended_settings.AUDIO_SAMPLE_RATE,
            recommended_settings.AUDIO_BYTES_PER_SAMPLE)
    else:
        output_stream = audio_helpers.SharedAudioStream(
            recommended_settings.AUDIO_SAMPLE_RATE,
            recommended_settings.AUDIO_BYTES_PER_SAMPLE,
            recommended_settings.AUDIO_CHUNK_BYTES)

    # Start the Embedded Assistant API client.
    assistant = embedded_assistant.EmbeddedAssistant(credentials,
                                                     endpoint='deprecated')

    def iter_with_progress(title, gen):
        with tqdm.tqdm(unit='B', unit_scale=True, position=0) as t:
            t.set_description(title)
            for d in gen:
                t.update(len(d))
                yield d

    request_samples = iter(lambda: input_stream.read(
        recommended_settings.AUDIO_CHUNK_BYTES), '')
    request_samples = iter_with_progress('Recording: ', request_samples)
    response_samples = assistant.converse(request_samples)
    next(response_samples)  # wait for end of utterance
    for s in iter_with_progress('Playing ', response_samples):
        output_stream.write(s)

    input_stream.close()
    output_stream.close()


if __name__ == '__main__':
    main()
