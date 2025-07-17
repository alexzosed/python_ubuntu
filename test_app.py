import pytest
from app import app
from PIL import Image
import numpy as np
from io import BytesIO

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

def test_index_page(client):
    """Test that index page loads correctly"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Image Processor" in response.data

def test_image_upload(client):
    """Test image upload processing"""
    # Создаем реальное тестовое изображение в памяти
    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=95)
    img_io.seek(0)
    
    data = {
        'file': (img_io, 'test.jpg'),
        'func_type': 'sin', 
        'period': '10'
    }
    
    response = client.post(
        '/',
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )
    
    assert response.status_code == 200
    assert b"Processed Image" in response.data