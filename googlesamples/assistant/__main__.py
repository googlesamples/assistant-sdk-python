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

"""Sample that implements gRPC client for Google Assistant API."""

import logging
import os.path

import click
from google.assistant.embedded.v1alpha1 import embedded_assistant_pb2
from google.rpc import code_pb2

from . import (
    assistant_helpers,
    audio_helpers,
    auth_helpers,
    common_settings
)

ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'
END_OF_UTTERANCE = embedded_assistant_pb2.ConverseResponse.END_OF_UTTERANCE
DIALOG_FOLLOW_ON = embedded_assistant_pb2.ConverseResult.DIALOG_FOLLOW_ON
CLOSE_MICROPHONE = embedded_assistant_pb2.ConverseResult.CLOSE_MICROPHONE


@click.command()
@click.option('--api-endpoint', default=ASSISTANT_API_ENDPOINT,
              metavar='<api endpoint>', show_default=True,
              help='Address of Google Assistant API service.')
@click.option('--credentials',
              metavar='<credentials>', show_default=True,
              default=os.path.join(
                  click.get_app_dir(common_settings.ASSISTANT_APP_NAME),
                  common_settings.ASSISTANT_CREDENTIALS_FILENAME
              ),
              help='Path to read OAuth2 credentials.')
@click.option('--verbose', '-v', is_flag=True, default=False,
              help='Verbose logging.')
@click.option('--input-audio-file', '-i',
              metavar='<input file>',
              help='Path to input audio file. '
              'If missing, uses audio capture')
@click.option('--output-audio-file', '-o',
              metavar='<output file>',
              help='Path to output audio file. '
              'If missing, uses audio playback')
@click.option('--audio-sample-rate',
              default=common_settings.DEFAULT_AUDIO_SAMPLE_RATE,
              metavar='<audio sample rate>', show_default=True,
              help='Audio sample rate in hertz.')
@click.option('--audio-sample-width',
              default=common_settings.DEFAULT_AUDIO_SAMPLE_WIDTH,
              metavar='<audio sample width>', show_default=True,
              help='Audio sample width in bytes.')
@click.option('--audio-iter-size',
              default=common_settings.DEFAULT_AUDIO_ITER_SIZE,
              metavar='<audio iter size>', show_default=True,
              help='Size of each read during audio stream iteration in bytes.')
@click.option('--audio-block-size',
              default=common_settings.DEFAULT_AUDIO_DEVICE_BLOCK_SIZE,
              metavar='<audio block size>', show_default=True,
              help=('Block size in bytes for each audio device '
                    'read and write operation..'))
@click.option('--audio-flush-size',
              default=common_settings.DEFAULT_AUDIO_DEVICE_FLUSH_SIZE,
              metavar='<audio flush size>', show_default=True,
              help=('Size of silence data in bytes written '
                    'during flush operation'))
@click.option('--grpc-deadline', default=common_settings.DEFAULT_GRPC_DEADLINE,
              metavar='<grpc deadline>', show_default=True,
              help='gRPC deadline in seconds')
@click.option('--ssl-credentials-for-testing',
              metavar='<ssl credentials>',
              help='Path to ssl_certificates.pem; for testing only.')
@click.option('--grpc-channel-option', multiple=True, nargs=2,
              metavar='<option> <value>',
              help='Options used to construct gRPC channel')
def main(api_endpoint, credentials, verbose,
         input_audio_file, output_audio_file,
         audio_sample_rate, audio_sample_width,
         audio_iter_size, audio_block_size, audio_flush_size,
         grpc_deadline, *args, **kwargs):
    """Samples for the Google Assistant API.

    Examples:
      Run the sample with microphone input and speaker output:

        $ python -m googlesamples.assistant

      Run the sample with file input and speaker output:

        $ python -m googlesamples.assistant -i <input file>

      Run the sample with file input and output:

        $ python -m googlesamples.assistant -i <input file> -o <output file>
    """
    # Setup logging.
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)

    # Load credentials.
    try:
        creds = auth_helpers.load_credentials(
            credentials, scopes=[common_settings.ASSISTANT_OAUTH_SCOPE]
        )
    except Exception as e:
        logging.error('Error loading credentials: %s', e)
        logging.error('Run auth_helpers to initialize new OAuth2 credentials.')
        return

    # Create gRPC channel
    grpc_channel = auth_helpers.create_grpc_channel(
        api_endpoint, creds,
        ssl_credentials_file=kwargs.get('ssl_credentials_for_testing'),
        grpc_channel_options=kwargs.get('grpc_channel_option')
    )
    logging.info('Connecting to %s', api_endpoint)
    # Create Google Assistant API gRPC client.
    assistant = embedded_assistant_pb2.EmbeddedAssistantStub(grpc_channel)

    # Configure audio source and sink.
    audio_device = None
    if input_audio_file:
        audio_source = audio_helpers.WaveSource(
            open(input_audio_file, 'rb'),
            sample_rate=audio_sample_rate,
            sample_width=audio_sample_width
        )
    else:
        audio_source = audio_device = (
            audio_device or audio_helpers.SoundDeviceStream(
                sample_rate=audio_sample_rate,
                sample_width=audio_sample_width,
                block_size=audio_block_size,
                flush_size=audio_flush_size
            )
        )
    if output_audio_file:
        audio_sink = audio_helpers.WaveSink(
            open(output_audio_file, 'wb'),
            sample_rate=audio_sample_rate,
            sample_width=audio_sample_width
        )
    else:
        audio_sink = audio_device = (
            audio_device or audio_helpers.SoundDeviceStream(
                sample_rate=audio_sample_rate,
                sample_width=audio_sample_width,
                block_size=audio_block_size,
                flush_size=audio_flush_size
            )
        )
    # Create conversation stream with the given audio source and sink.
    conversation_stream = audio_helpers.ConversationStream(
        source=audio_source,
        sink=audio_sink,
        iter_size=audio_iter_size,
    )

    # Interactive by default.
    wait_for_user_trigger = True
    # If file arguments are supplied, don't wait for user trigger.
    if input_audio_file or output_audio_file:
        wait_for_user_trigger = False

    # Stores an opaque blob provided in ConverseResponse that,
    # when provided in a follow-up ConverseRequest,
    # gives the Assistant a context marker within the current state
    # of the multi-Converse()-RPC "conversation".
    # This value, along with MicrophoneMode, supports a more natural
    # "conversation" with the Assistant.
    conversation_state_bytes = None

    # Stores the current volument percentage.
    # Note: No volume change is currently implemented in this sample
    volume_percentage = 50

    while True:
        if wait_for_user_trigger:
            click.pause(info='Press Enter to send a new request...')

        conversation_stream.start_recording()
        logging.info('Recording audio request.')

        # This generator yields ConverseRequest to send to the gRPC
        # Google Assistant API.
        def gen_converse_requests():
            converse_state = None
            if conversation_state_bytes:
                logging.debug('Sending converse_state: %s',
                              conversation_state_bytes)
                converse_state = embedded_assistant_pb2.ConverseState(
                    conversation_state=conversation_state_bytes,
                )
            config = embedded_assistant_pb2.ConverseConfig(
                audio_in_config=embedded_assistant_pb2.AudioInConfig(
                    encoding='LINEAR16',
                    sample_rate_hertz=int(audio_sample_rate),
                ),
                audio_out_config=embedded_assistant_pb2.AudioOutConfig(
                    encoding='LINEAR16',
                    sample_rate_hertz=int(audio_sample_rate),
                    volume_percentage=volume_percentage,
                ),
                converse_state=converse_state
            )
            # The first ConverseRequest must contain the ConverseConfig
            # and no audio data.
            yield embedded_assistant_pb2.ConverseRequest(config=config)
            for data in conversation_stream:
                # Subsequent requests need audio data, but not config.
                yield embedded_assistant_pb2.ConverseRequest(audio_in=data)

        def iter_converse_requests():
            for c in gen_converse_requests():
                assistant_helpers.log_converse_request_without_audio(c)
                yield c
            conversation_stream.start_playback()

        # This generator yields ConverseResponse proto messages
        # received from the gRPC Google Assistant API.
        for resp in assistant.Converse(iter_converse_requests(),
                                       grpc_deadline):
            assistant_helpers.log_converse_response_without_audio(resp)
            if resp.error.code != code_pb2.OK:
                logging.error('server error: %s', resp.error.message)
                break
            if resp.event_type == END_OF_UTTERANCE:
                logging.info('End of audio request detected')
                conversation_stream.stop_recording()
            if resp.result.spoken_request_text:
                logging.info('Transcript of user request: "%s".',
                             resp.result.spoken_request_text)
                logging.info('Playing assistant response.')
            if len(resp.audio_out.audio_data) > 0:
                conversation_stream.write(resp.audio_out.audio_data)
            if resp.result.spoken_response_text:
                logging.info(
                    'Transcript of TTS response '
                    '(only populated from IFTTT): "%s".',
                    resp.result.spoken_response_text)
            if resp.result.conversation_state:
                conversation_state_bytes = resp.result.conversation_state
            if resp.result.volume_percentage != 0:
                volume_percentage = resp.result.volume_percentage
                logging.info('Volume should be set to %s%%', volume_percentage)
            if resp.result.microphone_mode == DIALOG_FOLLOW_ON:
                wait_for_user_trigger = False
                logging.info('Expecting follow-on query from user.')
            elif resp.result.microphone_mode == CLOSE_MICROPHONE:
                wait_for_user_trigger = True
        logging.info('Finished playing assistant response.')
        conversation_stream.stop_playback()
        # If file arguments are supplied, end the conversation.
        if input_audio_file or output_audio_file:
            break

    conversation_stream.close()


if __name__ == '__main__':
    main()
