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

from setuptools import find_packages
from setuptools import setup


DEPENDENCIES = [
    'google-auth==0.8.0',
    'googleapis-common-protos==1.5.0',
    'grpcio==1.1.0',
    'requests==2.13.0',
    'requests-oauthlib==0.8.0',
    'six==1.10.0',
    'urllib3[secure]==1.20',
]

def load_test_suite():
    import unittest
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


setup(
    name='google-assistant',
    version='0.0.1',
    author='Google Embedded Assistant team',
    author_email='proppy@google.com',
    description='Google Embedded Assistant Sample client',
    long_description='Sample client for the Google Embedded Assistant gRPC API',
    url='TODO(proppy) add external repo url',
    packages=find_packages(exclude=('tests')),
    namespace_packages=('googlesamples',),
    install_requires=DEPENDENCIES,
    extras_require={
        'MAIN': ['tqdm==4.11.2', 'PyAudio==0.2.10']
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
    keywords='google assistant client sample',
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
