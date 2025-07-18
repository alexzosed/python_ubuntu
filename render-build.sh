#!/bin/bash
set -ex

# Установка зависимостей
apt-get update && apt-get install -y \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev

# Создаем директории в правильном месте
mkdir -p static/uploads static/processed
chmod -R 755 static

# Установка Python-пакетов
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir