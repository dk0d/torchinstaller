# PyTorch Install Helper

Super basic helper to install pytorch stuff without having to check cuda versions and go to websites for the installer URLs.

> _Only Linux and macOS Supported_

Detects what cuda version is available and runs the pip command to install latest pytorch and compatible cuda version

## Installation 

```bash
pip install torchinstaller
```


## Usage

```bash
$ torchinstall -h
usage: torchinstall [-h] [--poetry] [--dryrun] [--pyg] [--lightning]

optional arguments:
  -h, --help       show this help message and exit
  --poetry, -p     Uses poetry for install. Creates a torch source and adds torch to pyproject.toml
  --dryrun, -d     just prints the commands that would be run
  --pyg, -pyg      Flag to also install pytorch-geometric
  --lightning, -l  Flag to also install pytorch-lightning
```

> Note: poetry support is a work in-progress and is unstable


