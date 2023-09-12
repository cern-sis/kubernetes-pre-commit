#!/usr/bin/env python3

import subprocess
import os
import ruamel.yaml
import shutil
from multiprocessing import Pool
from pathlib import Path
from itertools import tee, chain


def build(path):
    kustomize = subprocess.Popen(
        [
            'kustomize',
            'build',
            '--load-restrictor',
            'LoadRestrictionsNone',
            path,
        ],
        stdout=subprocess.PIPE,
        universal_newlines=True,
        bufsize=0,
    )


    result_dir = path / '.result'
    shutil.rmtree(result_dir,  ignore_errors=True)

    yaml = ruamel.yaml.YAML()
    yaml.explicit_start = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.default_flow_style = False
    yaml.width = 100000

    ## Make a copy of the generator
    documents1, documents2 = tee(yaml.load_all(kustomize.stdout))

    ##
    ## Dump all resources in one file .result.yml
    ## To easily kubectl apply
    ##
    result_file = path / '.result.yml'
    with open(result_file, 'w') as file:
        yaml.dump_all(documents1, file)


    count = 0
    ##
    ## Dump each resources separatly in .result/
    ##
    for doc in documents2:
        kind = doc['kind'].lower()
        name = doc['metadata']['name']
        namespace = doc['metadata'].get('namespace', 'default')

        file_path = (result_dir / namespace / kind / name).with_suffix('.yml')
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as file:
            yaml.dump(doc, file)
            count += 1

    print(f"Rendering {path}: {count} resources generated.", flush=True)
    return [result_dir, result_file]


def main():
    directories = [
        k.parent for k in Path().rglob('kustomization.yml')
    ]

    with Pool() as pool:
        results = pool.map(build, directories)
        subprocess.call(['git', 'add'] + list(chain.from_iterable(results)))


if __name__ == "__main__":
    main()
