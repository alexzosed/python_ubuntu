#!/bin/bash
set -ex

# ��������� ������������
apt-get update && apt-get install -y \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev

# ������� ���������� � ���������� �����
mkdir -p static/uploads static/processed
chmod -R 755 static

# ��������� Python-�������
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir