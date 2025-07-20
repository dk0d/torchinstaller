<p align="center"><div align="center" style="display": none;>
  
<p align="center">
<img alt='icon' width="150" = src="https://github.com/dk0d/torchinstaller/raw/main/assets/torchinstaller_icon.png"/>
</p>
  
# `torchinstaller`

<h3 align="center">Installing PyTorch has never been easier</h3>

</div></p>

<p align="center">

<a href="https://pypi.org/project/torchinstaller/">
  <img alt="PYPI Version" src="https://img.shields.io/pypi/v/torchinstaller?color=blue">
</a>

<a href="https://github.com/dk0d/torchinstaller/blob/main/LICENSE">
  <img alt="Licence" src="https://img.shields.io/pypi/l/torchinstaller">
</a>

</p>

`torchinstaller` is a super simple helper to install PyTorch stuff without having to check cuda versions and go to websites for the installer URLs.
It installs PyTorch components based on requested or detected CUDA version, and doesn't check python versions.

> **_Only Linux and macOS supported_**

It detects what cuda version is available and runs the pip command to install latest PyTorch and compatible cuda version

## Installation

```bash
pip install torchinstaller
```

## Usage

```bash
$ torchinstall --help

 Usage: torchinstall [OPTIONS] COMMAND [ARGS]...

╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                            │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.     │
│ --help                        Show this message and exit.                                                          │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ platforms        List available compute platforms                                                                  │
│ install          Install PyTorch and related libraries                                                             │
│ sync             Update installation commands by parsing the pytorch website                                       │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

List the platforms that have been synced via `torchinstall sync`
```bash
$ torchinstall platforms
Available Compute Platforms:
 - cu102
 - cu111
 - cu113
 - cu116
 - cu117
 - cu118
 - cu121
 - cu124
 - cu126
 - cu128
 - rocm4.0.1
 - rocm4.1
 - rocm4.2
 - rocm4.5.2
 - rocm5.1.1
 - rocm5.2
 - rocm5.4.2
 - rocm5.6
 - rocm5.7
 - rocm6.0
 - rocm6.1
 - rocm6.2
 - rocm6.2.4
 - rocm6.3
```

> Note: `pytorch-geometric` can be problematic to install. Installing from source has been added to facilitate installation, but referring to their documentation may be necessary to address errors if they occur.
