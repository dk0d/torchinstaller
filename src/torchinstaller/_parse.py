# %%
import re
from pathlib import Path
import tomlkit
from rich import print

try:
    from torchinstaller._soup import get_commands

    def sync_commands(name="commands.md", out_suffix=".yaml"):
        src_dir = (Path(__file__).parent / "config").resolve()
        get_commands(src_dir, name=name)
        src_path = src_dir / name
        text = src_path.read_text()

        platforms = set(
            [
                p.group(0).split("/")[-1]
                for p in re.finditer(
                    r"(?:whl/.*)",
                    text,
                )
            ]
        )
        platforms.update(
            [
                p.group(1)
                for p in re.finditer(
                    r"torch==[\d\.]+\+([\w\d\.]+)",
                    text,
                )
            ]
        )

        platforms.add("macos")
        platforms = [p for p in platforms if ".html" not in p]
        platforms.sort()
        # print(platforms)
        #
        currentPlatform = ""
        output = {p: {} for p in platforms}

        for i, line in enumerate(src_path.read_text().splitlines()):
            if len(line) == 0:
                continue
            command = re.search(r"^(\w+) install (.+)", line)
            if command is not None:
                entry: dict = dict(installer=command.group(1), flags=[], packages={})
                try:
                    packages = command.group(2).split(" ")
                    for package in packages:
                        if "==" in package:
                            k, v = package.split("==")
                            vparts = v.split("+")
                            if k in ["torch", "pytorch"]:
                                entry["version"] = vparts[0]
                            if len(vparts) > 1:
                                entry["platform"] = vparts[-1]
                        elif "=" in package:
                            k, v = package.split("=")
                        else:
                            entry["flags"].append(package)
                            continue

                        if "cuda" in k:
                            entry["platform"] = f"cu{v.replace('.', '')}"

                        entry["packages"][k] = v

                    if "cpuonly" in entry["flags"]:
                        entry["platform"] = "cpu"

                    if "platform" not in entry:
                        for p in platforms:
                            if p in line:
                                entry["platform"] = p
                                break

                    if "platform" not in entry and currentPlatform is not None:
                        entry["platform"] = currentPlatform
                        currentPlatform = None

                    if "platform" not in entry:
                        for f in entry["flags"]:
                            p = re.search(r"whl/([\w\d\.]+)", f)
                            if p is not None:
                                entry["platform"] = p.group(1)
                        if "platform" not in entry:
                            entry["platform"] = "cpu"

                    if "version" not in entry:
                        entry["version"] = "latest"

                    if entry["installer"] not in output[entry["platform"]]:
                        output[entry["platform"]][entry["installer"]] = [entry]
                    else:
                        output[entry["platform"]][entry["installer"]].append(entry)

                except Exception as e:
                    print(f"[bold red]Error parsing line ({i}) {line} - {e}")
                    print(e)
                    print(f"{'-' * 80}\n{entry}\n{'-' * 80}")
                    raise e
            else:
                if "macos" in line.lower():
                    currentPlatform = "macos"
                elif "#" not in line:
                    currentPlatform = None

        outPath = (src_path.parent / "commands").with_suffix(out_suffix)

        if outPath.suffix in [".toml"]:
            with outPath.open("w") as fp:
                tomlkit.dump(output, fp)
        else:
            import yaml

            with outPath.open("w") as fp:
                yaml.dump(output, fp, sort_keys=False)

        return output

    # _ = parse_commands()


except ImportError:
    print("Run pip install 'torchinstaller[sync]' for sync feature")
    pass
