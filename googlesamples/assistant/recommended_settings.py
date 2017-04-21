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

# Recommended internal parameters. Changing these values may result in
# errors. See https://developers.google.com/assistant/reference for
# more information.
#
# Audio sample rate in Hertz.
#   Note: API supports higher frequencies, but using the same sample
#   rate for input and output allows us to share the same audio stream
#   for input and output.
AUDIO_SAMPLE_RATE_HZ = 16000
# Size of a single sample in bytes.
AUDIO_SAMPLE_SIZE = 2
# Size of an audio block of 1 seconds in bytes
# for the configured sample rate and size.
AUDIO_1SECOND_SIZE = AUDIO_SAMPLE_RATE_HZ * AUDIO_SAMPLE_SIZE
# Size of each ConverseStream read operation in bytes.
CONVERSE_READ_SIZE = int(0.1 * AUDIO_1SECOND_SIZE)
# Block size in bytes for each audio device read and write operation.
AUDIO_DEVICE_BLOCK_SIZE = int(0.2 * AUDIO_1SECOND_SIZE)
# Size of silence data in bytes written during flush operation
# (used during playback to ensure audio is not truncated).
AUDIO_DEVICE_FLUSH_SIZE = int(0.8 * AUDIO_1SECOND_SIZE)

# Google Assistant API RPC deadline in seconds.
DEADLINE_SECS = 60 * 3 + 5
