#!/bin/bash

# Set your ngrok authtoken here
NGROK_TOKEN="2YMZ0ommMCqEfRxkGx2YzzGB3Tb_5GhRhEg1xPSQEUFc1MxM6"

# Update package lists and install required packages
sudo apt-get update -y
sudo apt-get install -y wget unzip

# Download ngrok
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip -O ngrok.zip

# Unzip and move to /usr/local/bin
unzip ngrok.zip
sudo mv ngrok /usr/local/bin/
rm ngrok.zip

# Configure ngrok with the provided token
ngrok config add-authtoken $NGROK_TOKEN

# Verify installation
ngrok version

echo "Ngrok installed and configured successfully!"
