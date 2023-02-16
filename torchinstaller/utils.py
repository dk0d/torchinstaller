from pathlib import Path
import tomlkit
import subprocess
import re


def commandToLookup(commands):
    lookup = {}
    for pv, v in commands.items():
        if pv == 'keys_':
            continue
        for cv, command in v.items():
            if cv not in lookup.keys():
                lookup[cv] = []
            lookup[cv].append((pv, command))
            lookup[cv].sort(key=lambda v: v[0])
    return lookup


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
        with path.open('r') as fp:
            cfg = tomlkit.load(fp)
            # print(cfg)
        return cfg
    except Exception as e:
        print('Commands configuration not found, package installation error')
        exit(1)


def latestValidVersion(cudaVersion, cudaLookup):
    goodVersions = list(filter(lambda x: x <= cudaVersion, cudaLookup.keys()))
    goodVersions.sort()
    return goodVersions[-1]


def hasCommand(name):
    """
    Check whether `name` is in PATH and is executable 
    """
    from shutil import which
    return which(name) is not None


def getCudaVersion(cudaLookup):
    if hasCommand('nvidia-smi'):
        result = subprocess.run(['nvidia-smi'], capture_output=True)
        output = str(result.stdout, encoding='utf-8')
        version = re.search(r'CUDA\s+Version:\s+([\d\.]+)\s+', output)
        try:
            return latestValidVersion(version.group(1), cudaLookup), version.group(1)
        except:
            pass
    return 'cpu', None


def pythonVersion(withMicro=True):
    import sys
    version = f'{sys.version_info.major}.{sys.version_info.minor}'
    if withMicro:
        return f'{version}.{sys.version_info.micro}'
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


def commandToStrings(command, skip=['url']):
    strings = []
    for k, v in command.items():
        if k in skip:
            continue
        if v is None or len(v) == 0:
            strings.append(f'{k}')
        elif k == 'channels':
            strings.append(f"{v}")
        else:
            strings.append(f'{k}=={v}')
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


def cudaVersions(config):
    versions = list(set(
        ck
        for command in config['commands']
        if command in config['torch']
        for k, v in config['torch'][command].items()
        if k not in ['keys_']
        for ck, _ in v.items()
        if ck not in ['cpu', 'macOS']
    ))
    versions.sort()
    return versions
