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

"""Sample that implements device registration for the Google Assistant API."""

import json
import os

import click
import google.oauth2.credentials
import google.auth.transport.requests


def failed_request_exception(message, r):
    """Build ClickException from a failed request."""
    try:
        resp = json.loads(r.text)
        message = '%s: %d %s' % (message,
                                 resp['error']['code'],
                                 resp['error']['message'])
        if 'details' in resp['error']:
            details = '\n'.join(d['detail'] for d in resp['error']['details'])
            message += ' ' + details
        return click.ClickException(message)
    except ValueError:
        # fallback on raw text response if error is not structured.
        return click.ClickException('%s: %d\n%s' % (message,
                                                    r.status_code,
                                                    r.text))


@click.group()
@click.option('--project')
@click.option('--client-secret')
@click.option('--api-endpoint', default='embeddedassistant.googleapis.com',
              show_default=True)
@click.option('--credentials', show_default=True,
              default=os.path.join(click.get_app_dir('google-oauthlib-tool'),
                                   'credentials.json'))
@click.pass_context
def cli(ctx, project, client_secret, api_endpoint, credentials):
    try:
        with open(credentials, 'r') as f:
            c = google.oauth2.credentials.Credentials(token=None,
                                                      **json.load(f))
            http_request = google.auth.transport.requests.Request()
            c.refresh(http_request)
    except Exception as e:
        raise click.ClickException('Error loading credentials: %s.\n'
                                   'Run google-oauthlib-tool to initialize '
                                   'new OAuth 2.0 credentials.' % e)
    if project is None:
        if client_secret is None:
            client_secret = 'client_secret_%s.json' % c.client_id
        try:
            with open(client_secret, 'r') as f:
                secret = json.load(f)
                project = secret['installed']['project_id']
        except Exception as e:
            raise click.ClickException('Error loading client secret: %s.\n'
                                       'Run the register tool'
                                       'with --client-secret '
                                       'or --project option.\n'
                                       'Or copy the %s file'
                                       'in the current directory.'
                                       % (e, client_secret))
    ctx.obj['SESSION'] = google.auth.transport.requests.AuthorizedSession(c)
    ctx.obj['API_URL'] = ('https://%s/v1alpha2/projects/%s'
                          % (api_endpoint, project))
    ctx.obj['PROJECT_ID'] = project


@cli.command()
@click.option('--model', required=True)
@click.option('--type', type=click.Choice(['LIGHT', 'SWITCH', 'OUTLET']),
              required=True)
@click.option('--trait', multiple=True)
@click.option('--manufacturer', required=True)
@click.option('--product-name', required=True)
@click.option('--description')
@click.option('--device', required=True)
@click.option('--nickname')
@click.pass_context
def register(ctx, model, type, trait, manufacturer, product_name, description,
             device, nickname):
    ctx.invoke(register_model,
               model=model, type=type, trait=trait,
               manufacturer=manufacturer,
               product_name=product_name,
               description=description)
    ctx.invoke(register_device, device=device, model=model, nickname=nickname)


@cli.command('register-model')
@click.option('--model', required=True)
@click.option('--type', type=click.Choice(['LIGHT', 'SWITCH', 'OUTLET']),
              required=True)
@click.option('--trait', multiple=True)
@click.option('--manufacturer', required=True)
@click.option('--product-name', required=True)
@click.option('--description')
@click.pass_context
def register_model(ctx, model, type, trait,
                   manufacturer, product_name, description):
    session = ctx.obj['SESSION']

    model_base_url = '/'.join([ctx.obj['API_URL'], 'deviceModels'])
    model_url = '/'.join([model_base_url, model])
    payload = {
        'device_model_id': model,
        'project_id': ctx.obj['PROJECT_ID'],
        'device_type': 'action.devices.types.' + type,
    }
    if trait:
        payload['traits'] = trait
    if manufacturer:
        payload.setdefault('manifest', {})['manufacturer'] = manufacturer
    if product_name:
        payload.setdefault('manifest', {})['productName'] = product_name
    if description:
        payload.setdefault('manifest', {})['deviceDescription'] = description
    r = session.get(model_url)
    if r.status_code == 200:
        click.echo('updating existing device model: %s' % model)
        r = session.put(model_url, data=json.dumps(payload))
    elif r.status_code in (400, 404):
        click.echo('creating new device model')
        r = session.post(model_base_url, data=json.dumps(payload))
    else:
        raise failed_request_exception('failed to check existing model', r)
    if r.status_code != 200:
        raise failed_request_exception('failed to register model', r)
    click.echo(r.text)


@cli.command('register-device')
@click.option('--device', required=True)
@click.option('--model', required=True)
@click.option('--nickname')
@click.pass_context
def register_device(ctx, device, model, nickname):
    session = ctx.obj['SESSION']

    device_base_url = '/'.join([ctx.obj['API_URL'], 'devices'])
    device_url = '/'.join([device_base_url, device])
    payload = {
        'id': device,
        'model_id': model,
    }
    if nickname:
        payload['nickname'] = nickname

    r = session.get(device_url)
    if r.status_code == 200:
        click.echo('updating existing device: %s' % device)
        session.delete(device_url)
        r = session.post(device_base_url, data=json.dumps(payload))
    elif r.status_code in (400, 404):
        click.echo('creating new device')
        r = session.post(device_base_url, data=json.dumps(payload))
    else:
        raise failed_request_exception('failed to check existing device', r)
    if r.status_code != 200:
        raise failed_request_exception('failed to register device', r)
    click.echo(r.text)


@cli.command()
@click.option('--model', 'resource', flag_value='deviceModels', required=True)
@click.option('--device', 'resource', flag_value='devices', required=True)
@click.argument('id')
@click.pass_context
def get(ctx, resource, id):
    session = ctx.obj['SESSION']
    url = '/'.join([ctx.obj['API_URL'], resource, id])
    r = session.get(url)
    if r.status_code != 200:
        raise failed_request_exception('failed to get resource', r)
    click.echo(r.text)


@cli.command()
@click.option('--model', 'resource', flag_value='deviceModels', required=True)
@click.option('--device', 'resource', flag_value='devices', required=True)
@click.pass_context
def list(ctx, resource):
    session = ctx.obj['SESSION']
    url = '/'.join([ctx.obj['API_URL'], resource])
    r = session.get(url)
    if r.status_code != 200:
        raise failed_request_exception('failed to list resources', r)
    click.echo(r.text)


def main():
    cli(obj={})


if __name__ == '__main__':
    main()
