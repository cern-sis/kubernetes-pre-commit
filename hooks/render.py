#!/usr/bin/env python3

import os
import shutil
from pathlib import Path
from itertools import tee, chain
from multiprocessing import Pool
from subprocess import Popen, PIPE
import argparse
from contextlib import ExitStack
from functools import partial
import sys


RESULT_FILE = '.result.yml'
RESULT_DIR = '.result'


def render(args, path):
    file = path / RESULT_FILE

    cmds = [
        [
            'kustomize',
            'build',
            '--load-restrictor',
            'LoadRestrictionsNone',
            f'{path}',
        ]
    ]

    if args.update_namespace:
        prefix = f'{path.stem}-'

        cmds.append([
            'yq',
            f'(.metadata | select(has("namespace"))).namespace |= "{prefix}" + .',
        ])
        cmds.append([
            'yq',
            f'(. | select(.kind == "ClusterRoleBinding")).subjects.[].namespace |= "{prefix}" + .',
        ])

    cmds.append([ 'tee', f'{file}' ])

    if args.split_files:
        directory = path / RESULT_DIR

        if directory.exists():
            shutil.rmtree(directory)

        os.makedirs(directory)

        cmds.append([
            'yq',
            '-s',
            f'"{directory}/" + .metadata.annotations."sis.cern/appset"',
        ])


    procs = []
    with ExitStack() as stack:
        for c in cmds:
            # use stdout from the previous process if available
            stdin = procs[-1].stdout if procs else None

            p = stack.enter_context(
                Popen(
                    c,
                    stdin=stdin,
                    stdout=PIPE,
                    stderr=sys.stderr,
                )
            )

            if stdin:
                stdin.close()

            procs.append(p)


def git_stage(args, directories):
    to_stage = [f'{d}/{RESULT_FILE}' for d in directories]

    if args.split_files:
        to_stage += [f'{d}/{RESULT_DIR}' for d in directories]

    Popen(
        [
            'git',
            'add',
        ] + to_stage
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ns', '--update-namespace', action='store_true')
    parser.add_argument('-sp', '--split-files', action='store_true')
    args = parser.parse_args()

    directories = [
        k.parent for k in Path().rglob('kustomization.yml')
    ]

    dir_count = len(directories)

    with Pool(dir_count if dir_count >0 else 1) as pool:
        pool.map(partial(render, args), directories)

    git_stage(args, directories)


if __name__ == '__main__':
    main()
