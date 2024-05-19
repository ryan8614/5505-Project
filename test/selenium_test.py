'''
use 'python server.py & python -m unittest test/selenium_test.py' to test
or 'python -m unittest test/selenium_test.py' when server is running
''' 

import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


# Correctly import create_app and db from your application structure
from app import create_app, db
from app.config import TestConfig


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)

    def tearDown(self):
        if self.driver:
            self.driver.quit()



class IndexSeleniumTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        # Use create_app to create a Flask application instance
        cls.app = create_app(TestConfig)
        cls.app.config['WTF_CSRF_ENABLED'] = False
        with cls.app.app_context():
            db.create_all()
            cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()
            db.session.commit() # Ensure all transactions are committed or rolled back

    def setUp(self):
        super().setUp()
        self.driver.get("http://127.0.0.1:5001/")

    def test_navigation_links(self):
        nav_items = self.driver.find_elements(By.CSS_SELECTOR, "nav .navbar-nav a")
        self.assertTrue(len(nav_items) > 0, "No navigation links found.")
        for item in nav_items:
            self.assertTrue(item.is_displayed(), f"Nav item {item.text} is not visible.")

    def test_how_it_works_section(self):
        section_title = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'How It Works')]"))
        )
        self.assertTrue(section_title.is_displayed(), "Section title 'How It Works' is not visible.")

    def test_login_and_signup_buttons(self):
        login_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Log In"))
        )
        login_button.click()
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/auth/login")
        )
        self.assertIn("/auth/login", self.driver.current_url, "Did not navigate to login page.")

        self.driver.get("http://127.0.0.1:5001/")
        signup_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Sign Up"))
        )
        signup_button.click()
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/auth/register")
        )
        self.assertIn("/auth/register", self.driver.current_url, "Did not navigate to signup page.")


class MarketplaceTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        # Use create_app to create a Flask application instance
        cls.app = create_app(TestConfig)
        cls.app.config['WTF_CSRF_ENABLED'] = False
        with cls.app.app_context():
            db.create_all()
            cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()
            db.session.commit() # Ensure all transactions are committed or rolled back
    
    def setUp(self):
        super().setUp()
        # Initialize the WebDriver instance
        self.driver.get("http://localhost:5001/marketplace")
    
    
    def test_navigation_links(self):
        nav_links = self.driver.find_elements(By.CSS_SELECTOR, "nav .navbar-nav a")
        self.assertTrue(len(nav_links) > 0, "Navigation link not found")

    def test_market_introduction(self):
        intro_text = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".market-intro .intro-text"))
        )
        self.assertTrue(intro_text.is_displayed(), "Market introduction text is not displayed")
    
    def test_live_auctions_display(self):
        try:
            # Wait until the carousel items are not only loaded but also visible
            auction_items = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "#liveAuctionCarousel .carousel-item"))
            )
            # Assert to check if there's at least one carousel item
            self.assertTrue(len(auction_items) > 0, "Auction items are not displayed correctly")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            raise

    def test_faq_section(self):
        # Wait for the FAQ button element to load and be clickable
        faq_buttons = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".collap-btn"))
        )
        # Test each FAQ button
        for button in faq_buttons:
            # Get the current content visibility
            content = button.find_element(By.XPATH, "following-sibling::div")
            initially_visible = content.is_displayed()
            # Click button
            ActionChains(self.driver).move_to_element(button).click(button).perform()
            # Wait for content status to change
            WebDriverWait(self.driver, 10).until(
                lambda _: content.is_displayed() != initially_visible
            )
            # Verify that content visibility has changed
            self.assertNotEqual(content.is_displayed(), initially_visible, f"FAQ content visibility should change on click: {button.text}")


if __name__ == '__main__':
    unittest.main()