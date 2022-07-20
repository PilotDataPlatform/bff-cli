# Contribution Guide

## Bug Reports

For bug reports, [submit an issue](https://github.com/PilotDataPlatform/sandbox/issues).

## Pull Requests

1. Fork the [main repository](https://github.com/PilotDataPlatform/sandbox).
2. Create a feature branch to hold your changes.
3. Work on the changes in your feature branch.
4. Add [Unit Tests](#unit-tests).
5. Follow the Getting Started instruction to set up the service.
6. Create the Alembic [migration](#migrations) environment only when it's needed.
7. Test the code and create a pull request.

### Migrations

To create a new migration with Alembic, run:

```
docker compose run --rm alembic revision -m "Migration name"
```

### Unit Tests

When adding a new feature or fixing a bug, unit tests are necessary to write. Currently we use Pytest as our testing framework and all test cases are written under the `tests` directory.

Some services may need extra dependencies to run tests. Example:

```
docker run redis
```

Run test cases with Poetry and Pytest:
```
poetry run pytest
```
