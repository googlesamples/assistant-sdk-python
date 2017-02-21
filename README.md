Embedded Assistant Python SDK & Samples
=======================================

This repositories contains Python modules and samples for the Embedded Assistant
API.

Pre-requisites
--------------

- Raspberry Pi 3 running Raspbian
- USB audio adapter
- Microphone
- Speaker

API Setup
=========

- Visit [console.developers.google.com](console.developers.google.com).
- Select an existing project or create a new one.
- Go to `API Manager / Dashboard`.
- Enable `Google Cloud Speech API`.
- Go to `API Manager / Credentials`.
- Click `Create credentials / OAuth Client ID`.
- Select `Web`.
- Add `http://localhost:8080` and `http://raspberrypi.local:8080` as the `Authorized redirect URIs`.
- Click `Create`.
- Click `⬇` to download the `client_secret_XXXX.json` file.

Hardware setup
==============

- Connect the Microphone and the Speaker to the USB audio adapter.
- Connect the USB audio adapter to one of the Raspberry Pi USB port.
- Verify that the Microphone and the Speaker are working:

```
# record a short audio clip
arecord --format=S16_LE --duration=5 --rate=16k --file-type=raw out.raw
# check recording by replaying it
aplay --format=S16_LE --rate=16k out.raw
```

R Setup
==================

- Clone this repository:

```
git clone sso://devrel/samples/assistant/embedded-sdk-python embedded-assistant-sdk-python
```

- Copy the `client_secret_XXXX.json` file to the same directory:

```
cp ~/Downloads/client_secret_XXXX.json embedded-assistant-sdk-python/client_secret.json
```

- Copy this directory to the Raspberry Pi using `scp`:

```
scp -r embedded-assistant-sdk-python pi@raspberrypi.local:/home/pi
```

- SSH into the Raspberry Pi and install the sample dependencies:

```
ssh pi@raspberrypi.local
cd embedded-assistant-sdk-python
python -m venv env
env/bin/python -m pip install -r requirements.txt
```

Run the sample
==============

- Run the following command.
```
python embedded_assistant.py --client_secrets client_secret.json
```
- Follow the authorization instructions.
- Record your voice query and the sample should play back the assistant answer.

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
