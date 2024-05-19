'''
use 'python  -m unittest test/unit_test.py' to test
''' 

import unittest
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User, Fragment
from app.config import TestConfig
import json

class AuthTestCase(unittest.TestCase):

    def setUp(self):
        # Set up Flask test client and disable CSRF
        self.app = create_app(TestConfig)
        self.app.config['WTF_CSRF_ENABLED'] = False 
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        # Setup database and add a existed user
        db.create_all()
        hashed_password = generate_password_hash('test123', method='pbkdf2:sha256')
        user = User(username='testuser', email='testuser@example.com', passwd_hash=hashed_password)
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    def test_successful_login(self):
        with self.client as c:
            response = c.post('/auth/login', data={
                'user_email': 'testuser@example.com',
                'password': 'test123',
                'remember_me': True
            }, follow_redirects=False)  
            
            print(response.headers) 
            
            # Check if redirection occurred
            self.assertEqual(response.status_code, 302)
            
            # Get redirect target URL
            location = response.headers.get('Location', '')
            self.assertIn('/dashboard', location)  # Check redirect target
            
            # Follow the redirect to the dashboard page
            response = c.get(location, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Hello testuser, welcome to dashboard!', response.data)  # Check flash message


    def test_failed_login(self):
        with self.client as c:
            response = c.post('/auth/login', data={
                'user_email': 'testuser@example.com',
                'password': 'wrongpassword'
            }, follow_redirects=True) # Automatically follow redirects

            # Confirm that the response status code is 200, indicating that the page is reloaded
            self.assertEqual(response.status_code, 200)
            
            # Check whether the page contains specific elements of the login form to confirm that the login page is returned
            self.assertIn(b'<h2 class="text-center">Login</h2>', response.data)



    def test_successful_registration(self):
        with self.client as c:
            response = c.post('/auth/register', data={
                'username': 'newuser1',
                'email': 'new@example.com',
                'password': 'newpassword',
                'confirm_password': 'newpassword'
            }, follow_redirects=False)
            # First confirm that the redirection occurred
            self.assertEqual(response.status_code, 302)
            self.assertTrue('/auth/login' in response.headers['Location'])

            # Then follow the redirect to the login page
            response = c.get(response.headers['Location'], follow_redirects=True)
            # Check if specific HTML structures are included, such as the presence of a login form
            self.assertIn('login-container', response.get_data(as_text=True))  # Check whether the CSS class of the login container exists
            self.assertIn('<h2 class="text-center">Login</h2>', response.get_data(as_text=True))  # Check if the login header exists


    def test_failed_registration_duplicate_email(self):
        response = self.client.post('/auth/register', data={
            'username': 'newuser2',
            'email': 'testuser@example.com',
            'password': 'test123',
            'confirm_password': 'test123'
        }, follow_redirects=True)
        self.assertIn(b'This email address is already registered. Please use a different email address.', response.data)


class PagesTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        # Set up the database and add pre-existing users
        db.create_all()
        hashed_password = generate_password_hash('test123', method='pbkdf2:sha256')
        user = User(username='testuser', email='testuser@example.com', passwd_hash=hashed_password)
        user.set_balance(50)  # Assume that the User model has a set_balance method
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_dashboard_requires_login(self):
        # Access dashboard without login
        response = self.client.get('/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Check if the page contains specific elements of the login form to confirm that a login page is being returned
        self.assertIn(b'<h2 class="text-center">Login</h2>', response.data)

        # Log in to access the dashboard
        self.client.post('/auth/login', data={
            'user_email': 'testuser@example.com',
            'password': 'test123'
        }, follow_redirects=True)
        response = self.client.get('/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h1 class="mt-5 mb-5 text-center">Dashboard</h1>', response.data)

    def test_marketplace(self):
        response = self.client.get('/marketplace', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Marketplace', response.data)  # Assume the page contains the word Marketplace

    def test_index(self):
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h1 class="large-title">Welcome to the Virtual NFT Marketplace</h1>', response.data)  



class TradeTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        # Set up the database and add pre-existing users
        db.create_all()
        self.user = User(username='testuser', email='testuser@example.com', passwd_hash=generate_password_hash('test123', method='pbkdf2:sha256'))
        self.user.set_balance(50)
        self.other_user = User(email='other@example.com', passwd_hash=generate_password_hash('passwd', method='pbkdf2:sha256'))
        self.other_user.set_balance(50)
        self.fragment = Fragment(id='123', img_id='img_test', path='/static/outputs/test.png', piece_number=9, owner=1)
        db.session.add(self.user)
        db.session.add(self.fragment)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self):
        return self.client.post('/auth/login', data={
            'user_email': 'testuser@example.com',
            'password': 'test123'
        }, follow_redirects=True)

    def test_new_trade_creation(self):
        self.login()
        # User information does not match, try to use another user's ID
        wrong_owner_id = self.user.id + 1  # Assume that this ID does not belong to the currently logged in user
        response = self.client.post('/trade/trade', data=json.dumps({
            'fragment_id': '123',  # Consistent use of 'fragment_id'
            'price': 200,  # Numeric price to focus on owner mismatch
            'owner': wrong_owner_id  # Deliberately providing a wrong user ID
        }), content_type='application/json')
        self.assertEqual(response.status_code, 403)  # Expecting forbidden due to owner mismatch

        # Correct transaction data
        response = self.client.post('/trade/trade', data=json.dumps({
            'fragment_id': '123',  # Corrected key from 'id' to 'fragment_id'
            'price': 200,  # Changed from string '200' to numeric 200
            'owner': self.user.id
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'success')
        self.assertIn('Trade created successfully', json_data['message'])

        # Trying to create the same deal again should fail because it is already on sale
        response = self.client.post('/trade/trade', data=json.dumps({
            'fragment_id': '123',  # Consistent key 'fragment_id'
            'price': 300,
            'owner': self.user.id
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'error')
        self.assertIn('Fragment is currently for sale', json_data['message'])

        # Price format error
        response = self.client.post('/trade/trade', data=json.dumps({
            'fragment_id': '123',
            'price': 'not_a_number',  # This intentionally tests invalid price format
            'owner': self.user.id
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'error')
        self.assertIn('Invalid price format', json_data['message'])

   
    


if __name__ == '__main__':
    unittest.main()
