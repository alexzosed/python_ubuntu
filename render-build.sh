#!/bin/bash
set -e

# Установка системных зависимостей для Pillow
apt-get update && apt-get install -y \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev

# Установка Python-пакетов
pip install --upgrade pip
pip install wheel
pip install -r requirements.txt --no-cache-dir