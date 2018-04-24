# Copyright (C) 2018 Google Inc.
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

"""Simple file-based sample for the Google Assistant Service."""

import json
import logging
import os
import os.path
import sys

import click
import google.auth.transport.grpc
import google.auth.transport.requests
import google.oauth2.credentials

from google.assistant.embedded.v1alpha2 import (
    embedded_assistant_pb2,
    embedded_assistant_pb2_grpc
)


END_OF_UTTERANCE = embedded_assistant_pb2.AssistResponse.END_OF_UTTERANCE


@click.command()
@click.option('--api-endpoint', default='embeddedassistant.googleapis.com',
              metavar='<api endpoint>', show_default=True,
              help='Address of Google Assistant API service.')
@click.option('--credentials',
              metavar='<credentials>', show_default=True,
              default=os.path.join(click.get_app_dir('google-oauthlib-tool'),
                                   'credentials.json'),
              help='Path to read OAuth2 credentials.')
@click.option('--device-model-id', required=True,
              metavar='<device model id>',
              help='Unique device model identifier.')
@click.option('--device-id', required=True,
              metavar='<device id>',
              help='Unique registered device instance identifier.')
@click.option('--lang', show_default=True,
              metavar='<language code>',
              default='en-US',
              help='Language code of the Assistant.')
@click.option('--verbose', '-v', is_flag=True, default=False,
              help='Enable verbose logging.')
@click.option('--input-audio-file', '-i', required=True,
              metavar='<input file>', type=click.File('rb'),
              help='Path to input audio file (format: LINEAR16 16000 Hz).')
@click.option('--output-audio-file', '-o', required=True,
              metavar='<output file>', type=click.File('wb'),
              help='Path to output audio file (format: LINEAR16 16000 Hz).')
@click.option('--block-size', default=1024,
              metavar='<block size>', show_default=True,
              help='Size of each input stream read in bytes.')
@click.option('--grpc-deadline', default=300,
              metavar='<grpc deadline>', show_default=True,
              help='gRPC deadline in seconds')
def main(api_endpoint, credentials,
         device_model_id, device_id, lang, verbose,
         input_audio_file, output_audio_file,
         block_size, grpc_deadline, *args, **kwargs):
    """File based sample for the Google Assistant API.

    Examples:
      $ python -m audiofileinput -i <input file> -o <output file>
    """
    # Setup logging.
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)

    # Load OAuth 2.0 credentials.
    try:
        with open(credentials, 'r') as f:
            credentials = google.oauth2.credentials.Credentials(token=None,
                                                                **json.load(f))
            http_request = google.auth.transport.requests.Request()
            credentials.refresh(http_request)
    except Exception as e:
        logging.error('Error loading credentials: %s', e)
        logging.error('Run google-oauthlib-tool to initialize '
                      'new OAuth 2.0 credentials.')
        sys.exit(-1)

    # Create an authorized gRPC channel.
    grpc_channel = google.auth.transport.grpc.secure_authorized_channel(
        credentials, http_request, api_endpoint)
    logging.info('Connecting to %s', api_endpoint)

    # Create gRPC stubs
    assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(grpc_channel)

    # Generate gRPC requests.
    def gen_assist_requests(input_stream):
        dialog_state_in = embedded_assistant_pb2.DialogStateIn(
            language_code=lang,
            conversation_state=b''
        )
        config = embedded_assistant_pb2.AssistConfig(
            audio_in_config=embedded_assistant_pb2.AudioInConfig(
                encoding='LINEAR16',
                sample_rate_hertz=16000,
            ),
            audio_out_config=embedded_assistant_pb2.AudioOutConfig(
                encoding='LINEAR16',
                sample_rate_hertz=16000,
                volume_percentage=100,
            ),
            dialog_state_in=dialog_state_in,
            device_config=embedded_assistant_pb2.DeviceConfig(
                device_id=device_id,
                device_model_id=device_model_id,
            )
        )
        # Send first AssistRequest message with configuration.
        yield embedded_assistant_pb2.AssistRequest(config=config)
        while True:
            # Read user request from file.
            data = input_stream.read(block_size)
            if not data:
                break
            # Send following AssitRequest message with audio chunks.
            yield embedded_assistant_pb2.AssistRequest(audio_in=data)

    for resp in assistant.Assist(gen_assist_requests(input_audio_file),
                                 grpc_deadline):
        # Iterate on AssistResponse messages.
        if resp.event_type == END_OF_UTTERANCE:
            logging.info('End of audio request detected')
        if resp.speech_results:
            logging.info('Transcript of user request: "%s".',
                         ' '.join(r.transcript
                                  for r in resp.speech_results))
        if len(resp.audio_out.audio_data) > 0:
            # Write assistant response to supplied file.
            output_audio_file.write(resp.audio_out.audio_data)
        if resp.dialog_state_out.supplemental_display_text:
            logging.info('Assistant display text: "%s"',
                         resp.dialog_state_out.supplemental_display_text)
        if resp.device_action.device_request_json:
            device_request = json.loads(resp.device_action.device_request_json)
            logging.info('Device request: %s', device_request)


if __name__ == '__main__':
    main()
