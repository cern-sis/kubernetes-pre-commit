#!/usr/bin/env python3

import subprocess
import os
from pathlib import Path
from itertools import tee, chain

RESULT_FILE = '.result.yml'

def render(path):
    file = path / RESULT_FILE

    with open(file, 'w') as f:
        kustomize = subprocess.run(
            [
                'kustomize',
                'build',
                '--load-restrictor',
                'LoadRestrictionsNone',
                path,
            ],
            universal_newlines=True,
            stdout=f,
        )

    return file

def git_stage(files):
    subprocess.run(
        ['git', 'add'] + files
    )

def main():
    directories = [
        k.parent for k in Path().rglob('kustomization.yml')
    ]

    files = [ render(d) for d in directories ]

    git_stage(files)


if __name__ == '__main__':
    main()
