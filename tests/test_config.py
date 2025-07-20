from pathlib import Path
from torchinstaller.utils import getCommandForPlatform, getCudaVersion, loadConfig, availableCudaVersions
from torchinstaller._soup import get_latest_version
from torchinstaller._parse import sync_commands


def test_parse_config_toml():
    config_dir = "./src/torchinstaller/config/commands.toml"
    config = loadConfig(Path(config_dir))
    cVersions = availableCudaVersions(config)
    assert config is not None


def test_parse_config():
    config_dir = "./src/torchinstaller/config/commands.yaml"
    config = loadConfig(Path(config_dir))
    cVersions = availableCudaVersions(config)
    assert config is not None


def test_parse_commands():
    commands = sync_commands()
    assert "+" not in commands


def test_get_latest():
    version = get_latest_version()
    assert version is not None


def test_build_commands():
    config = loadConfig(Path("./src/torchinstaller/config/commands.yaml"))
    for command_key in ["pip", "conda", "mamba"]:
        print(command_key)
        for platform in availableCudaVersions(config):
            try:
                print(platform)
                command = getCommandForPlatform(config, command_key, "latest", platform)
                print(command)
            except Exception as e:
                print(f"{platform} Error: ", e)
