import pytest
from app import create_app
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            from models import db
            db.create_all()
        yield client

def test_home_page(client):
    """Test the home page redirects to login."""
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Log In' in response.data
