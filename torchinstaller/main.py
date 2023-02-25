from pathlib import Path
import argparse
import subprocess
import re
import tomlkit
from .utils import *


def main():
    configPath = Path(__file__).parent / "config" / "commands.toml"
    config = loadConfig(configPath)
    parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     '--poetry', '-p',
    #     action='store_true',
    #     default=False,
    #     help='Uses poetry for install. Creates a torch source and adds torch to pyproject.toml'
    # )
    # parser.add_argument(
    #     '--dryrun', '-d',
    #     action='store_true',
    #     default=Tre,
    #     help="just prints the commands that would be run"
    # )
    # parser.add_argument(
    #     '--install', '-i',
    #     help='run install commands'
    # )

    parser.add_argument(
        "--pytorch",
        "-pt",
        help="Flag to install pytorch",
        default=False,
        action='store_true'
    )
    parser.add_argument(
        "--pyg",
        "-pyg",
        help="Flag to install pytorch-geometric",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        '--pyg-lib-source',
        '-pyg-src',
        help="Pytorch Geometric doesn't support wheels for M1/M2 macs, they recomment installing from source",
        default=False,
        action='store_true',
        dest='pyg_lib_source'
    )
    parser.add_argument(
        "--cuda",
        "-c",
        type=str,
        default=None,
        choices=cudaVersions(config),
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
    command_key = "pip" if args.use in ['pip', 'poetry'] else args.use

    torchCudaLookup = commandToLookup(config["torch"][command_key])
    pygLookup = commandToLookup(config["pygeo"][command_key])

    installer = args.use

    pyVersion = pythonVersion()

    cudaVersion, detected = getCudaVersion(torchCudaLookup)

    if args.cuda is None:
        cudaVersion, detected = getCudaVersion(torchCudaLookup)
        print(f"System CUDA: {detected}\nUsing CUDA: {cudaVersion}")
    else:
        cudaVersion = args.cuda
        print(f"User specified CUDA: {cudaVersion}")
        print(f"System CUDA: {detected}\nUsing CUDA: {cudaVersion}")

    if getPlatform() == "darwin":
        cudaVersion == "macOS"

    if cudaVersion in ["macOS", "cpu"]:
        print("CPU ONLY")

    # try:

    command = torchCudaLookup[cudaVersion][-1][1]

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
            pygCommand = pygLookup[cudaVersion][-1][1]
            cArgs = [installer, "install"]

            if args.pyg_lib_source:
                cArgs.append("git+https://github.com/pyg-team/pyg-lib.git")
                run(cArgs, args.install)
                cArgs = cArgs[:-1]
                pygCommand.pop('pyg_lib')
                pygCommand.pop('url')

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
