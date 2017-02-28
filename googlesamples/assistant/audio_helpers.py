#
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
import pyaudio
import wave


# TODO(proppy): parse WAV instead of RAW data.
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
        self._fp = fp
        self._sample_rate = float(sample_rate)
        self._bytes_per_sample = float(bytes_per_sample)
        self._sleep_until = 0

    def read(self, size):
        """Read bytes from the stream and block until sample rate is achieved.

        Args:
          size: number of bytes to read from the stream.
        """
        now = time.time()
        missing_dt = self._sleep_until - now
        if missing_dt > 0:
            time.sleep(missing_dt)
        self._sleep_until = time.time() + self._sleep_time(size)
        data = self._fp.read(size)
        #  When reach end of audio stream, pad remainder with silence (zeros).
        return data.ljust(size, b'\x00')

    @property
    def sample_rate(self):
        """Return the sample rate of the underlying audio stream."""
        return self._sample_rate

    @property
    def bytes_per_sample(self):
        """Return the sample width of the underlying audio stream."""
        return self._bytes_per_sample

    def _sleep_time(self, size):
        sample_count = size / self.bytes_per_sample
        sample_rate_dt = sample_count / self.sample_rate
        return sample_rate_dt

    @property
    def name(self):
        return self._fp.name

    def close(self):
        """Close the underlying stream."""
        self._fp.close()


class WaveStreamWriter(object):
    """A WAV stream writer.

    Args:
      fp: file-like stream object to write to.
      sample_rate: sample rate in hertz.
      bytes_per_sample: sample size in bytes.
    """
    def __init__(self, fp, sample_rate, bytes_per_sample):
        self._fp = fp
        self._sample_rate = float(sample_rate)
        self._bytes_per_sample = float(bytes_per_sample)
        self._wavep = wave.open(self.fp)
        self._wavep.setsampwidth(bytes_per_sample)
        self._wavep.setnchannels(1)
        self._wavep.setframerate(sample_rate)

    @property
    def sample_rate(self):
        """Return the sample rate of the underlying audio stream."""
        return self._sample_rate

    @property
    def bytes_per_sample(self):
        """Return the sample width of the underlying audio stream."""
        return self._bytes_per_sample

    def write(self, data):
        """Read frame bytes to the WAV stream.

        Args:
          data: frame data to write.
        """
        self._wavep.writeframes(data)

    def close(self):
        """Close the underlying stream."""
        self._wavep.close()
        self._fp.close()


# TODO(proppy): split payaudio helper in separate file.
class SharedAudioStream(object):
    """A Shared PyAudio stream.

    Each instance will share the same bi-directional audio stream and
    audio interface.

    Args:
      fp: file-like stream object to write to.
      sample_rate: sample rate in hertz.
      bytes_per_sample: sample size in bytes.
      buffer_size: size in bytes of each audio I/O buffer.
    """
    _audio_interface = None
    _audio_stream = None

    def __init__(self, sample_rate, bytes_per_sample, buffer_size):
        self._sample_rate = sample_rate
        self._bytes_per_sample = bytes_per_sample

        if SharedAudioStream._audio_interface:
            return

        if bytes_per_sample == 2:
            audio_format = pyaudio.paInt16
        else:
            raise Exception('unsupported sample size:', bytes_per_sample)
        SharedAudioStream._audio_interface = pyaudio.PyAudio()
        SharedAudioStream._audio_stream = self._audio_interface.open(
            format=audio_format,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=sample_rate,
            frames_per_buffer=int(buffer_size/bytes_per_sample),
            input=True, output=True
        )

    @property
    def name(self):
        """Returns the name of the underlying audio device."""
        return self._audio_interface.get_default_input_device_info()['name']

    @property
    def sample_rate(self):
        """Return the sample rate of the underlying audio stream."""
        return self._sample_rate

    @property
    def bytes_per_sample(self):
        """Return the sample width of the underlying audio stream."""
        return self._bytes_per_sample

    def read(self, size):
        """Read the given number of bytes from the stream."""
        return self._audio_stream.read(size)

    def write(self, buf):
        """Write the given bytes to the stream."""
        return self._audio_stream.write(buf)

    def close(self):
        """Close the underlying stream and audio interface."""
        if SharedAudioStream._audio_stream:
            self._audio_stream.close()
            SharedAudioStream.audio_stream = None
        if SharedAudioStream._audio_interface:
            self._audio_interface.terminate()
            SharedAudioStream._audio_interface = None


if __name__ == '__main__':
    """Test audio stream processing:
    - Record 5 seconds of 16-bit samples at 16khz.
    - Playback the recorded samples.
    """
    import logging
    from tqdm import tqdm

    sample_rate_hz = 16000
    bytes_per_sample = 2
    buffer_size = 1024
    record_time = 5
    end_time = time.time() + record_time
    stream = SharedAudioStream(sample_rate_hz,
                               bytes_per_sample,
                               buffer_size)
    samples = []
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting audio test.')
    with tqdm(unit='s', total=sample_rate_hz*record_time,
              position=0) as t:
        t.set_description('Recording samples: ')
        while time.time() < end_time:
            samples.append(stream.read(buffer_size))
            t.update(buffer_size)

    with tqdm(unit='s', total=sample_rate_hz*record_time, position=1) as t:
        t.set_description('Playing samples: ')
        while len(samples):
            stream.write(samples.pop(0))
            t.update(buffer_size)

    stream.close()
    logging.info('audio test completed.')
