import pytest
from app import app
from PIL import Image
import numpy as np
from io import BytesIO
import os

@pytest.fixture
def client():
    # Настройка тестового окружения
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Создаем временные директории
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('static/processed', exist_ok=True)
    
    with app.test_client() as client:
        yield client
    
    # Очистка после тестов
    for f in os.listdir('static/uploads'):
        os.remove(f'static/uploads/{f}')
    for f in os.listdir('static/processed'):
        os.remove(f'static/processed/{f}')

def test_index_page(client):
    """Тест главной страницы"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Image Processor" in response.data

def test_image_upload(client):
    """Тест обработки изображения"""
    # Создаем тестовое изображение 100x100 пикселей
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    # Отправляем POST-запрос
    response = client.post(
        '/',
        data={
            'file': (img_bytes, 'test.jpg'),
            'func_type': 'sin',
            'period': '10'
        },
        content_type='multipart/form-data'
    )
    
    # Проверяем результаты
    assert response.status_code == 200
    assert b'Processed Image' in response.data
    
    # Проверяем, что файл создан
    processed_files = os.listdir('static/processed')
    assert any(f.startswith('processed_test') for f in processed_files)