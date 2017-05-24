Maintainer guide
================

## Prerequisites

- Install automation tools

        pip install --upgrade nox-automation

## Tasks

- Install package with local modifications

        pip install -e .[samples]

- Run lint tool

        nox -s lint

- Run unit tests

        nox -s unittest

- Create a new `google_assistant_sdk` release in `dist`

        nox -s release
