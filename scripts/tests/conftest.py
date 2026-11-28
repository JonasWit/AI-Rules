"""Shared pytest fixtures for scripts/tests/.

Loads scripts/check.py once per test session so every test file exercises the same
CLI entrypoint without duplicating module-loading boilerplate.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

CHECK_SCRIPT = Path(__file__).resolve().parents[1] / "check.py"


@pytest.fixture(scope="session")
def check_module():
    spec = importlib.util.spec_from_file_location("check", CHECK_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["check"] = module
    spec.loader.exec_module(module)
    return module
