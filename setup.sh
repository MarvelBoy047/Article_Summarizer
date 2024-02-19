#!/bin/bash

# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-pip

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

