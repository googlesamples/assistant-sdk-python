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


class DeviceClient(Client):
    """oauthlib Client implementation for the device grant_type."""

    def prepare_request_uri(self, uri, redirect_uri=None, scope=None,
                            state=None, **kwargs):
        return uri

    def prepare_request_body(self, client_id=None, code=None, body='',
                             redirect_uri=None, **kwargs):
        code = code or self.code
        return prepare_token_request('http://oauth.net/grant_type/device/1.0',
                                     code=code, body=body,
                                     client_id=self.client_id,
                                     redirect_uri=redirect_uri,
                                     **kwargs)


class DeviceFlow(google.oauth2.flow.Flow):
    """Flow implementation for OAuth2ForDevice."""

    def __init__(self, client_config, scopes, **kwargs):
        """
        Args:
        client_config: The client configuration
          in the Google `client secrets` format.
        scopes: The list of scopes to request during the flow.
        """
        client = DeviceClient(client_config['installed']['client_id'])
        session, client_config = (
            google.oauth2.oauthlib.session_from_client_config(
                client_config, scopes, client=client, **kwargs))
        super(DeviceFlow, self).__init__(session,
                                         client_type='installed',
                                         client_config=client_config)

    def device_code(self):
        r = self.oauth2session.post(
            'https://accounts.google.com/o/oauth2/device/code',
            data={'client_id': self.client_config['client_id'],
                  'scope': ' '.join(self.oauth2session.scope)})
        device_resp = r.json()
        return (device_resp['user_code'],
                device_resp['verification_url'],
                device_resp['device_code'])


def deviceflow_interactive(client_secrets, scopes):
    """Initiate an interactive OAuth2ForDevice flow.

    - Display a code and a url for the user to visit.
    - Poll for token until the user enters the code on the provided URL.
    - Return credentials.

    Args:
      client_secrets: The client configuration
        in the Google `client secrets` format.
      scopes: The list of scopes to request during the flow.
    """
    flow = DeviceFlow(client_secrets, scopes)
    user_code, url, device_code = flow.device_code()
    print("visit: %s and enter code: %s" % (url, user_code))

    while True:
        try:
            flow.fetch_token(code=device_code)
            break
        except MissingTokenError:
            print('waiting for authorization code')
            sleep(5)
            pass

    return flow.credentials


def webflow_interactive(client_secrets, scopes):
    """Initiate an interactive OAuth2ForWebServer flow.

    - Display a url for the user to visit.
    - Wait for an incoming HTTP request to the given redirect_url.
    - Exchange OAuth2 tokens.
    - Return credentials.

    Args:
      client_secrets: The client configuration
        in the Google `client secrets` format.
      scopes: The list of scopes to request during the flow.
    """
    session, client_config = (
        google.oauth2.oauthlib.session_from_client_config(
            client_secrets, scopes, redirect_uri='http://localhost:8000'))
    flow = google.oauth2.flow.Flow(session,
                                   client_type='web',
                                   client_config=client_config)
    auth_url, _ = flow.authorization_url(prompt='consent')
    print("visit: %s" % auth_url)

    def wait_for_request(message):
        result = {}

        def capture_app(environ, start_response):
            status = '200 OK'
            headers = [('Content-type', 'text/plain')]
            start_response(status, headers)
            result.update(parse_qsl(environ['QUERY_STRING']))
            return [message]

        class SilentWSGIRequestHandler(WSGIRequestHandler):

            def log_message(self, format, *args):
                pass
        # TODO(proppy): make port number / redirect_url a parameter.
        httpd = make_server('', 8000, capture_app,
                            handler_class=SilentWSGIRequestHandler)
        httpd.handle_request()
        return result

    result = wait_for_request(b'authorized')
    code = result['code']
    flow.fetch_token(code=code)
    return flow.credentials


def get_credentials_flow(client_secrets_file, scopes):
    """Initiate an interactive OAuth2 flow according to the client type.

    - OAuth2ForDevice for installed app OAuth2 config.
    - OAuth2ForWebService for web app OAuth2 config.

    Args:
      client_secrets_file: The path to the client secrets JSON file.
      scopes: The list of scopes to request during the flow.
    """
    with open(client_secrets_file, 'r') as json_file:
        client_config = json.load(json_file)
    if 'installed' in client_config:
        return deviceflow_interactive(client_config, scopes)
    elif 'web' in client_config:
        return webflow_interactive(client_config, scopes)
    raise Exception('unsupported client credentials: %s', client_config.keys())


if __name__ == '__main__':
    usage = 'usage: auth_helpers.py path/to/client_secrets.json SCOPES...\n'
    if len(sys.argv) < 3:
        sys.stderr.write(usage)
        sys.exit(-1)
    credentials = get_credentials_flow(sys.argv[1], scopes=sys.argv[2:])
    print("access_token: %s" % credentials.token)
