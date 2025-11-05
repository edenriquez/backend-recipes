#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Create a setup.py if it doesn't exist
if [ ! -f setup.py ]; then
    cat > setup.py << 'EOL'
from setuptools import setup, find_packages

setup(
    name="fastapi_app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=open('requirements.txt').read().splitlines(),
)
EOL
    
    # Install the package in development mode
    pip install -e .
fi
