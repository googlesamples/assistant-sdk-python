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
import os.path

install_requires = [
    'google-auth-oauthlib[tool]>=0.1.0'
]

samples_packages = [
    'grpc'
]


def samples_requirements():
    for p in samples_packages:
        with io.open(os.path.join('googlesamples', 'assistant', p,
                                  'requirements.txt')) as f:
            for p in f:
                yield p.strip()


with io.open('README.rst', 'r') as fh:
    long_description = fh.read()

setup(
    name='google-assistant-sdk',
    version='0.6.0',
    author='Google Assistant SDK team',
    author_email='proppy+assistant-sdk@google.com',
    description='Samples and Tools the Google Assistant SDK',
    long_description=long_description,
    url='https://github.com/googlesamples/assistant-sdk-python',
    packages=find_packages(exclude=['tests*']),
    namespace_packages=[
        'googlesamples',
        'googlesamples.assistant',
    ],
    install_requires=install_requires,
    extras_require={
        'samples': list(samples_requirements()),
    },
    entry_points={
        'console_scripts': [
            'googlesamples-assistant-audiotest'
            '=googlesamples.assistant.grpc.audio_helpers:main',
            'googlesamples-assistant-devicetool'
            '=googlesamples.assistant.grpc.devicetool:main',
            'googlesamples-assistant-pushtotalk'
            '=googlesamples.assistant.grpc.pushtotalk:main [samples]',
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
