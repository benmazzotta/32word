#!/bin/bash
# Publish script for 32word package
# Loads credentials from .env file and uploads to PyPI

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and add your PyPI API token:"
    echo "  cp .env.example .env"
    echo "  # Then edit .env with your actual token"
    exit 1
fi

# Load environment variables from .env
export $(grep -v '^#' .env | xargs)

# Check if credentials are set
if [ -z "$TWINE_USERNAME" ] || [ -z "$TWINE_PASSWORD" ]; then
    echo "Error: TWINE_USERNAME or TWINE_PASSWORD not set in .env file"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Find the latest version files
VERSION=$(python -c "from word32 import __version__; print(__version__)")
WHEEL="dist/32word-${VERSION}-py3-none-any.whl"
SDIST="dist/32word-${VERSION}.tar.gz"

# Check if distribution files exist
if [ ! -f "$WHEEL" ] || [ ! -f "$SDIST" ]; then
    echo "Error: Distribution files not found!"
    echo "Expected: $WHEEL and $SDIST"
    echo "Run 'python -m build' first to build the package"
    exit 1
fi

echo "Uploading 32word version ${VERSION} to PyPI..."
echo "Files: $WHEEL, $SDIST"
echo ""

# Upload to PyPI
twine upload "$WHEEL" "$SDIST"

echo ""
echo "✅ Successfully uploaded 32word ${VERSION} to PyPI!"
