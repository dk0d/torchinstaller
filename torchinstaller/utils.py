from pathlib import Path
from rich import print
import tomlkit
import subprocess
import re

VALID_PYG_BUILDS = [
    "torch-1.10.0+cpu",
    "torch-1.10.1+cpu",
    "torch-1.10.2+cpu",
    "torch-1.10.0+cu102",
    "torch-1.10.1+cu102",
    "torch-1.10.2+cu102",
    "torch-1.10.0+cu113",
    "torch-1.10.1+cu113",
    "torch-1.10.2+cu113",
    "torch-1.10.0+cu111",
    "torch-1.10.1+cu111",
    "torch-1.10.2+cu111",
    "torch-1.11.0+cpu",
    "torch-1.11.0+cu102",
    "torch-1.11.0+cu113",
    "torch-1.11.0+cu115",
    "torch-1.12.0+cpu",
    "torch-1.12.1+cpu",
    "torch-1.12.0+cu102",
    "torch-1.12.1+cu102",
    "torch-1.12.0+cu113",
    "torch-1.12.1+cu113",
    "torch-1.12.0+cu116",
    "torch-1.12.1+cu116",
    "torch-1.13.0+cpu",
    "torch-1.13.1+cpu",
    "torch-1.13.0+cu116",
    "torch-1.13.1+cu116",
    "torch-1.13.0+cu117",
    "torch-1.13.1+cu117",
    "torch-1.4.0+cpu",
    "torch-1.4.0+cu100",
    "torch-1.4.0+cu101",
    "torch-1.4.0+cu92",
    "torch-1.4.0",
    "torch-1.5.0+cpu",
    "torch-1.5.0+cu101",
    "torch-1.5.0+cu102",
    "torch-1.5.0+cu92",
    "torch-1.5.0",
    "torch-1.6.0+cpu",
    "torch-1.6.0+cu101",
    "torch-1.6.0+cu102",
    "torch-1.6.0+cu92",
    "torch-1.6.0",
    "torch-1.7.0+cpu",
    "torch-1.7.1+cpu",
    "torch-1.7.0+cu101",
    "torch-1.7.1+cu101",
    "torch-1.7.0+cu102",
    "torch-1.7.1+cu102",
    "torch-1.7.0+cu110",
    "torch-1.7.1+cu110",
    "torch-1.7.0+cu92",
    "torch-1.7.1+cu92",
    "torch-1.7.0",
    "torch-1.7.1",
    "torch-1.8.0+cpu",
    "torch-1.8.1+cpu",
    "torch-1.8.0+cu101",
    "torch-1.8.1+cu101",
    "torch-1.8.0+cu102",
    "torch-1.8.1+cu102",
    "torch-1.8.0+cu111",
    "torch-1.8.1+cu111",
    "torch-1.9.0+cpu",
    "torch-1.9.1+cpu",
    "torch-1.9.0+cu102",
    "torch-1.9.1+cu102",
    "torch-1.9.0+cu111",
    "torch-1.9.1+cu111",
    "torch-2.0.0+cpu",
    "torch-2.0.0+cu117",
    "torch-2.0.0+cu118",
]


def handleTorchCommand(installer, command: dict, run_install: bool):
    commandArgs = [installer, "install"]
    commandArgs.extend(commandToStrings(command["packages"]))
    commandArgs.extend(command.get("flags", []))
    run(commandArgs, run_install)


def handleLightningCommand(installer, run_install):
    if installer in ["poetry"]:
        run(["poetry", "add", "pytorch-lightning"], run_install)
    else:
        lightning = [installer, "install", "pytorch-lightning"]
        if installer == "pip":
            run(lightning, run_install)
        else:
            lightning.append("-c conda-forge")
            run(lightning, run_install)


def handlePyGCommand(installer, version, platform, pyg_lib_source, run_install, install_optionals=True):

    cArgs = [
        installer,
        "install",
        "torch_geometric",
    ]

    if installer in ["mamba", "conda"]:
        cArgs.extend(["pyg", "-c", "pyg"])
        run(cArgs, run_install)
        return

    if platform.lower() == "macos":
        platform = "cpu"

    if pyg_lib_source:
        cArgs.append("git+https://github.com/pyg-team/pyg-lib.git")
        run(cArgs, run_install)
        cArgs = cArgs[:-1]
    else:
        cArgs.append("pyg-lib")

    if install_optionals:
        cArgs.extend(
            [
                "torch_scatter",
                "torch_sparse",
                "torch_cluster",
                "torch_spline_conv",
            ]
        )
        torchVersion = f"torch-{version}+{platform}"
        if torchVersion not in VALID_PYG_BUILDS:
            print(f"[bold yellow]Unsupported Pytorch-Geometric platform: {torchVersion}")
            return
        url = f"https://data.pyg.org/whl/{torchVersion}.html"
        cArgs.extend(["-f", url])

    run(cArgs, run_install)


def handlePoetryCommand(command, run_install):
    try:
        url = command["url"]
    except Exception:
        url = None

    if url is not None:
        run(["poetry", "source", "add", "torch", command["url"]], run_install)

    commandArgs = ["poetry", "add"]
    commandArgs.extend(commandToStrings(command))

    if "url" in command and command["url"] is not None:
        commandArgs.extend(["--source", "torch"])

    run(commandArgs, run_install)


# Related to commands.bak.toml and pyg-commands.toml


def getCommandForPlatform(config, command_key, version, platform):
    commands = config[platform][command_key]
    try:
        command = list(filter(lambda v: v["version"] == version, commands))[0]
        return command
    except Exception:
        print(f"[red bold]Could not find version {version} for requested platform")
        print(f"\nAvailable pytorch versions on {platform}\n" + "-" * 80)
        for c in commands:
            print(f"- {c['version']}")
        print("-" * 80)
        exit(0)


def remove_none(d):
    keys = list(d.keys())
    for k in keys:
        if isinstance(d[k], dict):
            remove_none(d[k])
        elif d[k] is None:
            d.pop(k)
    return d


def loadConfig(path: Path) -> dict:
    try:
        with path.open("r") as fp:
            cfg = tomlkit.load(fp)
            # print(cfg)
        return cfg.unwrap()
    except Exception:
        print("[red bold]Commands configuration not found, package installation error")
        exit(1)


def closestLatestVersion(cudaVersion, availableVersions):
    goodVersions = list(filter(lambda x: x >= cudaVersion, availableVersions))
    goodVersions.sort()
    return goodVersions[0]


def hasCommand(name):
    """
    Check whether `name` is in PATH and is executable
    """
    from shutil import which

    return which(name) is not None


def getCudaVersion(availableVersions):
    if hasCommand("nvidia-smi"):
        result = subprocess.run(["nvidia-smi"], capture_output=True)
        output = str(result.stdout, encoding="utf-8")
        version = re.search(r"CUDA\s+Version:\s+([\d\.]+)\s*", output)
        cudaVersions = list(filter(lambda v: "cu" in v, availableVersions))
        if version is not None:
            try:
                cuVersion = f'cu{version.group(1).replace(".", "")}'
                closest = closestLatestVersion(cuVersion, cudaVersions)
                return closest, cuVersion
            except Exception:
                pass
    return "cpu", None


def getPythonVersion(withMicro=True):
    import sys

    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    if withMicro:
        return f"{version}.{sys.version_info.micro}"
    return version


def getSystemPlatform():
    from sys import platform

    return platform
    # if platform == "linux" or platform == "linux2":
    #     # linux
    # elif platform == "darwin":
    #     # OS X
    # elif platform == "win32":
    #     # Windows...


def commandToStrings(command, skip=["url"]):
    strings = []
    for k, v in command.items():
        if k in skip:
            continue
        if v is None or len(v) == 0:
            strings.append(f"{k}")
        elif k == "channels":
            strings.append(f"{v}")
        else:
            strings.append(f"{k}=={v}")
    return strings
    # return [
    #     f'{k}' if v is None or len(v) == 0 else f'{k}={v}'
    #     for k, v in command.items() if k not in skip
    # ]


def run(args, install):
    if not install:
        print(f"[blue bold]\n\\[Dry Run][/blue bold]\n{' '.join(args)}\n")
    else:
        print(f'[green bold]\n\\[Running][/green bold]\n{" ".join(args)}\n')
        subprocess.run(args)


def getPlatforms(config):
    # platforms = list(
    #     set(
    #         p["platform"]
    #         for _, versions in config["torch"].items()
    #         for _, packages in versions.items()
    #         for p in packages["platforms"]
    #     )
    # )
    # platforms.sort()

    return list(config.keys())


def availableCudaVersions(config):
    versions = [p for p in getPlatforms(config) if p not in ["cpu", "macOS"]]
    versions.sort()
    return versions
