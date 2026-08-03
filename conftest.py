import re
import sys
from pathlib import Path

import pytest

from utils.conftest import *  # noqa: F401,F403


for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="backslashreplace")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Keep browser evidence for every failed WebGuest setup or test."""
    outcome = yield
    report = outcome.get_result()
    if not report.failed or report.when not in {"setup", "call"}:
        return

    driver = item.funcargs.get("driver")
    if driver is None:
        return

    artifact_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", item.nodeid)
    artifact_directory = Path(".test-results") / artifact_name
    artifact_directory.mkdir(parents=True, exist_ok=True)

    screenshot_path = artifact_directory / f"{report.when}.png"
    page_source_path = artifact_directory / f"{report.when}.html"
    metadata_path = artifact_directory / f"{report.when}.txt"
    try:
        driver.save_screenshot(str(screenshot_path.resolve()))
        page_source_path.write_text(driver.page_source, encoding="utf-8")
        metadata_path.write_text(
            f"URL: {driver.current_url}\nTitle: {driver.title}\n",
            encoding="utf-8",
        )
        report.sections.append(
            (
                "WebGuest failure artifacts",
                str(artifact_directory.resolve()),
            )
        )
    except Exception as error:
        report.sections.append(
            ("WebGuest artifact capture error", str(error))
        )


