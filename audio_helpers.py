#!/usr/bin/python
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

import time


class SampleRateLimiter(object):
    """A stream reader that throttles reads to a given sample rate.

    This is used to throttle the rate at which gRPC ConverseRequest
    messages are sent to the EmbeddedAssistant API to emulate "real
    time" (i.e. at sample rate) audio throughput when reading data
    from files.

    Args:
      fp: file-like stream object to read from.
      sample_rate: sample rate in hertz.
      bytes_per_sample: sample size in bytes.
    """
    def __init__(self, fp, sample_rate, bytes_per_sample):
        self.fp = fp
        self.sample_rate = float(sample_rate)
        self.bytes_per_sample = float(bytes_per_sample)
        self.sleep_until = 0

    def read(self, size):
        """Read bytes from the stream and block until sample rate is achieved.

        Args:
          size: number of bytes to read from the stream.
        """
        now = time.time()
        missing_dt = self.sleep_until - now
        if missing_dt > 0:
            time.sleep(missing_dt)
        self.sleep_until = time.time() + self.sleep_time(size)
        data = self.fp.read(size)
        #  When reach end of audio stream, pad remainder with silence (zeros).
        return data.ljust(size, b'\x00')

    def sleep_time(self, size):
        sample_count = size / self.bytes_per_sample
        sample_rate_dt = sample_count / self.sample_rate
        return sample_rate_dt

    def close(self):
        """Close the underlying stream."""
        self.fp.close()
