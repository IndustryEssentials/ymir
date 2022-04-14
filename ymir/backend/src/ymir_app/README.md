# ymir-app

## develop

one time:

```bash
pip install -r dev-requirements.txt
pre-commit install
```

Note that:

pre-commit will run black/mypy/flake8 validation before git commit.

Fix all the issues before you commit.

## test

```bash
tox
```

## release

one time:

```bash
pip install bump2version==0.5.11
```

every time you push:

```bash
bumpversion patch
git push origin master --tags
```
