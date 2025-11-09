# SDK Publishing Guide

Guide for publishing Concise SDKs to package managers.

## Python SDK (PyPI)

### Prerequisites

```bash
pip install twine build
```

### Build Package

```bash
cd sdk/python-sdk

# Build distribution
python -m build

# This creates:
# - dist/concise_sdk-1.0.0.tar.gz (source)
# - dist/concise_sdk-1.0.0-py3-none-any.whl (wheel)
```

### Test Locally

```bash
# Install in development mode
pip install -e .

# Test import
python -c "from concise import Concise; print('Success')"
```

### Publish to TestPyPI (Testing)

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ concise-sdk
```

### Publish to PyPI (Production)

```bash
# Upload to PyPI
twine upload dist/*

# Users can now install:
# pip install concise-sdk
```

### PyPI Credentials

Set up `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-...your-token...

[testpypi]
username = __token__
password = pypi-...your-test-token...
```

---

## TypeScript SDK (NPM)

### Prerequisites

```bash
cd sdk/typescript-sdk
npm install
```

### Build Package

```bash
# Compile TypeScript
npm run build

# This creates dist/ folder with:
# - index.js (compiled JS)
# - index.d.ts (type definitions)
# - All source files compiled
```

### Test Locally

```bash
# Link locally
npm link

# In another project:
npm link concise-sdk

# Test import
node -e "const { Concise } = require('concise-sdk'); console.log('Success');"
```

### Publish to NPM (Testing)

```bash
# Login to npm
npm login

# Publish with tag
npm publish --tag beta

# Users can install:
# npm install concise-sdk@beta
```

### Publish to NPM (Production)

```bash
# Publish
npm publish

# Users can now install:
# npm install concise-sdk
```

### NPM Credentials

```bash
# Login (one-time)
npm login

# Or use token
npm config set //registry.npmjs.org/:_authToken YOUR_NPM_TOKEN
```

---

## Version Management

### Python SDK

Update version in `setup.py`:

```python
setup(
    name="concise-sdk",
    version="1.0.1",  # Increment here
    ...
)
```

### TypeScript SDK

Update version in `package.json`:

```json
{
  "name": "concise-sdk",
  "version": "1.0.1",  // Increment here
  ...
}
```

### Semantic Versioning

Follow semver (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes (e.g., 1.0.0 → 2.0.0)
- **MINOR**: New features, backward compatible (e.g., 1.0.0 → 1.1.0)
- **PATCH**: Bug fixes (e.g., 1.0.0 → 1.0.1)

---

## Pre-release Checklist

- [ ] All code complete and tested
- [ ] README.md updated
- [ ] Examples work
- [ ] Version bumped
- [ ] CHANGELOG.md updated
- [ ] License file present
- [ ] No sensitive data in code

---

## Publishing Commands (Quick Reference)

### Python

```bash
cd sdk/python-sdk
python -m build
twine upload dist/*
```

### TypeScript

```bash
cd sdk/typescript-sdk
npm run build
npm publish
```

---

## Post-publishing

### Python

Check package page:
- https://pypi.org/project/concise-sdk/

### TypeScript

Check package page:
- https://www.npmjs.com/package/concise-sdk

---

## Automated Publishing (CI/CD)

### GitHub Actions - Python

```yaml
name: Publish Python SDK

on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install build twine
      - run: python -m build
        working-directory: sdk/python-sdk
      - run: twine upload dist/*
        working-directory: sdk/python-sdk
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
```

### GitHub Actions - TypeScript

```yaml
name: Publish TypeScript SDK

on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          registry-url: 'https://registry.npmjs.org'
      - run: npm install
        working-directory: sdk/typescript-sdk
      - run: npm run build
        working-directory: sdk/typescript-sdk
      - run: npm publish
        working-directory: sdk/typescript-sdk
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

---

## Troubleshooting

### Python: "File already exists"

```bash
# Clear old builds
rm -rf dist/ build/ *.egg-info

# Rebuild
python -m build
```

### TypeScript: "Package name taken"

Change package name in `package.json` to something unique:

```json
{
  "name": "@your-org/concise-sdk"
}
```

### Both: "Authentication failed"

Verify credentials:
- Python: Check `~/.pypirc`
- TypeScript: Run `npm whoami`

---

## Next Steps

After publishing:

1. **Documentation**: Update docs.concise.dev with SDK examples
2. **Announcement**: Tweet/blog about SDK release
3. **Examples**: Create GitHub repo with example projects
4. **Support**: Monitor GitHub issues for SDK questions
5. **Versioning**: Plan next version features

---

## Quick Start for VibeCon

For demo purposes, you can skip publishing and show:

1. **Local installation**: `pip install -e .` or `npm link`
2. **Example code**: Run examples/ files
3. **GitHub**: Push SDKs to GitHub repo
4. **Demo**: "Here's how developers will use our API..."

Publishing to PyPI/NPM can be done post-VibeCon.
