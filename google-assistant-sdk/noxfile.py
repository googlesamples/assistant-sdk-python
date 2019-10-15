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


@nox.session(python=["3"])
def lint(session):
    session.install('pip', 'setuptools')
    session.install('docutils', 'flake8', 'readme_renderer')
    session.run('flake8',
                'googlesamples', 'tests',
                'nox.py', 'setup.py')
    session.run('python', 'setup.py', 'check',
                '--restructuredtext', '--strict')
    session.run('python', '-m', 'json.tool', 'actions.json')


@nox.session(python=['2.7', '3'])
def unittest(session):
    session.install('pip', 'setuptools')
    session.install('pytest', 'future')
    session.install('../google-assistant-grpc/')
    session.install('-e', '.[samples]')
    session.run('py.test', '-k', 'not test_endtoend', 'tests')


@nox.session(python=['2.7', '3'])
def endtoend_test(session):
    session.install('pip', 'setuptools')
    session.install('pytest', 'future')
    session.install('../google-assistant-grpc/')
    session.install('-e', '.[samples]')
    session.run('py.test', '-k', 'test_endtoend', 'tests')


@nox.session
def release(session):
    session.install('pip', 'setuptools', 'wheel')
    session.run('python', 'setup.py', 'sdist', 'bdist_wheel')
