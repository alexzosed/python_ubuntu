import pytest
from app import app

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

def test_image_upload(client):
    """Тест загрузки изображения"""
    with open('test_image.jpg', 'rb') as img:
        response = client.post(
            '/',
            data={'file': img, 'func_type': 'sin', 'period': '10'},
            content_type='multipart/form-data'
        )
    assert response.status_code == 200