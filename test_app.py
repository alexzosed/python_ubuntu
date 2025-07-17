import pytest
from app import app
import numpy as np
from PIL import Image
from io import BytesIO
import os

@pytest.fixture
def client():
    # Создаем тестовые директории
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('static/processed', exist_ok=True)
    
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    
    # Очистка после тестов
    for folder in ['uploads', 'processed']:
        for f in os.listdir(f'static/{folder}'):
            os.remove(f'static/{folder}/{f}')

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Image Processor" in response.data

def test_image_processing(client):
    # Создаем тестовое изображение
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    response = client.post(
        '/',
        data={
            'file': (img_bytes, 'test.jpg'),
            'func_type': 'sin',
            'period': '10'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    assert b'Processed Image' in response.data