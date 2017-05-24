Maintainer guide
================

## Prerequisites

- Install automation tools

        pip install --upgrade nox-automation

## Tasks

- Install package with local modifications

        pip install -e .

- Regenerate the python gRPC stubs

        git clone https://github.com/googleapis/googleapis
        nox -s protoc

- Create a new `google_assistant_grpc` release in `dist`

        nox -s release
