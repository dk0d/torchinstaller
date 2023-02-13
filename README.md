# PyTorch Install Helper

Super simple helper to install pytorch stuff without having to check cuda versions and go to websites for the installer URLs.
Installs based on requested or detected CUDA version, doesn't check python versions.

> _Only Linux and macOS Supported_

Detects what cuda version is available and runs the pip command to install latest pytorch and compatible cuda version

## Installation

```bash
pip install torchinstaller
```

## Usage

```bash
$ torchinstall -h
usage: torchinstall [-h] [--pyg] [--cuda {10.2,11.3,11.6,11.7}] [--lightning] [--use {pip,conda,mamba,poetry}] [-install]

optional arguments:
  -h, --help            show this help message and exit
  --pyg, -pyg           Flag to also install pytorch-geometric
  --cuda {10.2,11.3,11.6,11.7}, -c {10.2,11.3,11.6,11.7}
                        Manually specify cuda version instead of auto-detect (useful for cluster installations).
  --lightning, -l       Flag to also install pytorch-lightning
  --use {pip,conda,mamba,poetry}, -use {pip,conda,mamba,poetry}
                        set command to install with
  -install, -i          Run installation (default is to dry run commands)
```

> Note: poetry support is a work in-progress and is unstable
