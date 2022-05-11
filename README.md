# BFF-CLI
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.8](https://img.shields.io/badge/python-3.8-green?style=for-the-badge)](https://www.python.org/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/PilotDataPlatform/bff-cli/CI/develop?style=for-the-badge)](https://github.com/PilotDataPlatform/bff-cli/actions/workflows/main.yml)

[![codecov](https://img.shields.io/codecov/c/github/PilotDataPlatform/bff-cli?style=for-the-badge)](https://codecov.io/gh/PilotDataPlatform/bff-cli)
## About
The backend for the command line interface.
### Built With
- Python
- FastAPI
## Getting Started

### Prerequisites
- [Poetry](https://python-poetry.org/) dependency manager.
- Vault connection credentials or custom-set environment variables.

### Installation
#### Using Docker
1. Add environment variables into `.env`.
2. Run Docker compose with environment variables.

       docker-compose up

2. Find service locally at `http://localhost:5080/`.

#### Without Docker
1. Install [Poetry](https://python-poetry.org/docs/#installation).
2. Configure access to internal package registry.

       poetry config virtualenvs.create false

3. Install dependencies.

       poetry install --no-dev --no-root --no-interaction

4. Add environment variables into `.env`.
5. Run application.

       poetry run python run.py

6. Find service locally at `http://localhost:5080/`.

## Usage
Swagger API documentation can be found locally at `http://localhost:5080/v1/api-doc`.
