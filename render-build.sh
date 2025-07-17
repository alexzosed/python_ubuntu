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
pip install wheel==0.43.0 setuptools==68.2.2
pip install --no-cache-dir -r requirements.txt