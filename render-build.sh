#!/bin/bash
set -ex

# Установка системных зависимостей
apt-get update && apt-get install -y \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev

# Чистая установка Python-пакетов
python -m pip install --upgrade pip
pip install wheel setuptools
pip install -r requirements.txt -c constraints.txt --no-cache-dir