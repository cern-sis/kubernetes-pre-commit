#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path


RESULT_FILE = '.result.yml'

def yq(file):
    (p, e) = os.path.split(file.parent)
    prefix = f'{p}-{e}-'

    subprocess.run(
        [
            'yq',
            '-i',
            f'(.metadata | select(has("namespace")).namespace) |= "{prefix}" + .',
            file,
        ],
        encoding="utf8",
        check=True,
    )
    subprocess.call(
        [
            'yq',
            '-i',
            f'(. | select(.kind == "ClusterRoleBinding").subjects.[].namespace) |= "{prefix}" + .',
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
