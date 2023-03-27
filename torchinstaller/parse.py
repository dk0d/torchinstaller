#%%
import re
from pathlib import Path
import tomlkit


def parse_commands(src_path=Path("./torchinstaller/config/torch-commands.md").resolve()):

    if not src_path.exists():
        src_path = Path("./config/torch-commands.md").resolve()
    print(src_path)

    platforms = set([p.group(1) for p in re.finditer(r"\+([\d\w\.]+)", src_path.read_text())])
    platforms.add("macOS")
    platforms = list(platforms)
    platforms.sort()

    currentPlatform = ""
    output = {p: {} for p in platforms}

    for _, line in enumerate(src_path.read_text().splitlines()):
        if len(line) == 0:
            continue
        command = re.search(r"^(\w+) install (.+)", line)
        if command is not None:
            entry = dict(installer=command.group(1), flags=[], packages = {})
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

                if entry.get("platform", None) is None and currentPlatform is not None:
                    entry["platform"] = currentPlatform
                    currentPlatform = None

                entry['packages'][k] = v

            if "cpuonly" in entry["flags"]:
                entry["platform"] = "cpu"

            if "platform" not in entry:
                for p in platforms:
                    if p in line:
                        entry["platform"] = p
                        break

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


parse_commands()
# %%
