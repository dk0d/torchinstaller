from pathlib import Path
from  rich import print
import argparse
from .utils import *


def main():
    configPath = Path(__file__).parent / "config" / "commands.toml"
    config = loadConfig(configPath)
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--pytorch",
        "-pt",
        help="Flag to install pytorch",
        default=False,
        action="store_true",
    )
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
        help="Flag to install PyG from source. i.e. PyG doesn't support wheels for M1/M2 macs, they recommend installing from source",
        default=False,
        action="store_true",
        dest="pyg_lib_source",
    )
    parser.add_argument(
        "--cuda",
        "-c",
        type=str,
        default=None,
        choices=availableCudaVersions(config),
        help="Manually specify platform version (cuda or rocm) instead of auto-detect (useful for cluster installations).",
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
        print(f"[red bold]Install Failed: {e}")

    installer = args.use

    command_key = "conda" if installer in ["conda", "mamba"] else installer
    command_key = "pip" if installer in ["pip", "poetry"] else installer 

    python_version = getPythonVersion()
    system_platform = getSystemPlatform()

    platform, detected = getCudaVersion(availableCudaVersions(config))

    if system_platform == "darwin":
        platform = "macOS"
    else:
        if args.cuda is None:
            print(f"[blue bold]System CUDA: {detected}\nUsing CUDA: {platform}")
        else:
            platform = args.cuda
            print(f"[yellow bold]User specified CUDA: {platform}")
            print(f"[blue bold]System CUDA: {detected}\nUsing CUDA: {platform}")

    if platform in ["cpu"]:
        print("[orange bold]CPU ONLY")
    elif platform in ["macOS"]:
        print("[yellow bold]macOS (pytorch 2.0 supports apple silicon)")

    try:
        if args.pytorch:
            command = getCommandForPlatform(config["torch"][command_key], platform)
            handleTorchCommand(installer, command, args.install)

        if args.lightning:
            handleLightningCommand(installer, args.install)

        if args.pyg:
            pygCommand = getCommandForPlatform(config["pygeo"][command_key], platform)
            handlePyGCommand(installer, pygCommand, args.pyg_lib_source, args.install)

        if not any([args.pytorch, args.lightning, args.pyg]):
            print(f'[red bold]NO COMMANDS Selected')
            print(f'[green bold]Run torchinstall -h to see flags for installing')

    except Exception as err:
        print("Install failed")
        print(f"{err}")
        raise err


if __name__ == "__main__":
    main()
