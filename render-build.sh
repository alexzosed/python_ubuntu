#!/bin/bash
set -ex

# Установка системных зависимостей
apt-get update && apt-get install -y \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev

# Создаем директории
mkdir -p static/uploads static/processed

# Установка Python-пакетов
python -m pip install --upgrade "pip<24.0"
python -m pip install "setuptools<81.0.0" wheel
python -m pip install -r requirements.txt --no-cache-dir