# Developer guide

Before you push to the `main` branch, please test the code and the documentation locally.

## Unit testing

Run tests locally with the `unittest` package.

```bash
python -m venv venv
venv/bin/pip install --upgrade pip setuptools wheel
venv/bin/pip install -e .[tests]
venv/bin/python -m unittest
```

As soon as you push to the `main` branch, GitHub Actions will take out these unit tests, too.


## Documentation

After locally building the documentation, open `docs/build/index.html` in your browser.

```bash
venv/bin/pip install -e .[docs]
venv/bin/sphinx-apidoc --force --output-dir docs/source critdd
venv/bin/sphinx-build -M html docs/source docs/build
```

As soon as you push to the `main` branch, GitHub Actions will build the documentation, push it to the `gh-pages` branch, and publish the result on GitHub Pages: [https://mirkobunse.github.io/critdd](https://mirkobunse.github.io/critdd)
