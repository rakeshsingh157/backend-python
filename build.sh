#!/bin/bash
set -e

echo "=== Build Script Starting ==="
echo "Current Python version:"
python --version

echo "Current directory:"
pwd

echo "Environment variables:"
env | grep -E "(PYTHON|PATH)" || echo "No PYTHON env vars found"

echo "Available Python versions:"
ls -la /usr/bin/python* 2>/dev/null || echo "No system Python found"
ls -la /opt/render/project/python/ 2>/dev/null || echo "No render Python found"

echo "Attempting to install requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Build completed successfully ==="