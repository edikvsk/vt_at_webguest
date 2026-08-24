from unittest.mock import Mock

from utils.notificaton_handler import NotificationHandler


class FakeNotification:
    def __init__(self, text, displayed):
        self.text = text
        self._displayed = displayed

    def is_displayed(self):
        return self._displayed


def test_wait_for_notification_text_scans_past_hidden_stale_container():
    driver = Mock()
    driver.find_elements.return_value = [
        FakeNotification("Old notification", displayed=False),
        FakeNotification(
            "You are not authorized to access this link",
            displayed=True,
        ),
    ]
    logger = Mock()
    handler = NotificationHandler(driver, ("xpath", "//notification"), logger)

    actual = handler.wait_for_notification_text(
        "You are not authorized",
        timeout=0.2,
    )

    assert actual == "You are not authorized to access this link"
