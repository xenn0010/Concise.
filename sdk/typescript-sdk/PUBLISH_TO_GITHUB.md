# Quick Guide: Publish to GitHub Packages

Your TypeScript SDK is configured to publish as `@xenn0010/concise-sdk` to GitHub Packages.

## Step 1: Create GitHub Personal Access Token

**IMPORTANT**: Your token MUST have these exact scopes or publishing will fail with "permission_denied".

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name it: "NPM Package Publishing"
4. **Select EXACTLY these scopes** (this is critical):
   - ✅ `write:packages` - Upload packages to GitHub Package Registry
   - ✅ `read:packages` - Download packages from GitHub Package Registry
   - ✅ `repo` (if your repository is private)
5. Click "Generate token"
6. **COPY THE TOKEN** (you won't see it again!)

**Common mistake**: Creating a token without `write:packages` will cause error:
```
403 Forbidden - Permission permission_denied: The token provided does not match expected scopes.
```

## Step 2: Login to GitHub Packages

```bash
cd /home/yab/Concise/sdk/typescript-sdk

npm login --scope=@xenn0010 --registry=https://npm.pkg.github.com
```

When prompted, enter:
- **Username**: `xenn0010`
- **Password**: `YOUR_PERSONAL_ACCESS_TOKEN` (paste the token from Step 1)
- **Email**: `your-github-email@example.com`

## Step 3: Publish

```bash
npm publish
```

That's it! Your package will be published to:
`https://github.com/xenn0010?tab=packages`

## Step 4: Make Package Public (Optional)

By default, packages are private. To make it public:

1. Go to https://github.com/xenn0010?tab=packages
2. Click on `concise-sdk`
3. Click "Package settings" (gear icon)
4. Scroll to "Danger Zone"
5. Click "Change visibility" → "Public"

## How Users Install Your Package

### Option 1: From GitHub Packages (if public)

Users create `.npmrc` in their project:
```
@xenn0010:registry=https://npm.pkg.github.com
```

Then install:
```bash
npm install @xenn0010/concise-sdk
```

### Option 2: Direct from GitHub (works immediately)

```bash
npm install git+https://github.com/xenn0010/concise-sdk.git
```

## Troubleshooting

**404 Not Found**
- Make sure you pushed the code to `https://github.com/xenn0010/concise-sdk`
- Create the repository on GitHub if it doesn't exist

**401 Unauthorized**
- Regenerate your Personal Access Token
- Make sure it has `write:packages` permission
- Run `npm login` again

**Already published**
- Increment version in `package.json` (e.g., 1.1.1)
- Run `npm publish` again

## Current Configuration

✅ Package name: `@xenn0010/concise-sdk`
✅ Version: `1.1.0`
✅ Registry: GitHub Packages
✅ Repository: `https://github.com/xenn0010/concise-sdk`

Ready to publish! 🚀
