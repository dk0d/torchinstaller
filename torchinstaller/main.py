from pathlib import Path
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
        help="Pytorch Geometric doesn't support wheels for M1/M2 macs, they recomment installing from source",
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
        help="Manually specify cuda version instead of auto-detect (useful for cluster installations).",
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
        "-use",
        default="pip",
        choices=["pip", "conda", "mamba", "poetry"],
        help="set command to install with",
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
        print(f"Install Failed: {e}")

    command_key = "conda" if args.use in ["conda", "mamba"] else args.use
    command_key = "pip" if args.use in ["pip", "poetry"] else args.use

    python_version = pythonVersion()
    system_platform = getPlatform()

    installer = args.use

    platform, detected = getCudaVersion(availableCudaVersions(config))

    if system_platform == "darwin":
        platform = "macOS"
    else:
        if args.cuda is None:
            print(f"System CUDA: {detected}\nUsing CUDA: {platform}")
        else:
            platform = args.cuda
            print(f"User specified CUDA: {platform}")
            print(f"System CUDA: {detected}\nUsing CUDA: {platform}")

    if platform in ["cpu"]:
        print("CPU ONLY")
    elif platform in ["macOS"]:
        print("macOS (pytorch 2.0 supports apple silicon)")

    # try:
    command = getCommandForPlatform(config["torch"][command_key], platform)
    pygCommand = getCommandForPlatform(config["pygeo"][command_key], platform)


    if args.pytorch:
        handleTorchCommand(installer, command, args.install)

    if args.lightning:
        handleLightningCommand(installer, args.install)

    if args.pyg:
        handlePyGCommand(installer, pygCommand, args.pyg_lib_source, args.install)

    # except Exception as err:
    #     print('Install failed')
    #     print(f'{err}')
    #     raise err


if __name__ == "__main__":
    main()
