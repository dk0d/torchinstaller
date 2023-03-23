from pathlib import Path
import tomlkit
import subprocess
import re


def getCommandForPlatform(package_spec, platform):
    command = {}
    versions = list(package_spec.keys())
    versions.sort(reverse=True)
    for version in versions:
        for entry in package_spec[version]["platforms"]:
            if entry["platform"].startswith(platform):
                command.update(
                    **{
                        c: v
                        for c, v in package_spec[version].items()
                        if c != "platforms"
                    }
                )
                command.update(**{k: v for k, v in entry.items() if k != "platform"})
                return command
    raise Exception(f"platform not found: {platform}")


def remove_none(d):
    keys = list(d.keys())
    for k in keys:
        if isinstance(d[k], dict):
            remove_none(d[k])
        elif d[k] is None:
            d.pop(k)
    return d


def loadConfig(path: Path):
    try:
        with path.open("r") as fp:
            cfg = tomlkit.load(fp)
            # print(cfg)
        return cfg
    except Exception:
        print("Commands configuration not found, package installation error")
        exit(1)


def closestLatestVersion(cudaVersion, availableVersions):
    goodVersions = list(filter(lambda x: x >= cudaVersion, availableVersions.keys()))
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
        version = re.search(r"CUDA\s+Version:\s+([\d\.]+)\s+", output)
        try:
            return closestLatestVersion(
                version.group(1), availableVersions
            ), version.group(1)
        except:
            pass
    return "cpu", None


def pythonVersion(withMicro=True):
    import sys

    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    if withMicro:
        return f"{version}.{sys.version_info.micro}"
    return version


def getPlatform():
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
        print(f"[Dry Run]\n{' '.join(args)}")
    else:
        print(f'[Running]\n{" ".join(args)}\n')
        subprocess.run(args)


def getPlatforms(config):
    platforms = list(
        set(
            p["platform"]
            for _, versions in config["torch"].items()
            for _, packages in versions.items()
            for p in packages["platforms"]
        )
    )
    platforms.sort()
    return platforms


def availableCudaVersions(config):
    versions = [p for p in getPlatforms(config) if p not in ["cpu", "macOS"]]
    versions.sort()
    return versions
