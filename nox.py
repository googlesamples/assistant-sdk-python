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
import os.path
import tempfile


@nox.session
def lint(session):
    session.interpreter = 'python3.4'
    session.install('pip', 'setuptools')
    session.install('docutils', 'flake8')
    session.run('flake8',
                'samples/grpc/googlesamples', 'samples/grpc/tests',
                'sdk/grpc/setup.py',
                'nox.py', 'setup.py')
    session.run('python', 'setup.py', 'check',
                '--restructuredtext', '--strict')
    session.run('python', 'sdk/grpc/setup.py', 'check',
                '--restructuredtext', '--strict')


@nox.session
@nox.parametrize('python_version', ['2.7', '3.4'])
def unittest(session, python_version):
    session.interpreter = 'python' + python_version
    session.install('pip', 'setuptools')
    session.install('pytest')
    session.install('-e', '.[samples]')
    session.run('py.test', 'samples/grpc/tests')


@nox.session
@nox.parametrize('python_version', ['2.7', '3.4'])
def endtoend_test(session, python_version):
    session.interpreter = 'python' + python_version
    session.install('pip', 'setuptools')
    session.install('-e', '.[samples]')
    temp_dir = tempfile.mkdtemp()
    audio_out_file = os.path.join(temp_dir, 'out.raw')
    session.run('python', '-m', 'googlesamples.assistant',
                '-i', 'tests/data/whattimeisit.riff',
                '-o', audio_out_file)
    session.run('test', '-s', audio_out_file)


@nox.session
def protoc(session):
    session.install('pip', 'setuptools')
    session.install('grpcio-tools')
    session.run('python', '-m', 'grpc_tools.protoc',
                '--proto_path=googleapis',
                '--python_out=.',
                '--grpc_python_out=sdk/grpc/',
                'googleapis/google/assistant/embedded/v1alpha1/'
                'embedded_assistant.proto')


@nox.session
def release(session):
    session.install('pip', 'setuptools', 'wheel')
    session.run('python', 'setup.py', 'sdist', 'bdist_wheel')
    session.run('python', 'sdk/grpc/setup.py', 'sdist', 'bdist_wheel')
