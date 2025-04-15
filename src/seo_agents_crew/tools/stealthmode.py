import os
import time
import logging
from dotenv import load_dotenv
load_dotenv()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import random

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

class GoogleSSOLogin:
    def __init__(self, url: str, email: str, password: str, profile_path: str) -> None:
        """Initialize the GoogleSSOLogin class."""
        self.url = url
        self.email = email
        self.password = password
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-data-dir={profile_path}")
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(options=options)
        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        self.wait = WebDriverWait(self.driver, 30)

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

    def click_google_sso(self) -> None:
        """Click the 'Sign in with Google' button."""
        selector = "/html/body/div[3]/div/div/div/div[1]/div/div[2]/a"
        try:
            google_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            if google_button:
                google_button.click()
                logger.info("Clicked 'Sign in with Google' button")
                human_like_delay()
                return
        except Exception as e:
            logger.error(f"Error clicking 'Sign in with Google' button: {e}")
            self.close()
            raise

        logger.error("Could not find Google SSO button")
        self.close()
        raise Exception("Google SSO button not found")

    def perform_google_login(self) -> None:
        """Perform Google login."""
        try:
            email_field = self.wait.until(EC.element_to_be_clickable((By.ID, "identifierId")))
            email_field.send_keys(self.email)
            human_like_delay()
            self.driver.find_element(By.ID, "identifierNext").click()
            logger.info("Entered email and clicked 'Next'")

            password_field = self.wait.until(EC.element_to_be_clickable((By.NAME, "Passwd")))
            password_field.send_keys(self.password)
            human_like_delay()
            self.driver.find_element(By.ID, "passwordNext").click()
            logger.info("Entered password and clicked 'Next'")

            human_like_delay(10)  # Wait for login to complete
        except Exception as e:
            logger.error(f"Error during Google login: {e}")
            self.close()
            raise

    def login(self) -> webdriver.Chrome:
        """Perform the complete login process."""
        try:
            self.open_site()
            self.click_sign_in()
            self.click_google_sso()
            self.perform_google_login()
            return self.driver
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return None

    def close(self) -> None:
        """Close the browser."""
        self.driver.quit()

def main():
    # Configuration
    url = "https://medium.com/@StevieLKim"
    profile_path = r"/Users/stephaniekim/Library/Application Support/Google/Chrome/Profile 3" #added profile path here.

    try:
        google_email = os.environ.get("GOOGLE_EMAIL")
        google_password = os.environ.get("GOOGLE_PASSWORD")
    except Exception as e:
        if not google_email or not google_password:
            logger.error("Google email or password not set in environment variables")
            return

    sso_login = GoogleSSOLogin(url, google_email, google_password, profile_path)
    driver = sso_login.login()

    if driver:
        try:
            logger.info(f"Logged in successfully. Current URL: {driver.current_url}")
            human_like_delay(10) #add a delay after successful login.

        finally:
            sso_login.close()
            logger.info("Browser closed")

if __name__ == "__main__":
    main()