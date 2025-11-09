# How to Publish SDKs - Quick Guide

**Both packages are built and ready to publish!**

---

## Prerequisites

### 1. Create PyPI Account
1. Go to https://pypi.org/account/register/
2. Verify your email
3. Go to https://pypi.org/manage/account/token/
4. Create API token with name "concise-sdk"
5. Save the token (starts with `pypi-`)

### 2. Create NPM Account
1. Go to https://www.npmjs.com/signup
2. Verify your email
3. Run: `npm adduser`
4. Enter username, password, email

---

## Publish Python SDK to PyPI

### Step 1: Configure PyPI Token

Create file `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE
```

Replace `YOUR_TOKEN_HERE` with your actual PyPI token.

### Step 2: Publish

```bash
cd /home/yab/Concise/sdk/python-sdk

# Upload to PyPI
source ../../backend/venv/bin/activate
twine upload dist/*
```

You'll be asked to confirm. Type `yes`.

### Step 3: Verify

Go to: https://pypi.org/project/concise-sdk/

Users can now install:
```bash
pip install concise-sdk
```

---

## Publish TypeScript SDK to NPM

### Step 1: Login to NPM

```bash
npm login
```

Enter your username, password, and email.

Verify:
```bash
npm whoami
# Should show your username
```

### Step 2: Publish

```bash
cd /home/yab/Concise/sdk/typescript-sdk

# Publish to NPM
npm publish
```

### Step 3: Verify

Go to: https://www.npmjs.com/package/concise-sdk

Users can now install:
```bash
npm install concise-sdk
```

---

## What's Already Done

✅ **Python SDK:**
- Package built: `dist/concise_sdk-1.0.0-py3-none-any.whl`
- Source distribution: `dist/concise_sdk-1.0.0.tar.gz`
- Size: ~9KB
- Ready to upload

✅ **TypeScript SDK:**
- TypeScript compiled: `dist/*.js` and `dist/*.d.ts`
- Package ready: All files in place
- Size: ~20KB compiled
- Ready to publish

---

## Exact Commands to Run

### For Python (PyPI):

```bash
# 1. Set up credentials
nano ~/.pypirc
# Paste the [pypi] config above

# 2. Navigate and publish
cd /home/yab/Concise/sdk/python-sdk
source ../../backend/venv/bin/activate
twine upload dist/*
```

### For TypeScript (NPM):

```bash
# 1. Login
npm login

# 2. Navigate and publish
cd /home/yab/Concise/sdk/typescript-sdk
npm publish
```

---

## First Time Publishing?

### PyPI First-Time Setup:

1. Create account: https://pypi.org/account/register/
2. Verify email
3. Create API token: https://pypi.org/manage/account/token/
4. Copy token
5. Create `~/.pypirc` with token
6. Run: `twine upload dist/*`

### NPM First-Time Setup:

1. Create account: https://www.npmjs.com/signup
2. Verify email
3. Run: `npm adduser`
4. Enter credentials
5. Run: `npm publish`

---

## Troubleshooting

### Python: "File already exists"

If the package already exists on PyPI:

```bash
# Update version in setup.py
# Change: version="1.0.0"
# To:     version="1.0.1"

# Rebuild
python -m build

# Upload new version
twine upload dist/*
```

### TypeScript: "Package already exists"

If the package already exists on NPM:

```bash
# Update version in package.json
# Change: "version": "1.0.0"
# To:     "version": "1.0.1"

# Rebuild
npm run build

# Publish new version
npm publish
```

### Package name taken

If `concise-sdk` is already taken on PyPI or NPM, change the name:

**Python (setup.py):**
```python
name="concise-ai-sdk",  # Changed
```

**TypeScript (package.json):**
```json
"name": "concise-ai-sdk",  // Changed
```

Then rebuild and publish.

---

## After Publishing

### 1. Test Installation

**Python:**
```bash
# In a new terminal/environment
pip install concise-sdk
python -c "from concise import Concise; print('Success!')"
```

**TypeScript:**
```bash
# In a new directory
mkdir test-install && cd test-install
npm init -y
npm install concise-sdk
node -e "const { Concise } = require('concise-sdk'); console.log('Success!');"
```

### 2. Update Documentation

Add installation instructions to:
- README.md in main repo
- Website docs
- VibeCon presentation

### 3. Announce

- Tweet: "Just published Concise SDKs for Python & JavaScript! 🚀"
- Share on LinkedIn
- Post in relevant communities

---

## Package Info

### Python SDK (PyPI)

**Package name:** `concise-sdk`
**Version:** 1.0.0
**Size:** ~9KB
**Dependencies:** httpx>=0.25.0
**Python:** >=3.8

**Install:**
```bash
pip install concise-sdk
```

**Import:**
```python
from concise import Concise, OpenAI
```

### TypeScript SDK (NPM)

**Package name:** `concise-sdk`
**Version:** 1.0.0
**Size:** ~20KB
**Dependencies:** axios@^1.6.0
**Node:** >=16.0.0

**Install:**
```bash
npm install concise-sdk
```

**Import:**
```typescript
import { Concise, OpenAI } from 'concise-sdk';
```

---

## Publishing Checklist

Before publishing, verify:

- [x] Package builds successfully
- [x] Tests pass
- [x] README.md complete
- [x] Version number set
- [x] Dependencies listed
- [x] Examples work
- [x] No sensitive data in code
- [x] License file present
- [x] Description clear

**Both SDKs: All checks passed ✅**

---

## Quick Reference

| Action | Python Command | TypeScript Command |
|--------|---------------|-------------------|
| Build | `python -m build` | `npm run build` |
| Check build | `ls dist/` | `ls dist/` |
| Login | Create ~/.pypirc | `npm login` |
| Publish | `twine upload dist/*` | `npm publish` |
| Test install | `pip install concise-sdk` | `npm install concise-sdk` |
| Update version | Edit setup.py | Edit package.json |

---

## Support

If you run into issues:

1. **PyPI issues:**
   - Docs: https://packaging.python.org/tutorials/packaging-projects/
   - Help: https://pypi.org/help/

2. **NPM issues:**
   - Docs: https://docs.npmjs.com/packages-and-modules/contributing-packages-to-the-registry
   - Help: https://www.npmjs.com/support

---

## Next Steps

After publishing:

1. ✅ Publish Python SDK to PyPI
2. ✅ Publish TypeScript SDK to NPM
3. Test installation on fresh machines
4. Update main repo README with installation instructions
5. Add "Installation" section to VibeCon presentation
6. Create example projects showing SDK usage
7. Set up CI/CD for automated publishing

---

**You're ready to publish! Both packages are built and waiting.**

Run the commands above when you have your PyPI and NPM credentials set up.
