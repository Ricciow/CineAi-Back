import os
from unittest.mock import patch

# Set environment variables for testing BEFORE any imports that might trigger Settings()
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "mongodb://localhost:27017"
os.environ["OPENROUTER_API_KEY"] = "test-key"
os.environ["FRONTEND_URLS"] = '["http://localhost:5173"]'

# Mock DotEnvSettingsSource to avoid issues with existing .env file during tests
try:
    from pydantic_settings.sources.providers.dotenv import DotEnvSettingsSource
    patch('pydantic_settings.sources.providers.dotenv.DotEnvSettingsSource.__call__', return_value={}).start()
except ImportError:
    pass

import pytest

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    pass
