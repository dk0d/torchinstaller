from pathlib import Path
import argparse
import subprocess
import re
import tomlkit
from .utils import *


def main():
    configPath = Path(__file__).parent / 'config' / 'commands.toml'
    config = loadConfig(configPath)
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
    # parser.add_argument(
    #     '--install', '-i',
    #     help='run install commands'
    # )
    parser.add_argument(
        '--pyg', '-pyg',
        help='Flag to also install pytorch-geometric',
        action='store_true',
        default=False,
    )
    parser.add_argument(
        '--cuda', '-c',
        type=str,
        default=None,
        choices=cudaVersions(config),
        help="Manually specify cuda version instead of auto-detect (useful for cluster installations)."
    )
    parser.add_argument(
        '--lightning', '-l',
        action='store_true',
        help='Flag to also install pytorch-lightning',
        default=False,
    )

    torchCudaLookup = commandToLookup(config['torch']['commands'])
    pygLookup = commandToLookup(config['pygeo']['commands'])

    try:
        args = parser.parse_args()
    except Exception as e:
        print(f'Install Failed: {e}')

    pyVersion = pythonVersion()

    if args.cuda is None:
        cudaVersion = getCudaVersion(torchCudaLookup)
        print(f'Found CUDA: {cudaVersion}')
    else:
        cudaVersion = args.cuda
        print(f'User specified CUDA: {cudaVersion}')

    if getPlatform() == 'darwin':
        cudaVersion == 'macOS'

    if cudaVersion in ['macOS', 'cpu']:
        print('CPU ONLY')

    try:
        command = torchCudaLookup[cudaVersion][-1][1]
        url = command['url']
        if args.poetry:
            if url is not None:
                run(['poetry', 'source', 'add', 'torch',
                    command['url']], args.dryrun)

            commandArgs = ['poetry', 'add']
            commandArgs.extend(commandToStrings(
                config['torch']['keys_'], command))
            if url is not None:
                commandArgs.extend(['--source', 'torch'])

            run(commandArgs, args.dryrun)

            if args.lightning:
                run(['poetry', 'add', 'pytorch-lightning'], args.dryrun)
        else:
            commandArgs = ['pip', 'install']
            commandArgs.extend(commandToStrings(
                config['torch']['keys_'], command))

            if command['url'] is not None:
                commandArgs.extend(['--extra-index-url', command['url']])

            run(commandArgs, args.dryrun)

            if args.lightning:
                run(['pip', 'install', 'pytorch-lightning'], args.dryrun)

            if args.pyg:
                pygCommand = pygLookup[cudaVersion][-1][1]
                cArgs = ['pip', 'install'] + \
                    commandToStrings(config['pygeo']['keys_'], pygCommand)
                if pygCommand['url'] is not None:
                    cArgs.extend(['-f', pygCommand['url']])
                run(cArgs, args.dryrun)

    except Exception as err:
        print('Install failed')
        print(f'{err}')


if __name__ == "__main__":
    main()
