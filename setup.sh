#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Setup Streamlit config
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = $PORT\n\
address = \"0.0.0.0\"\n\
" > ~/.streamlit/config.toml

# Create empty .env if it doesn't exist (Heroku uses config vars instead)
touch .env
