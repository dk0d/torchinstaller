# %%
from pathlib import Path
from bs4 import BeautifulSoup
import requests
import re
import unmarkd
from rich import print


def get_latest_version(
    url="https://pypi.org/project/torch/",
):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    version = "v2"
    try:
        name = soup.find(class_="package-header__name")
        vers = name.get_text() if name is not None else ""
        vers = re.search(r"torch\s+(\d+\.\d+\.\d+)", vers).group(1)
        vers = f"v{vers}"
        version = vers
    except Exception as e:
        pass
    return version
    # md = unmarkd.unmark(soup.find(id="stable").get_text())
    # print(md)
    # version = re.search(r"Stable\s(v\d\.\d\.\d)", md, re.MULTILINE).group(1)
    # return version


def get_markdown(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return unmarkd.unmark(soup.get_text())


def get_commands(
    out_dir: Path,
    name="commands.md",
    url="https://pytorch.org/get-started/previous-versions",
):
    md = get_markdown(url)
    md = "\n".join([line.strip() for line in md.split("\n") if len(line.strip()) > 0])
    spans = [(versions.group(1), versions.span()) for versions in re.finditer(r"^(v\d\.\d\.\d)", md, re.MULTILINE)]
    latest_version = get_latest_version()
    latest = f"""
# latest ({latest_version})
# macOS
conda install pytorch::pytorch torchvision torchaudio -c pytorch
# Linux
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
conda install pytorch torchvision torchaudio cpuonly -c pytorch
# macOS
pip install torch torchvision torchaudio
# Linux
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"""

    out = latest + "\n"

    print(latest_version)
    for i in range(len(spans)):
        version, span = spans[i]
        if version < "v1.8.2":
            continue
        print(version)
        _, sn = spans[i + 1] if i + 1 < len(spans) else (None, None)
        if sn is None:
            sub = md[span[0] :]
            commandIdx = re.search(
                r"^commands",
                sub,
                re.MULTILINE | re.IGNORECASE,
            )
            sn = commandIdx.span()
            text = sub[: sn[0]]
        else:
            text = md[span[0] : sn[0]]

        cleaned = [line for line in text.split("\n") if len(line) > 0 and line[0] not in ["#", "*", "\\"]]
        cleaned = [line for line in cleaned if line not in ["Conda", "Wheel"]]
        for i in range(len(cleaned)):
            if "OSX" in cleaned[i]:
                cleaned[i] = cleaned[i].replace("OSX", "macOS")

            if "Linux" in cleaned[i]:
                cleaned[i] = "Linux"

            if cleaned[i] in ["macOS", "Linux", "Linux and Windows"]:
                cleaned[i] = f"## {cleaned[i]}"

        cleaned[0] = f"# {cleaned[0]}"
        spec = "\n".join(cleaned)
        out += spec + "\n"

    (out_dir / name).write_text(re.sub(r"\\", "", out))
