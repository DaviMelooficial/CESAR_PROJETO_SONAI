#!/bin/bash

# Script de setup para Streamlit Cloud

mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = \$PORT\n\
enableCORS = false\n\
\n\
[browser]\n\
gatherUsageStats = false\n\
" > ~/.streamlit/config.toml

# Criar diretório para banco de dados se não existir
mkdir -p data

echo "Setup completo!"
