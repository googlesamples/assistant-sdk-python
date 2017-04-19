Maintainer guide
================

## Prerequisites

- Install the gRPC tools.

        env/bin/pip install grpcio-tools

- Check out googleapis/googleapis repo.

        git clone https://github.com/googleapis/googleapis

## Tasks

- Run lint tool

        env/bin/python setup.py flake8

- Run unit tests

        env/bin/python setup.py test

- Regenerate the python gRPC stubs

        env/bin/python -m grpc_tools.protoc --proto_path=proto --proto_path=googleapis --python_out=. --grpc_python_out=. proto/google/assistant/embedded/v1alpha1/embedded_assistant.proto
