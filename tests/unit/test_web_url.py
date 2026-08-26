from unittest.mock import ANY, Mock, patch

from utils.web_url import acquire_desktop_url


def test_url_acquisition_waits_for_delayed_clipboard_render():
    desktop = Mock()
    desktop.check_element_enabled_by_title_part.return_value = False
    clipboard_read = Mock(
        side_effect=["", "clipboard is still rendering", "https://host/wg2/room-id"]
    )

    with patch("utils.web_url.time.sleep", return_value=None):
        result = acquire_desktop_url(
            desktop_app_page=desktop,
            logger=Mock(),
            source_title="Web Guest",
            copy_command="Copy Web Guest URL",
            clipboard_read=clipboard_read,
            clipboard_clear=Mock(),
            timeout=1,
        )

    assert result == "https://host/wg2/room-id"
    desktop.right_click_vt_source_item.assert_called_once()
    desktop.click_vt_source_item.assert_called_once_with(
        "Copy Web Guest URL",
        timeout=ANY,
    )
