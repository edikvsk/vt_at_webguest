from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    LOGIN_FIELD = (By.XPATH, "//input[@data-cy='banner-name-input']")
    LOCATION_FIELD = (By.XPATH, "//input[@data-cy='banner-location-input']")
    LOGIN_BUTTON = (By.XPATH, "//button[@type='submit' and @data-cy='connect-button']")

    def enter_username(self, username):
        self.send_keys(self.LOGIN_FIELD, username)

    def enter_location(self, location):
        self.send_keys(self.LOCATION_FIELD, location)

    def click_login_button(self):
        self.click(self.LOGIN_BUTTON)
