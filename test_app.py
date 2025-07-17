import pytest
from app import app
import os
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
    # Create a dummy image in memory
    test_img = BytesIO()
    test_img.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00' + b'\x00'*1000)
    test_img.seek(0)
    
    data = {
        'file': (test_img, 'test.jpg'),
        'func_type': 'sin',
        'period': '10'
    }
    
    response = client.post(
        '/',
        data=data,
        content_type='multipart/form-data'
    )
    assert response.status_code == 200