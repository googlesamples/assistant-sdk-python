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

import google.oauth2.flow
import google.oauth2.credentials


def credentials_flow_interactive(client_secrets_file, scopes):
    """Initiate an interactive OAuth2InstalledApp flow.

    - Display a URL for the user to visit.
    - URL displays a code for the user to copy.
    - Wait on standard input for the user to enter the provided code.
    - Exchange OAuth2 tokens.

    Args:
      client_secrets_file: The path to the client secrets JSON file.
      scopes: The list of scopes to request during the flow.
    Returns: serializable credentials.
    """
    flow = google.oauth2.flow.Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=scopes,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob')
    auth_url, _ = flow.authorization_url(prompt='consent')
    print('Please go to this URL: %s' % auth_url)
    code = input('Enter the authorization code: ')
    flow.fetch_token(code=code)
    credentials = flow.credentials
    return {'access_token': credentials.token,
            'refresh_token': credentials._refresh_token,
            'token_uri': credentials._token_uri,
            'client_id': credentials._client_id,
            'client_secret': credentials._client_secret}


def refresh_credentials(credentials, scopes):
    """Refresh OAuth credentials from serialized value.

    Args:
      credentials: serialized credentials.
      scopes: The list of scopes to use the credentials with.
    Returns: OAuth2 credentials instance.
    """
    credentials = google.oauth2.credentials.Credentials(
        credentials['access_token'],
        credentials['refresh_token'],
        credentials['token_uri'],
        credentials['client_id'],
        credentials['client_secret'],
        scopes=scopes)
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return {'access_token': credentials.token,
            'refresh_token': credentials._refresh_token,
            'token_uri': credentials._token_uri,
            'client_id': credentials._client_id,
            'client_secret': credentials._client_secret}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='helper script to generate OAuth2 credentials')
    parser.add_argument('client_secrets', type=str,
                        help='Path to OAuth2 client secret JSON file. ')
    parser.add_argument('scopes', type=str, nargs='+',
                        help='API scopes to authorize access for.')
    args = parser.parse_args()
    credentials = credentials_flow_interactive(args.client_secrets,
                                               args.scopes)
    print('access_token: %s' % credentials['access_token'])
