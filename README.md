# BFF-CLI
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.8](https://img.shields.io/badge/python-3.8-green?style=for-the-badge)](https://www.python.org/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/PilotDataPlatform/bff-cli/CI/develop?style=for-the-badge)](https://github.com/PilotDataPlatform/bff-cli/actions/workflows/main.yml)

[![codecov](https://img.shields.io/codecov/c/github/PilotDataPlatform/bff-cli?style=for-the-badge)](https://codecov.io/gh/PilotDataPlatform/bff-cli)
## Getting Started
The backend for the command line interface.
### Built With
- Python
- FastAPI
## Getting Started

### Prerequisites
This project is using [Poetry](https://python-poetry.org/docs/#installation) to handle the dependencies.

    curl -sSL https://install.python-poetry.org | python3 -

### Installation & Quick Start

1. Clone the project.

       git clone https://github.com/PilotDataPlatform/sandbox.git

2. Install dependencies.

       poetry install

3. Install any OS level dependencies.

       apt install <foo>
       brew install <bar>

5. Add environment variables into `.env` in case it's needed. Use `.env.schema` as a reference.


6. Run any initial scripts, migrations or database seeders.

       poetry run alembic upgrade head

7. Run application.

       poetry run python run.py

### Startup using Docker

This project can also be started using [Docker](https://www.docker.com/get-started/).

1. To build and start the service within the Docker container run.

       docker compose up

2. Migrations should run automatically on previous step. They can also be manually triggered:

       docker compose run --rm alembic upgrade head

## Resources

* [Pilot Platform API Documentation](https://pilotdataplatform.github.io/api-docs/)
* [Pilot Platform Helm Charts](https://github.com/PilotDataPlatform/helm-charts/)

## Contribution

You can contribute the project in following ways:

* Report a bug
* Suggest a feature
* Open a pull request for fixing issues or adding functionality. Please consider
  using [pre-commit](https://pre-commit.com) in this case.
* For general guidelines how to contribute to the project, please take a look at the [contribution guides](CONTRIBUTING.md).
