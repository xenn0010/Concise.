# Publishing TypeScript SDK to GitHub Packages

## Prerequisites

1. GitHub account
2. Personal Access Token with `write:packages` permission

## Step-by-Step Guide

### 1. Create GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: "NPM Package Publishing"
4. Select scopes:
   - ✅ `write:packages` (Upload packages to GitHub Package Registry)
   - ✅ `read:packages` (Download packages from GitHub Package Registry)
   - ✅ `repo` (if your repo is private)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)

### 2. Update package.json

Replace `GITHUB_USERNAME` with your actual GitHub username:

```json
{
  "name": "@GITHUB_USERNAME/concise-sdk",
  "version": "1.1.0",
  "publishConfig": {
    "registry": "https://npm.pkg.github.com"
  },
  "repository": {
    "type": "git",
    "url": "git+https://github.com/GITHUB_USERNAME/concise-sdk.git"
  }
}
```

### 3. Update .npmrc

Replace `GITHUB_USERNAME` in `.npmrc`:

```
@GITHUB_USERNAME:registry=https://npm.pkg.github.com
```

### 4. Login to GitHub Packages

```bash
cd /home/yab/Concise/sdk/typescript-sdk
npm login --scope=@GITHUB_USERNAME --registry=https://npm.pkg.github.com
```

When prompted:
- **Username**: Your GitHub username
- **Password**: Your Personal Access Token (from step 1)
- **Email**: Your GitHub email

### 5. Publish to GitHub Packages

```bash
npm publish
```

### 6. Users Install Your Package

Users will need to add this to their `.npmrc`:

```
@GITHUB_USERNAME:registry=https://npm.pkg.github.com
```

Then install:

```bash
npm install @GITHUB_USERNAME/concise-sdk
```

## Alternative: Make Package Public

By default, GitHub Packages are private. To make it public:

1. Go to your package page: `https://github.com/GITHUB_USERNAME?tab=packages`
2. Click on your package
3. Click "Package settings"
4. Scroll to "Danger Zone"
5. Click "Change visibility" → "Public"

## Troubleshooting

**Error: 404 Not Found**
- Make sure your GitHub username is correct in package.json
- Make sure you're logged in with correct token

**Error: 401 Unauthorized**
- Regenerate your Personal Access Token
- Make sure it has `write:packages` permission
- Run `npm login` again

**Error: Package already exists**
- Increment version in package.json
- Or delete the old package from GitHub

## Next Steps

Once published, update your main README to include:

```markdown
## Installation

For now, install from GitHub Packages:

1. Create `.npmrc` in your project root:
   ```
   @GITHUB_USERNAME:registry=https://npm.pkg.github.com
   ```

2. Install:
   ```bash
   npm install @GITHUB_USERNAME/concise-sdk
   ```

(Coming soon to NPM registry!)
```
