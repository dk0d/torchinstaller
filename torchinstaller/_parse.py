# %%
import re
from pathlib import Path
import tomlkit


def parse_commands(name="commands.md"):
    src_dir = Path("./torchinstaller/config").resolve()
    if not src_dir.exists():
        src_dir = Path("./config").resolve()

    src_path = src_dir / name

    platforms = set(
        [
            p.group(1)
            for p in re.finditer(r"(?:\+|whl/)([\d\w\.]+)", src_path.read_text())
        ]
    )
    platforms.add("macOS")
    platforms = [p for p in platforms if ".html" not in p]
    platforms.sort()

    currentPlatform = ""
    output = {p: {} for p in platforms}

    for _, line in enumerate(src_path.read_text().splitlines()):
        if len(line) == 0:
            continue
        command = re.search(r"^(\w+) install (.+)", line)
        if command is not None:
            entry = dict(installer=command.group(1), flags=[], packages={})
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

            if "version" not in entry:
                entry["version"] = "latest"

            if entry["installer"] not in output[entry["platform"]]:
                output[entry["platform"]][entry["installer"]] = [entry]
            else:
                output[entry["platform"]][entry["installer"]].append(entry)
        else:
            if "macos" in line.lower():
                currentPlatform = "macOS"
            elif "#" not in line:
                currentPlatform = None

    outDir = src_path.parent / "commands.toml"

    with outDir.open("w") as fp:
        tomlkit.dump(output, fp)

    return output


_ = parse_commands()


# %%
