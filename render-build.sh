#!/bin/bash
set -ex

# Установка зависимостей
apt-get update && apt-get install -y \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev

# Создаем директории
mkdir -p static/uploads static/processed

# Установка Python-пакетов
python -m pip install --upgrade pip
pip install wheel setuptools
pip install -r requirements.txt --no-cache-dir