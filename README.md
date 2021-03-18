## Setup and Run

Add  `.env` file containing at least `SECRET_KEY` (any string will do for developmen):

```
SECRET_KEY=<...>
```

Send email functionality works through AWS Simple Email Service. To make it work provide required variables in `.env` file:

```
AWS_ACCESS_KEY_ID=<...>
AWS_SECRET_ACCESS_KEY=<...>
AWS_SES_REGION=<...>
AWS_SES_EMAIL_SOURCE=<...>
```

Run and setup the project with:

```sh
make setup
```

Navigate to `localhost:8002/admin` to create treasure object with desired coordintes.

## Run tests

```sh
make test
```

## Check test coverate

```sh
make coverage
```

## Lint and Fix

For linting `flake8` is used. `black` and `isort` are used for automatic code formatting.

```sh
make lint
```

```sh
make fix
```

## Verify API manually:

This will install `httpie` and other dev packages:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
```

Register new user:

```sh
http localhost:8002/api/auth/register/ username=someone email=someone@example.com password=123
```

Hunt treasure anonymously:

```sh
http localhost:8002/api/treasure_hunt.json/ latitude=10.44 longitude=35.432 email=user@example.com
```

Get Auth Token:

```sh
http localhost:8002/api/auth/token/login/ username=someone password=123
```

Hunt treasure as a registered user:

```sh
http localhost:8002/api/treasure_hunt.json/ latitude=10.44 longitude=35.432 Authorization:"Bearer <token>"
```

## Notes

For demonstration purposes API is limited to accept 20 requests per minute for anonymous and registered users.
