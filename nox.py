# Copyright 2014 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import nox

@nox.session
def lint(session):
    session.interpreter = 'python3.4'
    session.install('docutils', 'flake8')
    session.run('flake8', 'googlesamples', 'tests')
    session.run('python', 'setup.py', 'check',
                '--restructuredtext', '--strict')

@nox.session
@nox.parametrize('python_version', ['2.7', '3.4'])
def unittest(session, python_version):
    session.interpreter = 'python' + python_version
    session.install('pytest')
    session.install('-e', '.[auth_helpers,audio_helpers]')
    session.run('py.test', 'tests')

@nox.session
def protoc(session):
    session.install('grpcio-tools')
    session.run('python', '-m', 'grpc_tools.protoc',
                '--proto_path=proto',
                '--proto_path=googleapis',
                '--python_out=.',
                '--grpc_python_out=.',
                'proto/google/assistant/embedded/v1alpha1/'
                'embedded_assistant.proto')

@nox.session
def release(session):
    session.install('setuptools', 'wheel')
    session.run('python', 'setup.py', 'sdist', 'bdist_wheel')
