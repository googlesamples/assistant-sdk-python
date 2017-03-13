Embedded Assistant Python SDK & Samples
=======================================

This repositories contains Python samples for the Embedded Assistant API.

Supported configuration
-----------------------

- [Raspberry Pi 3 Model B](https://www.adafruit.com/products/3334)
- [Mini USB Microphone](https://www.adafruit.com/product/3367)
- [Mini External USB Stereo Speaker](https://www.adafruit.com/products/3369) or [3.5mm Stereo Jack Speaker](https://www.sparkfun.com/products/14023).
- [Raspbian Jessie with Pixel](https://www.raspberrypi.org/downloads/raspbian/)
- [Enable SSH on Raspbian](https://www.raspberrypi.org/documentation/remote-access/ssh/)

Connect to the Raspberry Pi
===========================

- Depending of the Raspberry Pi configuration, follow guides below to
configure network access:

    - [Connect to a WiFi network](https://www.raspberrypi.org/documentation/configuration/wireless/README.md) network.
    - [Get console access using a USB-TTL cable](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-5-using-a-console-cable/overview).
    - [Connect to a WiFi network using the command line](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md)

- [Find the Raspberry Pi IP address](https://www.raspberrypi.org/documentation/remote-access/ip-address.md)
- Connect to the Raspberry Pi

        ssh pi@<raspberry-pi-ip-address>
        password: raspberry

Get the source
==============

- [Connect to the Raspberry Pi](#Connect-to-the-Raspberry-Pi)
- [Sign in](https://dev-partners-review.googlesource.com) the dev-partners gerrit instance.
- [Generate](https://dev-partners-review.googlesource.com/new-password) a new gerrit password
- Clone this repository:

        git clone https://dev-partners.googlesource.com/embedded-assistant-sdk-python

API Setup
=========

- Visit [console.developers.google.com](https://console.developers.google.com).
- Select an existing project or create a new one.
- Go to `API Manager / Dashboard`.
- Enable [`Embedded Google Assistant API`](https://console.developers.google.com/apis/api/internal-assistant-api/overview).
- Go to `API Manager / Credentials`.
- Click `Create credentials / OAuth Client ID`.
- Select `Other`.
- Click `Create`.
- Click `⬇` to download the `client_secret_XXXX.json` file.
- Copy the `client_secret_XXXX.json` file to the Raspberry Pi:

        scp ~/Downloads/client_secret_XXXX.json pi@raspberry-pi-ip-address:/home/pi/embedded-assistant-sdk-python/
        password: raspberry

Audio setup
===========

- [Connect to the Raspberry Pi](#Connect-to-the-Raspberry-Pi)
- Connect the USB microphone
- Connect the USB speaker or 3.5mm stereo jack speaker
- Enter the [sample directory](#Get-the-source)

        cd embedded-assistant-sdk-python

- Copy the `.asoundrc` file corresponding to the audio setup.

    - USB microphone and USB speaker:

            cp alsa/usb_mic_usb_speaker/.asoundrc /home/pi

    - USB microphone and 3.5mm stereo jack speaker:

            cp alsa/usb_mic_jack_speaker/.asoundrc /home/pi

- Verify that recording and playback are working:

            # record a short audio clip
            arecord --format=S16_LE --duration=5 --rate=16k --file-type=raw out.raw
            # check recording by replaying it
            aplay --format=S16_LE --rate=16k out.raw

            # adjust playback and recording volume
            alsamixer

Sample Setup
============

- [Connect to the Raspberry Pi](#Connect-to-the-Raspberry-Pi)
- Enter the [sample directory](#Get-the-source)

        cd embedded-assistant-sdk-python

- Install the sample and its dependencies:
  - If using python 3 (recommended):

        sudo apt-get update
        sudo apt-get install python3-dev python3-venv portaudio19-dev libffi-dev libssl-dev
        python3 -m venv env
        env/bin/python -m pip install -e ".[MAIN]"

  - If using python 2:

        sudo apt-get update
        sudo apt-get install python-dev python-virtualenv portaudio19-dev libffi-dev libssl-dev
        virtualenv env --no-site-packages
        env/bin/pip install -e ".[MAIN]"

- Verify the audio setup:

        # Record a 5 sec sample and play it back
        env/bin/python -m googlesamples.assistant.audio_helpers

Run the sample
==============

- [Connect to the Raspberry Pi](#Connect-to-the-Raspberry-Pi)
- Enter the [sample directory](#Get-the-source)

        cd embedded-assistant-sdk-python

- Authorize the Embedded Assistant sample to make Google Assistant query for a given Google Account.

        env/bin/python -m googlesamples.assistant --authorize client_secret_XXXX.json
        Please go to this URL: ...
        Enter the authorization code:

- Start the Embedded Assistant sample.

        env/bin/python -m googlesamples.assistant

- Record a voice query and the sample should play back the Google
  Assistant answer.

Troubleshooting
===============

- Use the following commands to troubleshoot/workaaround PyAudio issues:
```
# Record an assistant query with alsa commandline tools
arecord --format=S16_LE --duration=5 --rate=16k --file-type=raw in.raw
env/bin/python -m googlesamples.assistant -i in.raw

# Playback an assistant answer with alsa commandline tools
env/bin/python -m googlesamples.assistant -o out.raw
aplay out.raw
```

Test
====

```
# Run tests
env/bin/python setup.py flake8
env/bin/python setup.py test
```

License
=======

Copyright (C) 2016 Google Inc.

Licensed to the Apache Software Foundation (ASF) under one or more contributor
license agreements.  See the NOTICE file distributed with this work for
additional information regarding copyright ownership.  The ASF licenses this
file to you under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License.  You may obtain a copy of
the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
License for the specific language governing permissions and limitations under
the License.
