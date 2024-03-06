from pathlib import Path
from torchinstaller.utils import getCommandForPlatform, loadConfig, availableCudaVersions
from torchinstaller._soup import get_latest_version
from torchinstaller._parse import sync_commands


def test_parse_config():
    config_dir = "./torchinstaller/config/commands.toml"
    config = loadConfig(Path(config_dir))
    cVersions = availableCudaVersions(config)
    assert config is not None


def test_parse_commands():
    commands = sync_commands()
    assert "+" not in commands


def test_get_latest():
    version = get_latest_version()
    assert version is not None


def test_derive_latest():
    config = loadConfig(Path("./torchinstaller/config/commands.toml"))
    for command_key in ["pip", "conda", "mamba"]:
        print("-" * 80)
        print(command_key)
        for platform in availableCudaVersions(config):
            print(platform)
            # print("-" * 80
        # command = getCommandForPlatform(config, command_key, "latest", platform)
        # print(command)
