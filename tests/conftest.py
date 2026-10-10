"""Pytest configuration for CanopyTrace test suite."""

import os
import pytest

# Ensure unit and benchmark test suites execute deterministically offline
os.environ["CANOPYTRACE_MOCK_HARNESS"] = "1"
