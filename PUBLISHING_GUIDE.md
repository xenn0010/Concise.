# Publishing Guide - Concise SDK v1.1.0

Complete instructions for publishing both Python and TypeScript SDKs to package registries.

## Pre-Publishing Checklist

- [x] Version bumped to 1.1.0 in both SDKs
- [x] READMEs updated with TALE features
- [x] Code built successfully
- [ ] Tests passing (run before publishing)
- [ ] Changelog updated (create if needed)
- [ ] Git tags created

## Python SDK - PyPI Publishing

### 1. Prerequisites

Ensure you have the required tools:

```bash
pip install --upgrade build twine
```

### 2. Build the Package

```bash
cd sdk/python-sdk

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build source distribution and wheel
python -m build
```

This creates:
- `dist/concise-sdk-1.1.0.tar.gz` (source distribution)
- `dist/concise_sdk-1.1.0-py3-none-any.whl` (wheel)

### 3. Test the Build Locally

```bash
# Install in a test environment
pip install dist/concise_sdk-1.1.0-py3-none-any.whl

# Quick test
python -c "from concise import Concise; print('Import successful')"
python -c "from concise.types import TALEOptimizeResult; print('TALE types available')"
```

### 4. Upload to Test PyPI (Optional but Recommended)

```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ concise-sdk
```

### 5. Upload to Production PyPI

```bash
# Upload to production PyPI
twine upload dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your PyPI API token (starts with `pypi-`)

### 6. Verify Publication

```bash
# Wait 1-2 minutes for PyPI to index
pip install --upgrade concise-sdk

# Verify version
python -c "import concise; print(concise.__version__ if hasattr(concise, '__version__') else 'Version check needed')"
```

### 7. Create Git Tag

```bash
cd /home/yab/Concise
git tag -a python-v1.1.0 -m "Python SDK v1.1.0 - TALE Integration"
git push origin python-v1.1.0
```

---

## TypeScript SDK - NPM Publishing

### 1. Prerequisites

Ensure you're logged into NPM:

```bash
npm whoami
# If not logged in:
npm login
```

### 2. Build the Package

```bash
cd sdk/typescript-sdk

# Clean previous builds
rm -rf dist/

# Build TypeScript
npm run build
```

This compiles TypeScript to `dist/` directory with:
- `dist/index.js`
- `dist/index.d.ts`
- `dist/client.js`
- `dist/types.js`
- etc.

### 3. Test the Build Locally

```bash
# Link package locally
npm link

# Test in another directory
cd /tmp
npm link concise-sdk

# Quick test
node -e "const { Concise } = require('concise-sdk'); console.log('Import successful');"
```

### 4. Publish to NPM

```bash
cd sdk/typescript-sdk

# Dry run to check what will be published
npm publish --dry-run

# Publish to NPM
npm publish
```

If your package is scoped (e.g., `@concise/sdk`), use:
```bash
npm publish --access public
```

### 5. Verify Publication

```bash
# Wait 1-2 minutes for NPM to index
npm view concise-sdk version

# Install and test
npm install concise-sdk@1.1.0

# Verify
node -e "const { Concise } = require('concise-sdk'); console.log('Version 1.1.0 installed');"
```

### 6. Create Git Tag

```bash
cd /home/yab/Concise
git tag -a typescript-v1.1.0 -m "TypeScript SDK v1.1.0 - TALE Integration"
git push origin typescript-v1.1.0
```

---

## Post-Publishing Tasks

### 1. Update Documentation Site

If you have a documentation site (docs.concise.dev), update it with:
- New TALE examples
- API reference for new methods
- Migration guide for v1.0 → v1.1

### 2. Announce the Release

Create release notes highlighting:
- **New Feature**: TALE output optimization (60-70% reduction)
- **Breaking Changes**: None (backward compatible)
- **Upgrade Instructions**: Just update package version

Example announcement:

```markdown
# Concise SDK v1.1.0 - Output Optimization with TALE

We're excited to announce Concise SDK v1.1.0 with TALE (Token-Budget-Aware LLM Reasoning) integration!

## What's New

- **Output token reduction**: 60-70% fewer output tokens
- **Full-stack optimization**: Combined input + output = 70% total savings
- **Two new methods**: `optimize_for_output()` and `validate_output()`
- **LLM-agnostic**: Works with GPT-4, Claude, Gemini, all models

## Upgrade

**Python:**
```bash
pip install --upgrade concise-sdk
```

**TypeScript:**
```bash
npm update concise-sdk
```

## Quick Example

See TALE_EXAMPLES.md for complete examples!
```

### 3. Social Media / Blog Post

Share on:
- Twitter/X
- LinkedIn
- Reddit (r/MachineLearning, r/LocalLLaMA)
- Hacker News (if appropriate)

Key message:
> "Full-stack LLM cost optimization: 50% input compression + 70% output reduction = 70% total API cost savings. Works with any LLM."

### 4. Create GitHub Release

```bash
# On GitHub, create a release with:
- Tag: v1.1.0
- Title: "v1.1.0 - TALE Output Optimization"
- Description: Copy from CHANGELOG or SDK_UPGRADE_COMPLETE.md
- Attach: Built distributions (optional)
```

---

## Troubleshooting

### Python Publishing Issues

**Issue:** `twine: command not found`
```bash
pip install --upgrade twine
```

**Issue:** `Invalid credentials`
- Use `__token__` as username
- Use your PyPI token as password
- Generate token at: https://pypi.org/manage/account/token/

**Issue:** `Package already exists`
- You cannot re-upload the same version
- Increment version number and rebuild

### TypeScript Publishing Issues

**Issue:** `npm ERR! 403 Forbidden`
```bash
npm login
npm whoami  # Verify you're logged in
```

**Issue:** `npm ERR! You do not have permission`
- Check package name isn't taken: `npm view concise-sdk`
- Use scoped package: `@yourusername/concise-sdk`

**Issue:** `EBADENGINE Unsupported engine`
- Check `package.json` engines field
- Update Node.js version

---

## Quick Reference

### Python SDK
```bash
cd sdk/python-sdk
python -m build
twine upload dist/*
```

### TypeScript SDK
```bash
cd sdk/typescript-sdk
npm run build
npm publish
```

### Verify Both
```bash
# Python
pip install --upgrade concise-sdk
python -c "from concise import Concise; c = Concise(); print('Python SDK ready')"

# TypeScript
npm install concise-sdk@latest
node -e "const { Concise } = require('concise-sdk'); console.log('TypeScript SDK ready');"
```

---

## Rollback Plan

If critical issues are found after publishing:

### Python
1. Yank the release (doesn't delete, just marks as broken):
   ```bash
   # Contact PyPI support or use web interface
   ```
2. Fix issue and publish v1.1.1

### TypeScript
1. Deprecate the version:
   ```bash
   npm deprecate concise-sdk@1.1.0 "Critical bug, use 1.1.1 instead"
   ```
2. Fix issue and publish v1.1.1

---

## Success Metrics

After publishing, monitor:
- Download counts (PyPI stats, NPM stats)
- GitHub stars/forks
- Issue reports
- User feedback

**Goal**: Validate that TALE integration provides real value to users and results in measurable cost savings.

---

## Next Steps After v1.1.0

Future features to consider:
1. OpenAI proxy auto-TALE (automatically apply TALE to all requests)
2. Adaptive strategy improvements (learn from user patterns)
3. Multi-turn conversation optimization
4. Streaming support for TALE
5. Custom budget templates per use case

For now, focus on:
- Gathering user feedback on TALE
- Measuring real-world cost savings
- Improving documentation based on user questions
