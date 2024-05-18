import unittest
from flask import Flask
from werkzeug.security import generate_password_hash
from app import create_app, db  
from app.models import User    
from app.config import TestConfig

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        # Set up Flask test client and disable CSRF
        self.app = create_app(TestConfig)
        self.app.config['WTF_CSRF_ENABLED'] = False 
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)

        # Setup database and add a existed user
        db.create_all()
        hashed_password = generate_password_hash('test123')
        user = User(username='testuser', email='testuser@example.com', passwd_hash=hashed_password, balance=50)
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_successful_login(self):
        # Test successful login
        response = self.client.post('/login', data=dict(
            user_email='testuser@example.com', password='test123',
            remember_me = True), follow_redirects=True)
        self.assertIn(b'Log in successfully', response.data)

    def test_failed_login(self):
        # Test login failure
        response = self.client.post('/login', data=dict(
            user_email='testuser@example.com', password='wrongpassword'), follow_redirects=True)
        self.assertIn(b'Login failed', response.data)

    def test_successful_registration(self):
        response = self.client.post('/register', data=dict(
            username='newuser1', email='new@example.com', password='newpassword', 
            confirm_password='newpassword'), follow_redirects=True)
        self.assertIn(b'Account created', response.data)

    def test_failed_registration_duplicate_email(self):
        # Test registration using a registered email address 
        response = self.client.post('/register', data=dict(
            username='newuser2', email='testuser@example.com', password='test123',
            confirm_password='test123'), follow_redirect_links=True)
        # Check if the response contains a specific error message
        self.assertIn(b'This email address is already registered. Please use a different email address.', response.data)
        self.assertEqual(response.status_code, 200)
if __name__ == '__main__':
    unittest.main()

