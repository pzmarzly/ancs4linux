from typing import Any, Callable
import gi

gi.require_version("GLib", "2.0")
from gi.repository import GLib  # type: ignore # dynamic via PyGObject


class TaskRestarter:
    def __init__(
        self,
        max_attempts: int,
        interval: int,
        fn: Callable[[], bool],
        success_fn: Callable[[], Any],
        failure_fn: Callable[[], Any],
    ) -> None:
        self.attempts = 0
        self.max_attempts = max_attempts
        self.interval = interval
        self.fn = fn
        self.success_fn = success_fn
        self.failure_fn = failure_fn

    def try_running_tick(self) -> bool:
        if self.fn():
            self.success_fn()
            return False

        self.attempts += 1
        if self.attempts > self.max_attempts:
            self.failure_fn()
            return False

        # Retry.
        return True

    def try_running_bg(self):
        GLib.timeout_add_seconds(self.interval, self.try_running_tick)
