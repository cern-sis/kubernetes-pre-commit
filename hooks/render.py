#!/usr/bin/env python3

import subprocess
import os
from pathlib import Path
from itertools import tee, chain
from multiprocessing import Pool


RESULT_FILE = '.result.yml'

def render(path):
    file = path / RESULT_FILE

    subprocess.run(
        f'''
        kustomize build --load-restrictor LoadRestrictionsNone {path} >{file}
        ''',
        encoding="utf8",
        check=True,
        shell=True,
    )

    return file

def git_stage(files):
    subprocess.run(
        ['git', 'add'] + files,
        encoding="utf8",
        check=True,
    )

def main():
    directories = [
        k.parent for k in Path().rglob('kustomization.yml')
    ]

    dir_count = len(directories)
    pool = Pool(dir_count if dir_count >0 else 1)
    files = pool.map(render, directories)

    git_stage(files)


if __name__ == '__main__':
    main()
