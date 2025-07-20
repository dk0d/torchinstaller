from enum import Enum
from pathlib import Path
from typing import Annotated
from rich import print
from typer import Typer
import typer

from torchinstaller.utils import (
    GetCommandError,
    loadConfig,
    availableCudaVersions,
    getPythonVersion,
    getSystemPlatform,
    getCudaVersion,
    getCommandForPlatform,
    handlePyGCommand,
    handleTorchCommand,
    handleLightningCommand,
)


class PackageManager(str, Enum):
    pip = "pip"
    conda = "conda"
    mamba = "mamba"


app = Typer()
state = {"configPath": Path(__file__).parent / "config" / "commands.yaml", "config": None}


def parse_platform(value: str) -> str:
    cfg = loadConfig(state["configPath"])
    platforms = availableCudaVersions(cfg)
    if value not in platforms:
        raise typer.BadParameter(f"Invalid platform '{value}', must be one of: {', '.join(platforms)}")
    return value


@app.callback()
def shared():
    state["config"] = loadConfig(state["configPath"])


@app.command()
def platforms():
    """List available compute platforms"""
    cfg = loadConfig(state["configPath"])
    platforms = availableCudaVersions(cfg)
    print("[bold green]Available Compute Platforms:")
    for p in platforms:
        print(f" - [blue]{p}")


@app.command()
def install(
    pytorch: Annotated[
        str,
        typer.Option(
            "--pytorch",
            "-pt",
            help=(
                "Flag to install pytorch, can optionally specify a desired version."
                " Must be full semantic version, e.g. 1.13.1, not 1.13, defaults to `latest`"
            ),
        ),
    ] = "latest",
    pyg: Annotated[
        bool,
        typer.Option(
            "--pyg",
            "-pyg",
            help="Flag to install pytorch-geometric",
        ),
    ] = False,
    pyg_lib_source: Annotated[
        bool,
        typer.Option(
            "--pyg-lib-source",
            "-pyg-src",
            help=(
                "Flag to install PyG from source. i.e. PyG doesn't support wheels for M1/M2 macs."
                " They recommend installing from source"
            ),
        ),
    ] = False,
    lightning: Annotated[
        bool,
        typer.Option(
            "--lightning",
            "-l",
            help="Flag to install lightning (lightning.ai)",
        ),
    ] = False,
    compute_platform: Annotated[
        str | None,
        typer.Option(
            "--compute-platform",
            "-c",
            help=(
                "Manually specify platform version (cuda or rocm) instead of auto-detect (useful for cluster installations)."
            ),
            parser=parse_platform,
        ),
    ] = None,
    use: Annotated[
        PackageManager,
        typer.Option(
            "--use",
            "-u",
            help="set command to install with.",
            case_sensitive=False,
            show_default=True,
            # rich_help_panel="Installer Options",
            # rich_extras=["choices"],
        ),
    ] = PackageManager.pip,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            "-d",
            help="Dry run installation commands (default is to install)",
            show_default=True,
            is_flag=True,
        ),
    ] = False,
):
    """Install PyTorch and related libraries"""

    installer = use.value

    if installer in ["conda", "mamba"]:
        command_key = "conda"
    elif installer in ["pip", "poetry"]:
        command_key = "pip"
    else:
        raise NotImplementedError("Unsupported installer")

    config = state["config"]

    getPythonVersion()
    system_platform = getSystemPlatform()

    platform, detected = getCudaVersion(availableCudaVersions(config))

    print("-" * 20)
    if system_platform == "darwin":
        detected = "macos"

    if compute_platform is None:
        print(f"System platform: [blue bold]{detected}[/blue bold]\nUsing platform: [red bold]{platform}")
        platform = detected
    else:
        platform = compute_platform
        print(f"User specified platform: [yellow bold]{platform}")
        print(f"System platform: [blue bold]{detected}[/blue bold]\nUsing platform: [blue bold]{platform}")

    if platform in ["cpu"]:
        print("[yellow bold]CPU ONLY")
    elif platform in ["macos"]:
        print("\n[yellow bold]macOS (pytorch 2.0 supports apple silicon)\n")

    print("-" * 20)

    try:
        if pytorch is not None:
            command = getCommandForPlatform(config, command_key, pytorch, platform)
            handleTorchCommand(installer, command, dry_run)

        if lightning:
            handleLightningCommand(installer, dry_run)

        if pyg:
            handlePyGCommand(installer, pytorch, platform, pyg_lib_source, dry_run)

        if not any([pytorch, lightning, pyg]):
            print("[red bold]NO COMMANDS Selected")
            print("[green bold]Run torchinstall -h to see flags for installing")

    except GetCommandError as err:
        print("Unable to derive command\n")
        print(f"{err}")
    except Exception as err:
        print("Install failed")
        print(f"{err}")


@app.command()
def sync():
    """Update installation commands by parsing the pytorch website"""
    try:
        from torchinstaller._parse import sync_commands
    except ImportError:
        return

    print("[bold red]Syncing commands")
    sync_commands()

    _ = loadConfig(state["configPath"])
    print("[bold green]Sync complete")


def main():
    app()


if __name__ == "__main__":
    main()
