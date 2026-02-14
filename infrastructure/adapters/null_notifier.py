"""Null adapter for ProgressNotifierPort (tests, CLI, API)."""


class NullProgressNotifier:
    """No-op progress notifier — silently discards all notifications."""

    def notify_progress(self, current: int, total: int) -> None:
        pass
