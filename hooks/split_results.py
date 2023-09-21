#!/usr/bin/env python3

import os
import subprocess
import shutil
from pathlib import Path


RESULT_FILE = '.result.yml'
OUTPUT_DIR = '.result'

def yq(file):
    directory = file.parent / OUTPUT_DIR

    if directory.exists():
        shutil.rmtree(directory)

    os.makedirs(directory)

    subprocess.run(
        [
            'yq',
            '-s',
            f'"{directory}/" + .metadata.annotations."sis.cern/appset"',
            file,
        ],
        encoding="utf8",
        check=True,
    )

def git_stage(files):
    subprocess.run(
        ['git', 'add'] + files,
        encoding="utf8",
        check=True,
    )

def main():
    files = [
        k.parent / RESULT_FILE for k in Path().rglob('kustomization.yml')
    ]

    [ yq(f) for f in files ]

    git_stage(files)

if __name__ == '__main__':
    main()
