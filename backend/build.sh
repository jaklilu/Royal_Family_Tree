#!/bin/bash
# Build script to ensure Python 3.11 is used
set -e

# Check Python version
python3 --version

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

