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
```bash
$ torchinstall -h
usage: torchinstall [-h] [--pytorch [PYTORCH]] [--pyg] [--pyg-lib-source] 
                      [--compute-platform {cu102,cu113,cu116,cu117,cu118,cu121,rocm4.5.2,rocm5.1.1,rocm5.2,rocm5.4.2,rocm5.6}] 
                      [--lightning] [--use {pip,conda,mamba,poetry}] [-install]

options:
  -h, --help            show this help message and exit
  --pytorch [PYTORCH], -pt [PYTORCH]
                        Flag to install pytorch, can optionally specify a desired version. Must be full semantic version, e.g. 1.13.1, not 1.13, defaults to `latest`
  --pyg, -pyg           Flag to install pytorch-geometric
  --pyg-lib-source, -pyg-src
                        Flag to install PyG from source. i.e. PyG doesn't support wheels for M1/M2 macs. They recommend installing from source
  --compute-platform {cu102,cu113,cu116,cu117,cu118,cu121,rocm4.5.2,rocm5.1.1,rocm5.2,rocm5.4.2,rocm5.6}, -c {cu102,cu113,cu116,cu117,cu118,cu121,rocm4.5.2,rocm5.1.1,rocm5.2,rocm5.4.2,rocm5.6}
                        Manually specify platform version (cuda or rocm) instead ofauto-detect (useful for cluster installations).
  --lightning, -l       Flag to install lightning (lightning.ai)
  --use {pip,conda,mamba,poetry}, -u {pip,conda,mamba,poetry}
                        set command to install with.
  -install, -i          Run installation (default is to dry run commands)
```

> Note: pytorch-geometric can be problematic to install. Installing from source has been added to facilitate installation, but referring to their documentation may be necessary to address errors if they occur.

