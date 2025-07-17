import pytest
from app import app
from werkzeug.test import create_environ  # Добавляем импорт

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    """Тест главной страницы"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Image Processor" in response.data

def test_image_upload(client, tmp_path):
    """Тест загрузки изображения"""
    # Создаем временное тестовое изображение
    test_img = tmp_path / "test.jpg"
    with open(test_img, 'wb') as f:
        f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00' + b'\x00'*1000)
    
    with open(test_img, 'rb') as img:
        response = client.post(
            '/',
            data={
                'file': (img, 'test.jpg'),
                'func_type': 'sin',
                'period': '10'
            },
            content_type='multipart/form-data'
        )
    assert response.status_code == 200