#!/usr/bin/env bash
# Sair se der erro
set -o errexit

# 1. Instala as dependências
pip install -r requirements.txt

# 2. Coleta os arquivos estáticos (CSS, Imagens do sistema)
python manage.py collectstatic --no-input

# 3. Cria as tabelas no banco de dados do Render
python manage.py migrate