import unittest
from unittest.mock import Mock, patch

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from pages.web_guest_page import WebGuestPage
from utils.process_handler import ProcessManager


class FakeInput:
    def __init__(self, value=""):
        self.value = value
        self.sent_keys = []

    def is_displayed(self):
        return True

    def is_enabled(self):
        return True

    def clear(self):
        self.value = ""

    def send_keys(self, *keys):
        self.sent_keys.append(keys)
        if keys == (Keys.BACKSPACE,):
            self.value = ""
        elif keys not in ((Keys.CONTROL, "a"), (Keys.TAB,)):
            self.value += "".join(keys)

    def get_attribute(self, name):
        return self.value if name == "value" else None


class FakeDriver:
    def __init__(self, element):
        self.element = element

    def find_element(self, _by, _value):
        return self.element


class ResponsiveUiTests(unittest.TestCase):
    LOCATOR = (By.ID, "field")

    def test_text_is_sent_as_one_keyboard_operation(self):
        element = FakeInput("old")
        page = WebGuestPage(FakeDriver(element))

        page.input_text(self.LOCATOR, "example")

        self.assertEqual("example", element.value)
        self.assertEqual([("example",), (Keys.TAB,)], element.sent_keys)

    def test_text_is_deleted_without_per_character_delays(self):
        element = FakeInput("example")
        page = WebGuestPage(FakeDriver(element))

        page.delete_text(self.LOCATOR)

        self.assertEqual("", element.value)
        self.assertEqual((Keys.CONTROL, "a"), element.sent_keys[0])
        self.assertEqual((Keys.BACKSPACE,), element.sent_keys[1])

    def test_process_start_waits_for_window_readiness(self):
        manager = object.__new__(ProcessManager)
        manager.process_path = "VT_Publisher.exe"
        manager.process_name = "VT_Publisher.exe"
        manager.logger = Mock()
        manager.is_process_running = Mock(return_value=None)
        manager.delete_config_file = Mock(return_value=True)
        manager.wait_for_process_ready = Mock()
        launched = Mock(pid=123)

        with patch("utils.process_handler.subprocess.Popen", return_value=launched):
            manager.start_process()

        manager.wait_for_process_ready.assert_called_once_with(123)


if __name__ == "__main__":
    unittest.main()
