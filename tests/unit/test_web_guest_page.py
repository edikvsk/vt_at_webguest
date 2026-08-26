from unittest.mock import Mock, patch

import pytest
from selenium.common.exceptions import TimeoutException

from pages.web_guest_page import WebGuestPage


class FakeActions:
    def __init__(self, *_args, **_kwargs):
        self.perform_count = 0

    def move_to_element(self, _element):
        return self

    def pause(self, _seconds):
        return self

    def click(self):
        return self

    def perform(self):
        self.perform_count += 1
        return self


def test_combobox_selection_waits_for_confirmed_value():
    driver = Mock()
    page = WebGuestPage(driver)
    combobox = Mock()
    option = Mock()
    waits = [Mock(), Mock(), Mock(), Mock()]
    waits[0].until.return_value = combobox
    waits[1].until.return_value = option
    waits[2].until.return_value = True
    waits[3].until.return_value = True
    page._wait = Mock(side_effect=waits)

    with patch("pages.web_guest_page.ActionChains", FakeActions):
        page.select_from_combobox(
            ("xpath", "combobox"),
            "15 fps",
            value_locator=("xpath", "value"),
            expected_value="15 FPS",
            attempts=1,
            wait_for_menu_to_close=True,
        )

    assert page._wait.call_count == 4
    driver.execute_script.assert_called_once()


def test_combobox_selection_does_not_hide_failures():
    driver = Mock()
    driver.find_element.side_effect = RuntimeError("no body")
    page = WebGuestPage(driver)
    wait = Mock()
    wait.until.side_effect = TimeoutException("menu did not open")
    page._wait = Mock(return_value=wait)

    with patch("pages.web_guest_page.ActionChains", FakeActions):
        with pytest.raises(RuntimeError, match="после 2 попыток"):
            page.select_from_combobox(
                ("xpath", "combobox"),
                "H264",
                attempts=2,
            )


def test_combobox_selection_can_keep_rejected_option_menu_open():
    driver = Mock()
    page = WebGuestPage(driver)
    combobox = Mock()
    option = Mock()
    waits = [Mock(), Mock(), Mock()]
    waits[0].until.return_value = combobox
    waits[1].until.return_value = option
    waits[2].until.return_value = True
    page._wait = Mock(side_effect=waits)

    with patch("pages.web_guest_page.ActionChains", FakeActions):
        page.select_from_combobox(
            ("xpath", "combobox"),
            "60 fps",
            value_locator=("xpath", "value"),
            expected_value="30 FPS",
            attempts=1,
            wait_for_menu_to_close=False,
        )

    assert page._wait.call_count == 2
    driver.execute_script.assert_called_once()


def test_rejected_framerate_selection_can_skip_value_confirmation():
    page = WebGuestPage(Mock())
    page.hover_element = Mock()
    page.select_from_combobox = Mock()

    page.select_framerate(
        "60 FPS",
        wait_for_menu_to_close=False,
        verify_value=False,
    )

    page.select_from_combobox.assert_called_once_with(
        page.FRAMERATE_COMBOBOX,
        "60 fps",
        value_locator=None,
        expected_value="60 FPS",
        wait_for_menu_to_close=False,
    )


def test_preview_controls_dispatch_hover_on_transparent_overlay():
    driver = Mock()
    page = WebGuestPage(driver)
    overlay = Mock()
    wait = Mock()
    wait.until.return_value = [overlay]
    page._wait = Mock(return_value=wait)
    actions = Mock()
    actions.move_to_element.return_value.perform.return_value = None
    page._actions = Mock(return_value=actions)

    page.reveal_preview_controls()

    actions.move_to_element.assert_called_once_with(overlay)
    driver.execute_script.assert_called_once()
    assert driver.execute_script.call_args.args[-1] is overlay


def test_combobox_text_normalization_ignores_case_and_layout_whitespace():
    assert (
        WebGuestPage._normalized_text("AUDIO BITRATE\n  10K")
        == WebGuestPage._normalized_text("audio bitrate 10k")
    )


def test_numeric_audio_channels_fall_back_to_other_channels():
    page = WebGuestPage(Mock())
    page.hover_element = Mock()
    page.click = Mock()
    page.input_text = Mock()
    page.select_from_combobox = Mock(
        side_effect=[RuntimeError("preset is absent"), None]
    )

    page.select_audio_channels("1, 2")

    assert page.select_from_combobox.call_count == 2
    page.click.assert_called_once_with(page.COMBOBOX_BACK_BUTTON)
    page.input_text.assert_called_once_with(page.INPUT_FIELD_OTHER_CHANNELS, "1, 2")
