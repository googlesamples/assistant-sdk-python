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
from googlesamples.assistant.audio_helpers import SampleRateLimiter
from six import BytesIO
import time


class SampleRateLimiterTest(unittest.TestCase):
    def setUp(self):
        stream = BytesIO()
        self.limiter = SampleRateLimiter(stream, 16000, 16, 1024)
        self.sleep_time_1024 = self.limiter._sleep_time(1024)
        self.sleep_time_512 = self.limiter._sleep_time(512)

    def test_sleep_time(self):
        self.assertEqual(self.sleep_time_512, self.sleep_time_1024 / 2)

    def test_no_sleep_on_first_read(self):
        previous_time = time.time()
        self.limiter.read(1024)
        # check sleep was not called
        self.assertLess(time.time(), previous_time + self.sleep_time_1024)

    def test_first_sleep(self):
        self.limiter.read(1024)
        previous_time = time.time()
        self.limiter.read(512)
        # sleep was called with sleep_time_1024
        self.assertGreater(time.time(), previous_time + self.sleep_time_1024)

    def test_next_sleep(self):
        self.limiter.read(1024)
        self.limiter.read(512)
        previous_time = time.time()
        self.limiter.read(0)
        # sleep was called with sleep_time_512
        self.assertGreater(time.time(), previous_time + self.sleep_time_512)
        self.assertLess(time.time(), previous_time + self.sleep_time_1024)


if __name__ == '__main__':
    unittest.main()
