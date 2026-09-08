import time
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import utils.conftest as fixtures
from utils.process_handler import ProcessManager


class FakeProcessManager:
    def __init__(self):
        self.kill_count = 0
        self.start_count = 0

    def kill_process(self):
        self.kill_count += 1

    def start_process(self):
        self.start_count += 1


class FakeRequest:
    def __init__(self):
        self.finalizers = []

    def addfinalizer(self, finalizer):
        self.finalizers.append(finalizer)


class FakeOptions:
    def __init__(self):
        self.binary_location = None

    def add_argument(self, _value):
        pass

    def add_experimental_option(self, _name, _value):
        pass


class FakeDriver:
    def __init__(self):
        self.quit_count = 0

    def maximize_window(self):
        pass

    def execute_cdp_cmd(self, _command, _parameters):
        pass

    def quit(self):
        self.quit_count += 1


class FixtureCleanupTests(unittest.TestCase):
    def test_publisher_is_killed_before_and_after_each_test(self):
        process_manager = FakeProcessManager()
        with patch.object(
            fixtures,
            "ProcessManager",
            return_value=process_manager,
        ), patch.object(time, "sleep", return_value=None):
            fixture = fixtures.ensure_vt_killed_before_test.__wrapped__()
            next(fixture)
            self.assertEqual(1, process_manager.kill_count)

            with self.assertRaises(StopIteration):
                next(fixture)

        self.assertEqual(2, process_manager.kill_count)

    def test_browser_cleanup_is_registered_during_fixture_setup(self):
        process_manager = FakeProcessManager()
        web_driver = FakeDriver()
        request = FakeRequest()
        test_config = SimpleNamespace(
            get_chrome_options=lambda: [],
            media=SimpleNamespace(
                camera_for_selection="camera",
                mic_for_selection="microphone",
            ),
        )

        with patch.object(
            fixtures,
            "ProcessManager",
            return_value=process_manager,
        ), patch.object(fixtures, "Options", FakeOptions), patch.object(
            fixtures,
            "Service",
            return_value=object(),
        ), patch.object(
            fixtures.webdriver,
            "Chrome",
            return_value=web_driver,
        ), patch.object(fixtures, "config", test_config):
            result = fixtures.driver.__wrapped__(None, request)

        self.assertIs(web_driver, result)
        self.assertEqual(1, process_manager.start_count)
        self.assertEqual(1, len(request.finalizers))

        request.finalizers[0]()
        self.assertEqual(1, web_driver.quit_count)

    def test_wm_close_failure_falls_back_to_process_terminate(self):
        process = Mock()
        process.pid = 123
        process.children.return_value = []
        process.terminate.side_effect = lambda: setattr(process, "alive", False)
        process.alive = True

        manager = object.__new__(ProcessManager)
        manager.process_name = "VT_Publisher.exe"
        manager.logger = Mock()
        manager.get_window_handle = Mock(return_value=456)
        manager.iter_processes = lambda: iter([process] if process.alive else [])

        with patch(
            "utils.process_handler.win32gui.PostMessage",
            side_effect=RuntimeError("access denied"),
        ):
            manager.kill_process()

        process.terminate.assert_called_once_with()

    def test_successful_wm_close_does_not_terminate_process(self):
        process = Mock()
        process.pid = 123
        process.alive = True

        manager = object.__new__(ProcessManager)
        manager.process_name = "VT_Publisher.exe"
        manager.logger = Mock()
        manager.get_window_handle = Mock(return_value=456)
        manager.iter_processes = lambda: iter([process] if process.alive else [])

        def close_process(*_args):
            process.alive = False

        with patch(
            "utils.process_handler.win32gui.PostMessage",
            side_effect=close_process,
        ):
            manager.kill_process()

        process.terminate.assert_not_called()

    def test_windowless_process_uses_terminate_only_after_grace_period(self):
        process = Mock()
        process.pid = 123
        process.alive = True
        process.terminate.side_effect = lambda: setattr(process, "alive", False)

        manager = object.__new__(ProcessManager)
        manager.process_name = "VT_Publisher.exe"
        manager.logger = Mock()
        manager.get_window_handle = Mock(return_value=None)
        manager.iter_processes = lambda: iter([process] if process.alive else [])

        # The first value creates the deadline; the second expires the graceful
        # stage immediately so the test does not really wait ten seconds.
        with patch("utils.process_handler.time.time", side_effect=[0, 11]):
            manager.kill_process()

        process.terminate.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
