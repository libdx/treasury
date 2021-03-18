## Run

```sh
make up-build
```

## Run tests

```sh
make test
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

Hunt treasure authenticated:

```sh
http localhost:8002/api/treasure_hunt.json/ latitude=10.44 longitude=35.432 Authorization:"Bearer <token>"
```
