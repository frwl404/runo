import pytest


@pytest.fixture
def config_path(tmp_path):
    return tmp_path / "cfg.toml"
