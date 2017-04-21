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

"""Helper command to create assistant credentials."""

import os.path

import click

from . import (
    credentials_flow_interactive,
    save_credentials,
)
from .. import (
    common_settings
)


@click.command()
@click.option('--client-secrets',
              metavar='<client_secret_json_file>', required=True,
              help='Path to OAuth2 client secret JSON file.')
@click.option('--scope', multiple=True,
              metavar='<oauth2 scope>', show_default=True,
              default=[common_settings.ASSISTANT_OAUTH_SCOPE],
              help='API scopes to authorize access for.')
@click.option('--credentials',
              metavar='<oauth2_credentials_file>', show_default=True,
              default=os.path.join(
                  click.get_app_dir(common_settings.ASSISTANT_APP_NAME),
                  common_settings.ASSISTANT_CREDENTIALS_FILENAME
              ),
              help='Path to store OAuth2 credentials.')
def main(client_secrets, scope, credentials):
    """Helper script to generate OAuth2 credentials.
    """
    creds = credentials_flow_interactive(client_secrets, scope)
    save_credentials(credentials, creds)
    click.echo('credentials saved: %s' % credentials)


if __name__ == '__main__':
    main()
