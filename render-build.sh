#!/bin/bash
set -ex

# Установка системных зависимостей
apt-get update && apt-get install -y \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev

# Создаем директории с правильными правами
mkdir -p static/uploads static/processed
chmod -R 755 static/

# Установка Python-пакетов
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir

# Создаем тестовые файлы для проверки прав
touch static/uploads/test.txt static/processed/test.txt