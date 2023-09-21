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

    subprocess.call([
        'yq',
        '-s',
        f'"{directory}/" + .metadata.annotations."sis.cern/appset"',
        file,
    ])

def git_stage(files):
    subprocess.call(
        ['git', 'add'] + files
    )

def main():
    files = [
        k.parent / RESULT_FILE for k in Path().rglob('kustomization.yml')
    ]

    [ yq(f) for f in files ]

    git_stage(files)

if __name__ == '__main__':
    main()
