#!/bin/bash

# SDK Publishing Script
# Run this when you're ready to publish both SDKs

set -e  # Exit on error

echo "========================================================================"
echo "CONCISE SDK PUBLISHING SCRIPT"
echo "========================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "python-sdk" ] || [ ! -d "typescript-sdk" ]; then
    echo -e "${RED}Error: Must run from /home/yab/Concise/sdk/${NC}"
    exit 1
fi

echo -e "${YELLOW}This script will publish both SDKs to PyPI and NPM${NC}"
echo ""
echo "Prerequisites:"
echo "  - PyPI account and API token configured in ~/.pypirc"
echo "  - NPM account and logged in (npm login)"
echo ""
read -p "Do you want to continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo ""
echo "========================================================================"
echo "STEP 1: Publishing Python SDK to PyPI"
echo "========================================================================"
echo ""

cd python-sdk

# Check if dist exists
if [ ! -d "dist" ]; then
    echo -e "${YELLOW}Building Python package...${NC}"
    source ../../backend/venv/bin/activate
    python -m build
fi

echo -e "${YELLOW}Uploading to PyPI...${NC}"
source ../../backend/venv/bin/activate
twine upload dist/*

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python SDK published successfully!${NC}"
    echo -e "  View at: https://pypi.org/project/concise-sdk/"
else
    echo -e "${RED}✗ Python SDK publishing failed${NC}"
    exit 1
fi

cd ..

echo ""
echo "========================================================================"
echo "STEP 2: Publishing TypeScript SDK to NPM"
echo "========================================================================"
echo ""

cd typescript-sdk

# Check if dist exists
if [ ! -d "dist" ]; then
    echo -e "${YELLOW}Building TypeScript package...${NC}"
    npm run build
fi

echo -e "${YELLOW}Uploading to NPM...${NC}"
npm publish

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ TypeScript SDK published successfully!${NC}"
    echo -e "  View at: https://www.npmjs.com/package/concise-sdk"
else
    echo -e "${RED}✗ TypeScript SDK publishing failed${NC}"
    exit 1
fi

cd ..

echo ""
echo "========================================================================"
echo "PUBLISHING COMPLETE!"
echo "========================================================================"
echo ""
echo -e "${GREEN}Both SDKs are now live!${NC}"
echo ""
echo "Python SDK:"
echo "  - PyPI: https://pypi.org/project/concise-sdk/"
echo "  - Install: pip install concise-sdk"
echo ""
echo "TypeScript SDK:"
echo "  - NPM: https://www.npmjs.com/package/concise-sdk"
echo "  - Install: npm install concise-sdk"
echo ""
echo "Next steps:"
echo "  1. Test installation on a fresh machine"
echo "  2. Update main README with installation instructions"
echo "  3. Tweet about the release"
echo "  4. Update VibeCon presentation"
echo ""
echo "========================================================================"
