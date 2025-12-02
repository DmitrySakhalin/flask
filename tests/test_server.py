import pytest
import sys
sys.path.append('.')

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

def test_register_415():
    """Тест: /register без Content-Type — 415"""
    rv = app.test_client().post('/register')
    assert rv.status_code == 415

def test_register_no_data():
    """Тест: /register без JSON данных — 400"""
    rv = app.test_client().post('/register', json={})
    assert rv.status_code == 400

def test_register_postman_style():
    """Тест имитирует Postman запрос — 400"""
    rv = app.test_client().post('/register',
                               data='{}',
                               content_type='application/json')
    assert rv.status_code == 400

def test_nonexistent_route():
    """Тест несуществующего роута — 404"""
    rv = app.test_client().get('/nonexistent')
    assert rv.status_code == 404
