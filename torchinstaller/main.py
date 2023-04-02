from pathlib import Path
from rich import print
import argparse

from .utils import (
    loadConfig,
    availableCudaVersions,
    getPythonVersion,
    getSystemPlatform,
    getCudaVersion,
    getCommandForPlatform,
    handlePyGCommand,
    handleTorchCommand,
    handleLightningCommand,
)


def main():
    LATEST_VERSION = "2.0.0"

    configPath = Path(__file__).parent / "config" / "commands.toml"
    config = loadConfig(configPath)
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--pytorch",
        "-pt",
        help=(
            "Flag to install pytorch, can optionally specify a desired version."
            " Must be full semantic version, e.g. 1.13.1, not 1.13, defaults to `latest`"
        ),
        nargs="?",
        const="latest",
    )
    parser.add_argument
    parser.add_argument(
        "--pyg",
        "-pyg",
        help="Flag to install pytorch-geometric",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--pyg-lib-source",
        "-pyg-src",
        help=(
            "Flag to install PyG from source. i.e. PyG doesn't support wheels for M1/M2 macs."
            " They recommend installing from source"
        ),
        default=False,
        action="store_true",
        dest="pyg_lib_source",
    )
    parser.add_argument(
        "--compute-platform",
        "-c",
        type=str,
        default=None,
        dest="cuda",
        choices=availableCudaVersions(config),
        help=(
            "Manually specify platform version (cuda or rocm) instead of"
            "auto-detect (useful for cluster installations)."
        ),
    )
    parser.add_argument(
        "--lightning",
        "-l",
        action="store_true",
        help="Flag to install pytorch-lightning",
        default=False,
    )
    parser.add_argument(
        "--use",
        "-u",
        default="pip",
        choices=["pip", "conda", "mamba", "poetry"],
        help="set command to install with.",
    )
    parser.add_argument(
        "-install",
        "-i",
        default=False,
        action="store_true",
        help="Run installation (default is to dry run commands)",
    )

    try:
        args = parser.parse_args()
    except Exception as e:
        print("-" * 80)
        print("[red bold]Argument Error")
        print(e)
        print("-" * 80)
        exit(0)

    installer = args.use

    if installer in ["conda", "mamba"]:
        command_key = "conda"
    elif installer in ["pip", "poetry"]:
        command_key = "pip"
    else:
        raise NotImplementedError("Unsupported installer")

    getPythonVersion()
    system_platform = getSystemPlatform()

    platform, detected = getCudaVersion(availableCudaVersions(config))

    print("-" * 100)
    if system_platform == "darwin":
        platform = "macOS"
    else:
        if args.cuda is None:
            print(f"[blue bold]System platform: {detected}\nUsing platform: {platform}")
        else:
            platform = args.cuda
            print(f"User specified platform: [yellow bold]{platform}")
            print(f"System platform: [blue bold]{detected}[/blue bold]\nUsing platform: [blue bold]{platform}")

    if platform in ["cpu"]:
        print("[orange bold]CPU ONLY")
    elif platform in ["macOS"]:
        print("[yellow bold]macOS (pytorch 2.0 supports apple silicon)")

    print("-" * 100)

    try:
        if args.pytorch is not None:
            command = getCommandForPlatform(config, command_key, args.pytorch, platform)
            handleTorchCommand(installer, command, args.install)

        if args.lightning:
            handleLightningCommand(installer, args.install)

        if args.pyg:
            version = LATEST_VERSION if args.pytorch == "latest" else args.pytorch
            handlePyGCommand(installer, version, platform, args.pyg_lib_source, args.install)

        if not any([args.pytorch, args.lightning, args.pyg]):
            print("[red bold]NO COMMANDS Selected")
            print("[green bold]Run torchinstall -h to see flags for installing")

    except Exception as err:
        print("Install failed")
        print(f"{err}")
        raise err
    print("-" * 100)


if __name__ == "__main__":
    main()
