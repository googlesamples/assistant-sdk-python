#!/usr/bin/python
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
"""auth_helpers implements Device and Web authorization flow."""

import sys
import json
from time import sleep
from six.moves.urllib.parse import parse_qsl
from wsgiref.simple_server import make_server, WSGIRequestHandler

from oauthlib.oauth2.rfc6749.clients.base import Client
from oauthlib.oauth2.rfc6749.parameters import prepare_token_request
from oauthlib.oauth2.rfc6749.errors import MissingTokenError
import google.oauth2.flow


def oobflow_interactive(client_secrets, scopes):
    """Initiate an interactive OAuth2InstalledApp flow.

    - Display a URL for the user to visit.
    - URL displays a code for the user to copy.
    - Wait on standard input for the user to enter the provided code.
    - Exchange OAuth2 tokens.
    - Return credentials.

    Args:
      client_secrets: The client configuration
        in the Google `client secrets` format.
      scopes: The list of scopes to request during the flow.
    """
    session, client_config = (
        google.oauth2.oauthlib.session_from_client_config(
            client_secrets, scopes, redirect_uri='urn:ietf:wg:oauth:2.0:oob'))
    flow = google.oauth2.flow.Flow(session,
                                   client_type='installed',
                                   client_config=client_config)
    auth_url, _ = flow.authorization_url(prompt='consent')
    print('visit: %s' % auth_url)
    code = input('enter the code: ')
    flow.fetch_token(code=code)
    return flow.credentials


def get_credentials_flow(client_secrets_file, scopes):
    """Initiate an interactive OAuth2InstalledApp flow.

    Args:
      client_secrets_file: The path to the client secrets JSON file.
      scopes: The list of scopes to request during the flow.
    """
    with open(client_secrets_file, 'r') as json_file:
        client_config = json.load(json_file)
    return oobflow_interactive(client_config, scopes)


if __name__ == '__main__':
    usage = 'usage: auth_helpers.py path/to/client_secrets.json SCOPES...\n'
    if len(sys.argv) < 3:
        sys.stderr.write(usage)
        sys.exit(-1)
    credentials = get_credentials_flow(sys.argv[1], scopes=sys.argv[2:])
    print('access_token: %s' % credentials.token)
