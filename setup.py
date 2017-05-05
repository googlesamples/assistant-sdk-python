# Copyright 2017 Google Inc.
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

from setuptools import setup, find_packages
import io

install_requires = [
    'googleapis-common-protos==1.5.2',
    'grpcio==1.2.1',
]

auth_helpers_requires = [
    'google-auth-oauthlib==0.0.1',
    'urllib3[secure]==1.20',
]

audio_helpers_requires = [
    'sounddevice==0.3.7',
]

samples_requires = [
    'click==6.7',
    'tenacity==4.1.0',
] + auth_helpers_requires + audio_helpers_requires

with io.open('README.rst', 'r') as fh:
    long_description = fh.read()

setup(
    name='google-assistant-sdk',
    version='0.2.1',
    author='Google Assistant SDK team',
    author_email='proppy+assistant-sdk@google.com',
    description='Samples and bindings for the Google Assistant API',
    long_description=long_description,
    url='https://github.com/googlesamples/assistant-sdk-python',
    packages=find_packages(exclude=['tests*']),
    namespace_packages=[
        'google',
        'google.assistant',
        'google.assistant.embedded',
        'googlesamples',
    ],
    install_requires=install_requires,
    extras_require={
        'samples': samples_requires,
        'auth_helpers': auth_helpers_requires,
        'audio_helpers': audio_helpers_requires,
    },
    entry_points={
        'console_scripts': [
            'googlesamples-assistant'
            '=googlesamples.assistant.__main__:main [samples]',
            'googlesamples-assistant-auth'
            '=googlesamples.assistant.auth_helpers.__main__:main [samples]',
        ],
    },
    license='Apache 2.0',
    keywords='google assistant api sdk sample',
    classifiers=(
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
    ),
)
