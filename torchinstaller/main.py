# %%
import argparse
import subprocess
import re

TORCH_COMMANDS = {
    "1.13.1": {
        "11.6": {"torch": None, "torchvision": None, "torchaudio": None, "url": "https://download.pytorch.org/whl/cu116"},
        "11.7": {"torch": None, "torchvision": None, "torchaudio": None, "url": None},
        "cpu": {"torch": None, "torchvision": None, "torchaudio": None, "url": "https://download.pytorch.org/whl/cpu"},
        "macOS": {"torch": None, "torchvision": None, "torchaudio": None, "url": None}
    },
    "1.12.1": {
        "10.2": {"torch": "1.12.1+cu102", "torchvision": "0.13.1+cu102", "torchaudio": "0.12.1", "url": "https://download.pytorch.org/whl/cu102"},
        "11.3": {"torch": "1.12.1+cu113", "torchvision": "0.13.1+cu113", "torchaudio": "0.12.1", "url": "https://download.pytorch.org/whl/cu113"},
        "11.6": {"torch": "1.12.1+cu116", "torchvision": "0.13.1+cu116", "torchaudio": "0.12.1", "url": "https://download.pytorch.org/whl/cu116"},
        "cpu": {"torch": "1.12.1+cpu", "torchvision": "0.13.1+cpu", "torchaudio": "0.12.1", "url": "https://download.pytorch.org/whl/cpu"},
        "macOS": {"torch": "1.12.1", "torchvision": "0.13.1", "torchaudio": "0.12.1", "url": None}
    },
    "1.12.0": {
        "10.2": {"torch": "1.12.0+cu102", "torchvision": "0.13.0+cu102", "torchaudio": "0.12.0", "url": "https://download.pytorch.org/whl/cu102"},
        "11.3": {"torch": "1.12.0+cu113", "torchvision": "0.13.0+cu113", "torchaudio": "0.12.0", "url": "https://download.pytorch.org/whl/cu113"},
        "11.6": {"torch": "1.12.0+cu116", "torchvision": "0.13.0+cu116", "torchaudio": "0.12.0", "url": "https://download.pytorch.org/whl/cu116"},
        "cpu": {"torch": "1.12.0+cpu", "torchvision": "0.13.0+cpu", "torchaudio": "0.12.0", "url": "https://download.pytorch.org/whl/cpu"},
        "macOS": {"torch": "1.12.0", "torchvision": "0.13.0", "torchaudio": "0.12.0", "url": None}
    },
    "1.11.0": {
        "10.2": {"torch": "1.11.0+cu102", "torchvision": "0.12.0+cu102", "torchaudio": "0.11.0", "url": "https://download.pytorch.org/whl/cu102"},
        "11.3": {"torch": "1.11.0+cu113", "torchvision": "0.12.0+cu113", "torchaudio": "0.11.0", "url": "https://download.pytorch.org/whl/cu113"},
        "cpu": {"torch": "1.11.0+cpu", "torchvision": "0.12.0+cpu", "torchaudio": "0.11.0", "url": "https://download.pytorch.org/whl/cpu"},
        "macOS": {"torch": "1.11.0", "torchvision": "0.12.0", "torchaudio": "0.11.0", "url": None}
    },
}


PYG_COMMANDS = {
    "1.12.*": {
        "10.2": {
            "pyg-lib": None, "torch-scatter": None, "torch-sparse": None, "torch-cluster": None, "torch-spline-conv": None, "torch-geometric": None,
            "url": "https://data.pyg.org/whl/torch-1.12.0+cu102.html"},
        "11.3": {
            "pyg-lib": None, "torch-scatter": None, "torch-sparse": None, "torch-cluster": None, "torch-spline-conv": None, "torch-geometric": None,
            "url": "https://data.pyg.org/whl/torch-1.12.0+cu113.html"
        },
        "11.6": {
            "pyg-lib": None, "torch-scatter": None, "torch-sparse": None, "torch-cluster": None, "torch-spline-conv": None, "torch-geometric": None,
            "url": "https://data.pyg.org/whl/torch-1.12.0+cu116.html"
        },
        "cpu": {
            "pyg-lib": None, "torch-scatter": None, "torch-sparse": None, "torch-cluster": None, "torch-spline-conv": None, "torch-geometric": None,
            "url": "https://data.pyg.org/whl/torch-1.12.0+cpu.html"
        }
    },
    "1.13.*": {
        "11.6": {
            "pyg-lib": None, "torch-scatter": None, "torch-sparse": None, "torch-cluster": None, "torch-spline-conv": None, "torch-geometric": None,
            "url": "https://data.pyg.org/whl/torch-1.13.0+cu116.html"
        },
        "11.7": {
            "pyg-lib": None, "torch-scatter": None, "torch-sparse": None, "torch-cluster": None, "torch-spline-conv": None, "torch-geometric": None,
            "url": "https://data.pyg.org/whl/torch-1.13.0+cu117.html"
        },
        "cpu": {
            "pyg-lib": None, "torch-scatter": None, "torch-sparse": None, "torch-cluster": None, "torch-spline-conv": None, "torch-geometric": None,
            "url": "https://data.pyg.org/whl/torch-1.13.0+cpu.html"
        }
    }
}


def commandToLookup(commands):
    lookup = {}
    for pv, v in commands.items():
        for cv, command in v.items():
            if cv not in lookup.keys():
                lookup[cv] = []
            lookup[cv].append((pv, command))
            lookup[cv].sort(key=lambda v: v[0])
    return lookup


CUDA_LOOKUP = commandToLookup(TORCH_COMMANDS)
PYG_LOOKUP = commandToLookup(PYG_COMMANDS)


def latestValidVersion(cudaVersion):
    goodVersions = list(filter(lambda x: x <= cudaVersion, CUDA_LOOKUP.keys()))
    goodVersions.sort()
    return goodVersions[-1]


def hasCommand(name):
    """
    Check whether `name` is in PATH and is executable 
    """
    from shutil import which
    return which(name) is not None


def getCudaVersion():
    if hasCommand('nvidia-smi'):
        result = subprocess.run(['nvidia-smi'], capture_output=True)
        output = str(result.stdout, encoding='utf-8')
        version = re.search(r'CUDA\s+Version:\s+([\d\.]+)\s+', output)
        try:
            return latestValidVersion(version.group(1))
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


def commandToStrings(command):
    return [
        f'{k}' if v is None else f'{k}=={v}'
        for k, v in command.items() if k != 'url'
    ]


def run(args, dry):
    if dry:
        print(f"[Dry Run]\n{' '.join(args)}")
    else:
        print(f'[Running]\n{" ".join(args)}\n')
        subprocess.run(args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--poetry', '-p',
        action='store_true',
        default=False,
        help='Uses poetry for install. Creates a torch source and adds torch to pyproject.toml'
    )
    parser.add_argument(
        '--dryrun', '-d',
        action='store_true',
        default=False,
        help="just prints the commands that would be run"
    )
    parser.add_argument(
        '--pyg', '-pyg',
        help='Flag to also install pytorch-geometric',
        action='store_true',
        default=False,
    )
    parser.add_argument(
        '--lightning', '-l',
        action='store_true',
        help='Flag to also install pytorch-lightning',
        default=False,
    )

    args = parser.parse_args()

    cudaVersion = getCudaVersion()
    if getPlatform() == 'darwin':
        cudaVersion == 'macOS'

    if cudaVersion in ['macOS', 'cpu']:
        print('CPU ONLY')
    else:
        print(f'Found CUDA: {cudaVersion}')

    # try:
    command = CUDA_LOOKUP[cudaVersion][-1][1]
    url = command['url']
    if args.poetry:
        if url is not None:
            run(['poetry', 'source', 'add', 'torch',
                command['url']], args.dryrun)

        commandArgs = ['poetry', 'add']
        commandArgs.extend(commandToStrings(command))
        if url is not None:
            commandArgs.extend(['--source', 'torch'])

        run(commandArgs, args.dryrun)

        if args.lightning:
            run(['poetry', 'add', 'pytorch-lightning'], args.dryrun)
    else:
        commandArgs = ['pip', 'install']
        commandArgs.extend(commandToStrings(command))

        if command['url'] is not None:
            commandArgs.extend(['--extra-index-url', command['url']])

        run(commandArgs, args.dryrun)

        if args.lightning:
            run(['pip', 'install', 'pytorch-lightning'], args.dryrun)

        if args.pyg:
            pygCommand = PYG_LOOKUP[cudaVersion][-1][1]
            cArgs = ['pip', 'install'] + commandToStrings(pygCommand)
            if pygCommand['url'] is not None:
                cArgs.extend(['-f', pygCommand['url']])
            run(cArgs, args.dryrun)

    # except Exception as err:
    #     print('Install failed')
    #     print(f'{err}')


if __name__ == "__main__":
    main()
