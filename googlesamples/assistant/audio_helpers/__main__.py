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

"""Helper command to test audio stream processing.

- Record 5 seconds of 16-bit samples at 16khz.
- Playback the recorded samples.
"""

import time
import logging

import click

from . import (
    SoundDeviceStream,
    ConversationStream)

from .. import (
    common_settings
)


@click.command()
@click.option('--record-time', default=5,
              metavar='<record time>', show_default=True,
              help='Record time in secs')
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
def main(record_time, audio_sample_rate, audio_sample_width,
         audio_iter_size, audio_block_size, audio_flush_size):
    end_time = time.time() + record_time
    audio_device = SoundDeviceStream(sample_rate=audio_sample_rate,
                                     sample_width=audio_sample_width,
                                     block_size=audio_block_size,
                                     flush_size=audio_flush_size)
    stream = ConversationStream(source=audio_device,
                                sink=audio_device,
                                iter_size=audio_iter_size)
    samples = []
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting audio test.')

    stream.start_recording()
    logging.info('Recording samples.')
    while time.time() < end_time:
        samples.append(stream.read(audio_block_size))
    logging.info('Finished recording.')
    stream.stop_recording()

    stream.start_playback()
    logging.info('Playing back samples.')
    while len(samples):
        stream.write(samples.pop(0))
    logging.info('Finished playback.')
    stream.stop_playback()

    logging.info('audio test completed.')
    stream.close()


if __name__ == '__main__':
    main()
