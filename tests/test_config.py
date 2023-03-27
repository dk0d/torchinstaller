from pathlib import Path
from torchinstaller.utils import loadConfig, availableCudaVersions


def test_parse_config():

    config_dir = "./torchinstaller/config/commands.toml"
    config = loadConfig(Path(config_dir))
    cVersions = availableCudaVersions(config)
    assert config is not None


def test_platforms():
    # TODO:
    pass
