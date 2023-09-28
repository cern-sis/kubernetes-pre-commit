#!/usr/bin/env python3

import os
import shutil
import shlex
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
SPLIT_ON = 'sis.cern/base'


def render(args, path):
    file = path / RESULT_FILE
    directory = path / RESULT_DIR

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
        (project, environment) = path.parts[-2:]
        if project == environment:
            prefix = project
        else:
            prefix = f'{project}-{environment}'

        cmds.append([
            'yq',
            'ea',
            f'( .metadata | select(has("namespace") and .namespace != "{prefix}")).namespace |= "{prefix}-" + . | (.metadata | select(has("namespace") and .namespace == "{project}")).namespace |= . + "-{environment}"',
            '-',
        ])
        cmds.append([
            'yq',
            'ea',
            f'(. | select( .kind == "ClusterRoleBinding" and .subjects.[].namespace != "{prefix}")).subjects.[].namespace |= "{prefix}-" + . | ( . | select( .kind == "ClusterRoleBinding" and .subjects.[].namespace == "{project}")).subjects.[].namespace |= . + "-{environment}"',
            '-',
        ])

    cmds.append([ 'tee', f'{file}' ])

    if args.split_files:
        if not directory.exists():
            os.makedirs(directory)

        [f.unlink() for f in directory.rglob("*")]

        ## Splitting yaml document into files where each reasulting files
        ## contains multiple documents is only doable in two passes.
        ## https://github.com/mikefarah/yq/discussions/1799
        cmds.append([
            'yq',
            'ea',
            f'[.] | group_by(.metadata.annotations."{SPLIT_ON}") | .[] | split_doc',
            '-s',
            f'"{directory}/" + .[0].metadata.annotations."{SPLIT_ON}" // "missing-annotation"',
            '-',
        ])

    previous = None
    for i, c in enumerate(cmds):
        # use stdout from the previous process if available
        stdin = previous.stdout if previous else None
        stdout = PIPE if i < len(cmds) else None

        previous = Popen(
            c,
            stdin=stdin,
            stdout=stdout,
            stderr=sys.stderr,
        )

        if stdin:
            stdin.close()

    previous.communicate()

    if args.split_files:
        ## Second pass of the split
        Popen(
            f'find {directory}/*.yml -exec yq ".[] | split_doc" -i {{}} \;',
            shell=True,
            stderr=sys.stderr,
        ).communicate()


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
    parser.add_argument('changes', nargs='*')

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
