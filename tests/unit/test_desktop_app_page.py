import logging
from unittest.mock import Mock

import pytest

from pages.desktop_app_page import DesktopAppPage
from utils import conftest as fixture_support
from utils.web_url import DesktopUrlAcquisitionError


class FakeMenuItem:
    handle = 101

    def __init__(self, title):
        self.title = title
        self.clicked = False

    def window_text(self):
        return self.title

    def is_visible(self):
        return True

    def is_enabled(self):
        return True

    def click_input(self):
        self.clicked = True


class FakeWrapper:
    """Models the UIAWrapper objects returned by Application.windows()."""

    def __init__(self, items):
        self.items = items

    def descendants(self, control_type=None):
        assert control_type == "MenuItem"
        return self.items


class FakeWindowSpec:
    def __init__(self, popup):
        self.app = type("FakeApplication", (), {"windows": lambda _: [popup]})()

    def child_window(self, **_kwargs):
        return MissingMenuItem()

    def descendants(self, control_type=None):
        assert control_type == "MenuItem"
        return []


class MissingMenuItem:
    handle = None

    def exists(self, timeout=0):
        return False


def test_click_vt_source_item_supports_top_level_uia_wrappers():
    item = FakeMenuItem("Copy Web Guest URL")
    popup = FakeWrapper([item])
    page = DesktopAppPage(FakeWindowSpec(popup))

    page.click_vt_source_item("Copy Web Guest URL", timeout=0.5)

    assert item.clicked


def test_right_click_source_uses_default_title_before_caption_refresh():
    page = DesktopAppPage(Mock())
    source = Mock()
    parent = Mock()
    source.parent.return_value = parent

    def find_source(title, enabled_only=False):
        assert enabled_only
        if title == "Web Guest":
            return source
        raise LookupError(title)

    page._find_text_element = Mock(side_effect=find_source)

    matched_title = page.right_click_vt_source_item_by_any_title(
        ("01TEST_NAME", "Web Guest"),
        timeout=0.1,
    )

    assert matched_title == "Web Guest"
    parent.set_focus.assert_called_once_with()
    assert source.click_input.call_count == 2
    source.click_input.assert_called_with(button="right")


def test_current_web_guest_url_never_falls_back_to_cached_room(monkeypatch):
    acquisition_error = DesktopUrlAcquisitionError("current VT URL unavailable")

    def fail_current_url(*_args, **_kwargs):
        raise acquisition_error

    monkeypatch.setattr(fixture_support, "get_web_url", fail_current_url)

    with pytest.raises(DesktopUrlAcquisitionError) as captured:
        fixture_support._resolve_web_guest_url(
            object(),
            logging.getLogger("current-room-test"),
        )

    assert "Cached config URLs are not valid fallbacks" in str(captured.value)
