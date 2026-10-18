"""Shared test setup.

Tests must run with no network access (FR-TST-01). This blocks every outbound
socket connection for the whole test session, so a test that tries to reach
the internet fails loudly instead of silently depending on it.
"""

import socket

import pytest


class NetworkBlockedError(RuntimeError):
    pass


def _blocked(*args, **kwargs):
    raise NetworkBlockedError("Network access is not allowed in tests (FR-TST-01).")


@pytest.fixture(autouse=True, scope="session")
def _no_network():
    original_connect = socket.socket.connect
    original_create = socket.create_connection
    socket.socket.connect = _blocked
    socket.create_connection = _blocked
    yield
    socket.socket.connect = original_connect
    socket.create_connection = original_create
