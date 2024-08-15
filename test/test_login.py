import os

from utils.conftest import driver, login_fixture


def test_valid_login(login_fixture, driver):
    test_name = os.path.splitext(os.path.basename(__file__))[0]
