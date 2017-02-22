Embedded Assistant Python SDK & Samples
=======================================

This repositories contains Python modules and samples for the Embedded Assistant
API.

Pre-requisites
--------------

- Python >= 2.7 or >= 3.4
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
- Select `Other`.
- Click `Create`.
- Click `⬇` to download the `client_secret_XXXX.json` file.

Hardware setup
==============

- Verify that the Microphone and the Speaker are working:
```
# record a short audio clip
arecord --format=S16_LE --duration=5 --rate=16k --file-type=raw out.raw
# check recording by replaying it
aplay --format=S16_LE --rate=16k out.raw
```

Sample Setup
============

- Clone this repository:

```
git clone sso://devrel/samples/assistant/embedded-sdk-python embedded-assistant-sdk-python
```

- Copy the `client_secret_XXXX.json` file to the same directory:

```
cp ~/Downloads/client_secret_XXXX.json embedded-assistant-sdk-python/client_secret.json
```

- Install the sample dependencies:
    - If you're using python 3:

        ```
        PYTHON3_MINOR_VERSION=$(python3 -c 'import sys; print(sys.version_info[1])')
        sudo apt-get install python3-dev python3.$PYTHON3_MINOR_VERSION-venv
        cd embedded-assistant-sdk-python
        python3 -m venv env
        env/bin/python3 -m pip install -r requirements.txt
        ```

  - If you're using python 2:

        ```
        sudo apt-get install python-dev python-virtualenv
        cd embedded-assistant-sdk-python
        virtualenv env --no-site-packages
        env/bin/pip install -r requirements.txt
        ```

Run the sample
==============

- Initialize new OAuth2 credentials by running the following command
  and follow its instructions.
```
env/bin/python embedded_assistant.py --authorize client_secret.json
```
- Start the Embedded Assistant sample.
```
env/bin/python embedded_assistant.py
```
- Record your voice query and the sample should play back the Google
  Assistant answer.

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
