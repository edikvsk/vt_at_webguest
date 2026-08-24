"""Reliable acquisition of dynamic URLs exposed by VT Publisher."""

from __future__ import annotations

import configparser
import time
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import urlparse


class DesktopUrlAcquisitionError(RuntimeError):
    """Raised when VT Publisher never exposes a usable URL."""


def normalize_desktop_url(value: object) -> Optional[str]:
    """Return a normalized HTTP(S) URL, or ``None`` for clipboard noise."""
    if value is None:
        return None

    candidate = str(value).strip().strip("\"'")
    if not candidate:
        return None

    parsed = urlparse(candidate)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return None
    return candidate


def is_web_guest_url(value: object) -> bool:
    """Return whether a value points to a concrete ``/wg2/<room>`` page."""
    candidate = normalize_desktop_url(value)
    if not candidate:
        return False

    path_parts = [part for part in urlparse(candidate).path.split("/") if part]
    return len(path_parts) >= 2 and path_parts[0].lower() == "wg2"


def read_url_from_config(
    config_path: str,
    key: str,
    validator: Callable[[object], bool],
) -> Optional[str]:
    """Read and validate a URL from a runtime INI file when one exists."""
    path = Path(config_path)
    if not path.is_file():
        return None

    parser = configparser.ConfigParser()
    parser.read(str(path), encoding="utf-8")
    candidate = parser.get("DEFAULT", key, fallback=None)
    return normalize_desktop_url(candidate) if validator(candidate) else None


def acquire_desktop_url(
    desktop_app_page,
    logger,
    source_title: str,
    copy_command: str,
    clipboard_read: Callable[[], object],
    clipboard_clear: Optional[Callable[[], None]] = None,
    timeout: float = 60.0,
    retry_interval: float = 1.0,
) -> str:
    """Start publishing when needed and retry the context-menu copy action.

    VT creates its WebGuest room asynchronously.  A successful click on
    ``Start Publishing`` therefore does not mean that the copy command or its
    clipboard value is ready.  This function retries the complete UI action
    until VT exposes a valid URL or the deadline is reached.
    """
    expects_web_guest = copy_command.casefold() == "copy web guest url"
    validator = is_web_guest_url if expects_web_guest else (
        lambda value: normalize_desktop_url(value) is not None
    )
    deadline = time.monotonic() + max(timeout, 0.1)
    attempt = 0
    publishing_started = False
    failures = []

    while time.monotonic() < deadline:
        attempt += 1
        try:
            remaining = max(0.5, deadline - time.monotonic())
            desktop_app_page.focus_click_vt_source_item(
                source_title,
                timeout=min(5.0, remaining),
            )

            if (
                not publishing_started
                and desktop_app_page.check_element_enabled_by_title_part(
                    "Start Publishing"
                )
            ):
                desktop_app_page.click_button_by_name("Start Publishing")
                publishing_started = True
                logger.info(
                    "VT publishing started; waiting for the dynamic URL."
                )
                time.sleep(min(2.0, max(0.0, deadline - time.monotonic())))

            if clipboard_clear is not None:
                try:
                    clipboard_clear()
                except Exception as clear_error:
                    failures.append(
                        "clipboard clear failed: "
                        f"{type(clear_error).__name__}: {clear_error}"
                    )

            remaining = max(0.5, deadline - time.monotonic())
            desktop_app_page.right_click_vt_source_item(
                source_title,
                timeout=min(5.0, remaining),
            )
            time.sleep(0.4)
            remaining = max(0.5, deadline - time.monotonic())
            desktop_app_page.click_vt_source_item(
                copy_command,
                timeout=min(5.0, remaining),
            )

            clipboard_deadline = min(deadline, time.monotonic() + 2.5)
            while time.monotonic() < clipboard_deadline:
                candidate = clipboard_read()
                if validator(candidate):
                    url = normalize_desktop_url(candidate)
                    parsed = urlparse(url)
                    logger.info(
                        "VT supplied %s from %s%s.",
                        copy_command,
                        parsed.netloc,
                        "/wg2/<room>" if expects_web_guest else parsed.path,
                    )
                    return url
                time.sleep(0.2)

            failures.append(
                f"attempt {attempt}: {copy_command} did not put a valid URL "
                "on the clipboard"
            )
        except Exception as error:
            failures.append(
                f"attempt {attempt}: {type(error).__name__}: {error}"
            )

        remaining = deadline - time.monotonic()
        if remaining > 0:
            time.sleep(min(retry_interval, remaining))

    recent_failures = "; ".join(failures[-5:]) or "no UI action completed"
    raise DesktopUrlAcquisitionError(
        f"VT Publisher did not expose '{copy_command}' for source "
        f"'{source_title}' within {timeout:g} seconds after {attempt} "
        f"attempt(s). Recent failures: {recent_failures}"
    )
