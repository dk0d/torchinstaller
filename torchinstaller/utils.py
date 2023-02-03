from pathlib import Path
import tomlkit
import subprocess
import re


def commandToLookup(commands):
    lookup = {}
    for pv, v in commands.items():
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
            return latestValidVersion(version.group(1), cudaLookup)
        except:
            pass
    return 'cpu'


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


def commandToStrings(keys, command):
    kvs = {k: command.get(k, None) for k in keys if k != 'url'}
    return [
        f'{k}' if v is None else f'{k}=={v}'
        for k, v in kvs.items()
    ]


def run(args, dry):
    if dry:
        print(f"[Dry Run]\n{' '.join(args)}")
    else:
        print(f'[Running]\n{" ".join(args)}\n')
        subprocess.run(args)


def cudaVersions(config):
    versions = list(set(
        ck
        for k, v in config['torch']['commands'].items()
        for ck, _ in v.items()
        if ck not in ['cpu', 'macOS']
    ))
    versions.sort()
    return versions
