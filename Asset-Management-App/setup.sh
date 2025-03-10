#!/bin/bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
port = 10000\n\
enableCORS = false\n\
headless = true\n\
" > ~/.streamlit/config.toml
