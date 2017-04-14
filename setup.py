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

from setuptools import setup, find_packages

install_requires = [
  'googleapis-common-protos[grpc]>=1.5.2, <2.0dev',
  'grpcio>=1.0.2, <2.0dev',
]

auth_helpers_requires = [
    'google-auth-oauthlib==0.0.1',
    'urllib3[secure]==1.20',
]

samples_requires = [
    'six==1.10.0',
    'PyAudio==0.2.10',
] + auth_helpers_requires


def load_test_suite():
    import unittest
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


setup(
    name='google-assistant-sdk',
    version='0.1',
    author='Google Assistant SDK team',
    author_email='proppy@google.com',
    description='Python SDK for the Google Assistant API',
    long_description=('Python bindings and samples '
                      'for the Google Assistant API'),
    url='https://github.com/googlesamples/google-assistant-sdk-python',
    packages=find_packages(exclude=('tests')),
    namespace_packages=[
        'google',
        'google.assistant',
        'googlesamples',
    ],
    install_requires=install_requires,
    extras_require={
        'MAIN': samples_requires,
        'samples': samples_requires,
        'auth_helpers': auth_helpers_requires,
    },
    setup_requires=['flake8'],
    tests_require=['flake8'],
    test_suite='setup.load_test_suite',
    entry_points={
        'console_scripts': [
            'googlesamples-assistant'
            '=googlesamples.assistant.__main__:main [MAIN]'
        ],
    },
    license='Apache 2.0',
    keywords='google assistant api sample',
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
