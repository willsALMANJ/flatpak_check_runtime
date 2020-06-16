#!/usr/bin/env python
"Update flatpak runtime-version in manifest if not the latest version"
# Requires Python >= 3.8 for subprocess.run arguments
import argparse
from distutils.version import LooseVersion
import json
from pathlib import Path
from subprocess import run
import sys

from ruamel.yaml import YAML


yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)


def parse_args():
    "Parse command line arguments"
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", help="Current flatpak manifest")
    return parser.parse_args()


def load_manifest(path):
    "Load manifest file"
    path = Path(path)
    with path.open("r") as file_:
        if path.suffix == ".json":
            manifest = json.load(file_)
        else:
            manifest = yaml.load(file_)

    return manifest


def write_manifest(path, manifest):
    "Write manifest to disk"
    path = Path(path)
    with path.open("w") as file_:
        if path.suffix == ".json":
            json.dump(manifest, file_, indent=4)
        else:
            yaml.dump(manifest, file_)


def get_latest_runtime(runtime_id):
    "Get latest version of runtime"
    columns = ("application", "branch")
    print("runtime_id", runtime_id)
    proc = run(
        ["flatpak", "search", f"--columns={','.join(columns)}", "kde"],
        capture_output=True,
        text=True,
        check=True,
    )
    parsed = [dict(zip(columns, l.split("\t"))) for l in proc.stdout.splitlines()]
    versions = [l["branch"] for l in parsed if l["application"] == runtime_id]
    latest = max(versions, key=LooseVersion)
    return latest


def main():
    "Main logic"
    args = parse_args()

    manifest = load_manifest(args.manifest)

    latest_runtime = get_latest_runtime(manifest["runtime"])

    if latest_runtime != manifest["runtime-version"]:
        manifest["runtime-version"] = latest_runtime
        write_manifest(args.manifest, manifest)


if __name__ == "__main__":
    main()
