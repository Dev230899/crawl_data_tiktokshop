import time
import os
from selenium import webdriver
from selenium.webdriver import ChromeOptions


class SeleniumHandler:
    def __init__(self, settings, install_extension: bool = False):
        self.selenium_type = settings.SELENIUM_TYPE
        self.grid_url = settings.SELENIUM_GRID_URL
        self.driver = None
        self.install_extension = install_extension

    def config_options(self):
        options = ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--start-maximized")
        options.add_argument("--remote-allow-origins=*")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-web-security")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-notifications")

        if self.install_extension:
            extension_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "extensions/extension.crx",
            )
            print("Start add custom extensions!", extension_path)
            options.add_extension(extension_path)
            print("Add custom extensions success!")

        return options

    def __enter__(self):
        options = self.config_options()
        if self.selenium_type == "GRID" and self.grid_url is not None:
            self.driver = webdriver.Remote(
                command_executor=self.grid_url, options=options
            )

        elif self.selenium_type == "LOCAL":
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service

            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options,
            )
        elif self.selenium_type == "UC":
            import undetected_chromedriver as uc

            self.driver = uc.Chrome(version_main=121)
        else:
            raise ValueError("Selenium type is not valid")

        self.driver.set_page_load_timeout(100)  # Timeout in seconds
        self.driver.implicitly_wait(100)  # Timeout in seconds
        self.driver.set_script_timeout(100)  # Timeout in seconds

        return self

    def login(self, cookies, site):
        try:
            self.driver.get(site)
            time.sleep(5)
            for cookie in cookies:
                self.driver.add_cookie(
                    {"name": cookie["name"], "value": cookie["value"]}
                )
            time.sleep(1)
            self.driver.refresh()
            time.sleep(3)
            return True
        except Exception as e:
            print(e)
            return False

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()
