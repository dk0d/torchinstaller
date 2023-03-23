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

    try:
        url = command["url"]
    except:
        url = None

    use_poetry = args.use == "poetry"

    if use_poetry:
        if args.pytorch:
            if url is not None:
                run(["poetry", "source", "add", "torch", command["url"]], args.install)

            commandArgs = ["poetry", "add"]
            commandArgs.extend(commandToStrings(command))

            if url is not None:
                commandArgs.extend(["--source", "torch"])

            run(commandArgs, args.install)

        if args.lightning:
            run(["poetry", "add", "pytorch-lightning"], args.install)
    else:
        if args.pytorch:
            commandArgs = [installer, "install"]
            commandArgs.extend(commandToStrings(command))

            if url is not None and installer == "pip":
                commandArgs.extend(["--extra-index-url", command["url"]])

            run(commandArgs, args.install)

        if args.lightning:
            lightning = [installer, "install", "pytorch-lightning"]
            if installer == "pip":
                run(lightning, args.install)
            else:
                lightning.append("-c conda-forge")
                run(lightning, args.install)

        if args.pyg:
            cArgs = [installer, "install"]

            if args.pyg_lib_source:
                cArgs.append("git+https://github.com/pyg-team/pyg-lib.git")
                run(cArgs, args.install)
                cArgs = cArgs[:-1]
                pygCommand.pop("pyg_lib")
                pygCommand.pop("url")

            cArgs.extend(commandToStrings(pygCommand))

            if "url" in pygCommand:
                cArgs.extend(["-f", pygCommand["url"]])

            run(cArgs, args.install)

    # except Exception as err:
    #     print('Install failed')
    #     print(f'{err}')
    #     raise err


if __name__ == "__main__":
    main()
