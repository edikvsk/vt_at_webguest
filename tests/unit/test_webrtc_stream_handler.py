from unittest.mock import Mock, patch

import pytest
from selenium.common.exceptions import TimeoutException

from utils.webrtc_stream_handler import StreamHandler


def test_frame_dimensions_must_be_stable_in_consecutive_samples():
    handler = StreamHandler(Mock())
    handler.get_video_frame_dimensions = Mock(
        side_effect=["640X480", "1920X1080", "1280X720", "1920X1080", "1920X1080"]
    )

    with patch("utils.webrtc_stream_handler.time.sleep", return_value=None):
        result = handler.wait_for_video_frame_dimensions(
            "1920X1080",
            timeout=10,
            stable_samples=2,
        )

    assert result == "1920X1080"
    assert handler.get_video_frame_dimensions.call_count == 5


def test_frame_dimensions_timeout_reports_last_observed_value():
    handler = StreamHandler(Mock())
    handler.get_video_frame_dimensions = Mock(return_value="1280X720")

    with pytest.raises(TimeoutException, match="last value: None"):
        handler.wait_for_video_frame_dimensions("1920X1080", timeout=0)


def test_average_fps_waits_for_completed_browser_measurement():
    driver = Mock()
    driver.execute_script.side_effect = [
        True,
        None,
        [29.0, 30.0, 31.0],
    ]
    handler = StreamHandler(driver)

    assert handler.calculate_average_stream_fps(duration=3) == 30.0


@pytest.mark.parametrize(
    ("measured", "expected"),
    [
        (5.0, "AUDIO BITRATE\n6K"),
        (8.0, "AUDIO BITRATE\n10K"),
        (16.0, "AUDIO BITRATE\n20K"),
        (33.36, "AUDIO BITRATE\n40K"),
        (80.0, "AUDIO BITRATE\n96K"),
        (160.0, "AUDIO BITRATE\n192K"),
        (420.0, "AUDIO BITRATE\n510K"),
    ],
)
def test_audio_bitrate_uses_payload_tolerance(measured, expected):
    assert StreamHandler.format_audio_bitrate(measured) == expected


def test_audio_bitrate_outside_supported_presets_is_not_hidden():
    assert StreamHandler.format_audio_bitrate(300) == "AUDIO BITRATE 300.0K"
