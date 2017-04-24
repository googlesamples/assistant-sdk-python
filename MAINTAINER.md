Maintainer guide
================

## Prerequisites

- Install automation tools

        pip install --upgrade nox-automation

## Tasks

- Run lint tool

        nox -s lint

- Run unit tests

        nox -s unittest

- Regenerate the python gRPC stubs

        git clone https://github.com/googleapis/googleapis
        nox -s protoc

- Create a new `google_assistant_sdk` release in `dist`

        nox -s release
