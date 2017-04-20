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

"""auth_helpers implements InstalledApp authorization flow helpers."""

import json
import os

import google.auth
import google.auth.transport.grpc
import google.auth.transport.requests
import google_auth_oauthlib.flow
import google.oauth2.credentials
import grpc


def credentials_flow_interactive(client_secrets_path, scopes):
    """Initiate an interactive OAuth2InstalledApp flow.

    - If an X server is running: Run a browser based flow.
    - If not: Run a console based flow.

    Args:
      client_secrets_file: The path to the client secrets JSON file.
      scopes: The list of scopes to request during the flow.
    Returns:
      google.oauth2.credentials.Credentials: new OAuth2 credentials authorized
        with the given scopes.
    """
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_path,
        scopes=scopes)
    if 'DISPLAY' in os.environ:
        flow.run_local_server()
    else:
        flow.run_console()
    return flow.credentials


def credentials_to_dict(credentials):
    return {'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret}


def credentials_from_dict(credentials, scopes):
    return google.oauth2.credentials.Credentials(
        token=credentials['access_token'],
        refresh_token=credentials['refresh_token'],
        token_uri=credentials['token_uri'],
        client_id=credentials['client_id'],
        client_secret=credentials['client_secret'],
        scopes=scopes)


def save_credentials(path, credentials):
    """Write credentials to the given file.
    Args:
      path(str): path to the credentials file.
      credentials(google.oauth2.credentials.Credentials): OAuth2 credentials.
    """
    config_path = os.path.dirname(path)
    if not os.path.isdir(config_path):
        os.makedirs(config_path)
    with open(path, 'w') as f:
        json.dump(credentials_to_dict(credentials), f)


def load_credentials(path, scopes):
    """Load credentials from the given file.
    Args:
      path(str): path to the credentials file.
      scopes: scope for the given credentials.
    Returns:
      google.oauth2.credentials.Credentials: OAuth2 credentials.
    """
    with open(path, 'r') as f:
        return credentials_from_dict(json.load(f),
                                     scopes=scopes)


def create_grpc_channel(target, credentials, ssl_credentials_file=None,
                        grpc_channel_options=[]):
    """Create and return a gRPC channel.

    Args:
      credentials(google.oauth2.credentials.Credentials): OAuth2 credentials.
      ssl_credentials_file(str): Path to SSL credentials.pem file
        (for testing).
      grpc_channel_options([(option_name, option_val)]): gRPC channel options.
    Returns:
      grpc.Channel.
    """
    ssl_credentials = None
    if ssl_credentials_file:
        with open(ssl_credentials_file) as f:
            ssl_credentials = grpc.ssl_channel_credentials(f.read())
    http_request = google.auth.transport.requests.Request()
    # TODO(proppy): figure out if/why we need to force a refresh.
    # if yes, consider remove access token from serialized credentials.
    credentials.refresh(http_request)
    return google.auth.transport.grpc.secure_authorized_channel(
        credentials, http_request, target,
        ssl_credentials=ssl_credentials,
        options=grpc_channel_options)
