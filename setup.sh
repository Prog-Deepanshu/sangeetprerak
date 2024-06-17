#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies again (in the virtual environment)
pip install -r requirements.txt

# Deactivate the virtual environment
deactivate