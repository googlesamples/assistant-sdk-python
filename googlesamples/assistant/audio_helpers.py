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
import sys

from . import recommended_settings


class AudioStreamBase(object):
    """A base class for audio stream based on file-like objects.

    Args:
      fp: file-like stream object to read from.
      sample_rate: sample rate in hertz.
      bytes_per_sample: sample size in bytes.
      chunk_size: chunk size in bytes of each read when iterating.
    """
    def __init__(self,
                 sample_rate=recommended_settings.AUDIO_SAMPLE_RATE_HZ,
                 bytes_per_sample=recommended_settings.AUDIO_BYTES_PER_SAMPLE,
                 chunk_size=recommended_settings.AUDIO_CHUNK_SIZE):
        self._sample_rate = sample_rate
        self._bytes_per_sample = bytes_per_sample
        self._chunk_size = chunk_size

    @property
    def sample_rate(self):
        """Return the sample rate of the underlying audio stream."""
        return self._sample_rate

    @property
    def bytes_per_sample(self):
        """Return the sample width of the underlying audio stream."""
        return self._bytes_per_sample

    @property
    def chunk_size(self):
        """Return the chunk size of the underlying audio stream."""
        return self._chunk_size

    def __iter__(self):
        """Returns a generator reading data from the stream."""
        return iter(lambda: self.read(self._chunk_size), '')


class SampleRateLimiter(AudioStreamBase):
    """A stream reader that throttles reads to a given sample rate.

    This is used to throttle the rate at which gRPC ConverseRequest
    messages are sent to the EmbeddedAssistant API to emulate "real
    time" (i.e. at sample rate) audio throughput when reading data
    from files.

    Support file-object like interface and generator iteration.

    Args:
      fp: file-like stream object to read from.
      sample_rate: sample rate in hertz.
      bytes_per_sample: sample size in bytes.
      chunk_size: chunk size in bytes of each read when iterating.
    """
    def __init__(self, fp, *args, **kwargs):
        super(SampleRateLimiter, self).__init__(*args, **kwargs)
        self._fp = fp
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

    def close(self):
        """Close the underlying stream."""
        self._fp.close()

    def _sleep_time(self, size):
        sample_count = size / float(self.bytes_per_sample)
        sample_rate_dt = sample_count / float(self.sample_rate)
        return sample_rate_dt

    @property
    def name(self):
        return self._fp.name


class WaveStreamWriter(AudioStreamBase):
    """A WAV stream writer.

    Args:
      fp: file-like stream object to read from.
      sample_rate: sample rate in hertz.
      bytes_per_sample: sample size in bytes.
    """
    def __init__(self, fp, *args, **kwargs):
        super(WaveStreamWriter, self).__init__(*args, **kwargs)
        self._fp = fp
        self._wavep = wave.open(self._fp)
        self._wavep.setsampwidth(self.bytes_per_sample)
        self._wavep.setnchannels(1)
        self._wavep.setframerate(self.sample_rate)

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


# TODO(proppy): split pyAudio helper in separate file.
class PyAudioStream(AudioStreamBase):
    """A PyAudio stream helper.

    Support file-object like interface and generator iteration.

    Args:
      sample_rate: sample rate in hertz.
      bytes_per_sample: sample size in bytes.
      chunk_size: chunk size in bytes of each audio I/O buffer.
    """
    def __init__(self, *args, **kwargs):
        super(PyAudioStream, self).__init__(*args, **kwargs)
        if self.bytes_per_sample == 2:
            audio_format = pyaudio.paInt16
        else:
            raise Exception('unsupported sample size:', self.bytes_per_sample)
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=audio_format,
            channels=1,
            rate=self.sample_rate,
            frames_per_buffer=int(self.chunk_size/self.bytes_per_sample),
            input=True, output=True
        )

    @property
    def name(self):
        """Returns the name of the underlying audio device."""
        return self._audio_interface.get_default_input_device_info()['name']

    def read(self, size):
        """Read the given number of bytes from the stream."""
        # TODO(proppy): enable exception_on_overflow when audio
        # processing moved to separate thread.
        return self._audio_stream.read(size, exception_on_overflow=False)

    def write(self, buf):
        """Write the given bytes to the stream."""
        return self._audio_stream.write(buf)

    def flush(self, size=recommended_settings.AUDIO_FLUSH_SIZE):
        self._audio_stream.write(b'\x00' * size)

    def close(self):
        """Flush and close the underlying stream and audio interface."""
        if self._audio_stream:
            self.flush()
            self._audio_stream.close()
            self._audio_stream = None
        if self._audio_interface:
            self._audio_interface.terminate()
            self._audio_interface = None


if __name__ == '__main__':
    """Test audio stream processing:
    - Record 5 seconds of 16-bit samples at 16khz.
    - Playback the recorded samples.
    """
    import logging
    from tqdm import tqdm

    sample_rate_hz = recommended_settings.AUDIO_SAMPLE_RATE_HZ
    bytes_per_sample = recommended_settings.AUDIO_BYTES_PER_SAMPLE
    chunk_size = recommended_settings.AUDIO_CHUNK_SIZE
    record_time = 5
    end_time = time.time() + record_time
    stream = PyAudioStream(sample_rate_hz,
                           bytes_per_sample,
                           chunk_size)
    samples = []
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting audio test.')
    with tqdm(unit='s', total=sample_rate_hz*record_time,
              position=0) as t:
        t.set_description('Recording samples: ')
        while time.time() < end_time:
            samples.append(stream.read(chunk_size))
            t.update(chunk_size)

    with tqdm(unit='s', total=sample_rate_hz*record_time, position=1) as t:
        t.set_description('Playing samples: ')
        while len(samples):
            stream.write(samples.pop(0))
            t.update(chunk_size)

    stream.close()
    logging.info('audio test completed.')


def iter_with_progress(title, gen):
    from tqdm import tqdm
    with tqdm(unit='B', unit_scale=True, position=0) as t:
        t.set_description(title)
        for d in gen:
            t.update(sys.getsizeof(d))
            yield d
