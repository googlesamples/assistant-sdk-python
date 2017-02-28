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

# Recommended Audio parameters:
# Audio sample rate in Hertz.
#   Note: API supports higher frequencies, but using the same sample
#   rate for input and output allows us to share the same audio stream
#   for input and output.
AUDIO_SAMPLE_RATE = 16000
# Audio sample size in bytes.
AUDIO_BYTES_PER_SAMPLE = 2
# Audio I/O chunk size in bytes.
AUDIO_CHUNK_BYTES = 1024

# Embedded Assistant API RPC deadline in seconds.
DEADLINE_SECS = 60 * 3 + 5
