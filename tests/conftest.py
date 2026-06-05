import os
import pytest

# ------------------------------------------------------------------ #
# Centralised URL config                                               #
#                                                                      #
# Override by setting the LMS_FRONTEND_URL environment variable:      #
#   $env:LMS_FRONTEND_URL = "http://localhost:5174"                   #
#   pytest tests/                                                      #
# ------------------------------------------------------------------ #

BASE_URL = os.environ.get("LMS_FRONTEND_URL", "http://localhost:5173")


def pytest_configure(config):
    """Expose BASE_URL so every test module can import it."""
    config.addinivalue_line(
        "markers", "smoke: quick smoke tests"
    )


# Make BASE_URL available as a pytest fixture too (optional convenience)
@pytest.fixture(scope="session")
def base_url():
    return BASE_URL
