import os
import time
import logging
import random
from dotenv import load_dotenv
load_dotenv()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth

# Set up logging
if not os.path.exists('/seo_agents_crew/logs/'):
    os.makedirs('/seo_agents_crew/logs/')

logging.basicConfig(
    level=logging.DEBUG,
    filemode='w',
    filename='logs/sso_login.log',
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def human_like_delay(min_delay=1, max_delay=3):
    time.sleep(random.uniform(min_delay, max_delay))

class FacebookLogin:
    def __init__(self, url: str, email: str, password: str) -> None:
        """Initialize the GoogleSSOLogin class."""
        self.url = url
        self.email = email
        self.password = password
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 30)
        stealth(self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

    def open_site(self) -> None:
        """Open the target site."""
        self.driver.get(self.url)
        logger.info(f"Opened site: {self.url}")

    def click_sign_in(self) -> None:
        """Click the 'Sign in' button on the site."""
        selector = "//*[@id='root']/div/div[3]/div[1]/div[2]/div[4]/div/div/p/span/a"
        try:
            sign_in_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            sign_in_button.click()
            logger.info("Clicked 'Sign in' button")
            human_like_delay()
        except Exception as e:
            logger.error(f"Error clicking 'Sign in' button: {e}")
            self.close()
            raise

    def click_fb_login(self) -> None:
        """Click the 'Sign in with Facebook"""
        selector = "/html/body/div[3]/div/div/div/div[1]/div/div[2]/div[1]/a"

        try:
            fb_login = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))

            if fb_login:
                fb_login.click()
                logger.info("Clicked 'Sign in with FB' button")
                human_like_delay()
                return
        except Exception as e:
            logger.error(f"Error clicking 'Sign in with FB' button: {e}")
            self.close()
            raise

        logger.error("Could not find FB button")
        self.close()
        raise Exception("FB button not found")

    def perform_fb_login(self) -> None:
        """Perform Facebook login."""

        try:
            email_field = self.wait.until(EC.element_to_be_clickable((By.ID, "email")))
            email_field.send_keys(self.email)
            human_like_delay()
            password_field = self.wait.until(EC.element_to_be_clickable((By.ID, "pass")))
            password_field.send_keys(self.password)
            human_like_delay()
            self.driver.find_element(By.NAME, "login").click() #changed to login button name.
            logger.info("Entered email and password and clicked 'Log In'")
            human_like_delay(10)  # Wait for login to complete

        except Exception as e:
            logger.error(f"Error during Facebook login: {e}")
            self.close()
            raise


    def login(self) -> webdriver.Chrome:
        """Perform the complete login process."""
        try:
            self.open_site()
            self.click_sign_in()
            self.click_fb_login()
            self.perform_fb_login()
            return self.driver
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return None

    def close(self) -> None:
        """Close the browser."""
        self.driver.quit()

def main():
    # Configuration
    url = "https://medium.com/@StevieLKim"  # URL to Medium's site

    try:
        fb_email = os.environ.get("FB_EMAIL")
        fb_password = os.environ.get("FB_PASSWORD")
    except Exception as e:
        if not fb_email or not fb_password:
            logger.error(f"Error getting environment variables: {e}")
            return

    
    #Create an instance of the FacebookLogin class
    fb_login_instance = FacebookLogin(url, fb_email, fb_password)
    # Call the login method
    driver = fb_login_instance.login()
    #this brings up a captcha page, so that can be done manually, but then it has
    # a button that says "Continue as Stevie" that can be clicked manually or
    # added into the script.
    # The main point of the automation is to automate the uploading of new blog posts
    # to medium, so the captcha can be done manually, but the rest can be automated
    # The reason I automated the login is I initially wanted to have an excuse to create
    # a custom tool for CrewAI, and I also wanted to only have one human-in-the-loop
    # phase which was the selection of the CrewAI SEO suggestions.

    if driver:
        try:
            # Perform actions after login
            logger.info(f"Logged in successfully. Current URL: {driver.current_url}")
            # Example: Wait and demonstrate successful login
            time.sleep(30)
            
        finally:
            # Always close the browser
            driver.close()
            logger.info("Browser closed")

if __name__ == "__main__":
    main()