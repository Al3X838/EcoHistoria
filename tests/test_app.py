import unittest
from app import create_app
from config import Config
from models import db, User

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        # Create a test user
        u = User(username='testuser', email='test@example.com', nombre_completo='Test User')
        u.set_password('password')
        db.session.add(u)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register_and_login(self):
        # Test registration
        response = self.client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'nombre_completo': 'New User',
            'facultad': 'Ingeniería',
            'carrera': 'Ingeniería en Sistemas',
            'password': 'password',
            'password2': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Your account has been created', response.data.decode('utf-8'))

        # Test login
        response = self.client.post('/auth/login', data={
            'username': 'newuser',
            'password': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Welcome back', response.data.decode('utf-8'))

    def test_password_reset(self):
        # Request password reset
        response = self.client.post('/auth/reset_password', data={
            'email': 'test@example.com'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('An email has been sent', response.data.decode('utf-8'))

        # Reset password with token
        user = User.query.filter_by(email='test@example.com').first()
        token = user.get_reset_token()
        response = self.client.post(f'/auth/reset_password/{token}', data={
            'password': 'newpassword',
            'password2': 'newpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Your password has been updated', response.data.decode('utf-8'))

        # Login with new password
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'newpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Welcome back', response.data.decode('utf-8'))

if __name__ == '__main__':
    unittest.main()
