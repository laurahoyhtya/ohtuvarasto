# ohtuvarasto

[![codecov](https://codecov.io/github/laurahoyhtya/ohtuvarasto/graph/badge.svg?token=NJDERU5P1Z)](https://codecov.io/github/laurahoyhtya/ohtuvarasto)

[![GHA workflow badge](https://github.com/laurahoyhtya/ohtuvarasto/actions/workflows/main.yml/badge.svg)](https://github.com/laurahoyhtya/ohtuvarasto/actions)

## Web interface

Install dependencies and start the Flask application:

```sh
uv sync
uv run flask --app src/app.py run
```

Open <http://127.0.0.1:5000> in a browser. Warehouses are kept in memory and
are reset when the application stops.

## Tests

Run the test suite with:

```sh
uv sync
uv run pytest
```
