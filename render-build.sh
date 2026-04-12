#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Node.js dependencies
npm install

# Build frontend if it were in the same repo, but it's separate. 
# Just run migrations for the backend.
npm run migrate

# Install Python dependencies
# Render's standard Node runtime usually has Python 3 installed.
if command -v pip &> /dev/null
then
    echo "Installing Python dependencies..."
    pip install -r python/requirements.txt
else
    echo "pip not found. Attempting to use pip3..."
    pip3 install -r python/requirements.txt
fi

echo "Build complete."
