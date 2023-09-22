#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path
from multiprocessing import Pool


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
    subprocess.run(
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

    files_count = len(files)
    pool = Pool(files_count if files_count >0 else 1)
    pool.map(yq, files)

    git_stage(files)

if __name__ == '__main__':
    main()
