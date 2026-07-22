from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from unittest.mock import patch

import pytest


@dataclass
class _Mocker:
    _patches: list[Any] = field(default_factory=list)

    def patch(self, target: str, *args: Any, **kwargs: Any) -> Any:
        mocked = patch(target, *args, **kwargs)
        started = mocked.start()
        self._patches.append(mocked)
        return started


@pytest.fixture
def mocker() -> Any:
    helper = _Mocker()
    try:
        yield helper
    finally:
        while helper._patches:
            helper._patches.pop().stop()