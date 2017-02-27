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

import unittest
from audio_helpers import SampleRateLimiter
from six import BytesIO
import time

class SampleRateLimiterTest(unittest.TestCase):
    def test_rate_limiting(self):
        stream = BytesIO()
        limiter = SampleRateLimiter(stream, 16000, 16)
        sleep_time_1024 = limiter.sleep_time(1024)
        sleep_time_512 = limiter.sleep_time(512)
        self.assertEqual(sleep_time_512, sleep_time_1024 / 2)
        previous_time = time.time()
        limiter.read(1024)
        # check sleep was not called
        self.assertLess(time.time(), previous_time + sleep_time_1024)
        previous_time = time.time()
        limiter.read(512)
        # sleep was called with sleep_time_1024
        self.assertGreater(time.time(), previous_time + sleep_time_1024)
        previous_time = time.time()
        limiter.read(0)
        # sleep was called with sleep_time_512
        self.assertGreater(time.time(), previous_time + sleep_time_512)
        self.assertLess(time.time(), previous_time + sleep_time_1024)

if __name__ == '__main__':
    unittest.main()
