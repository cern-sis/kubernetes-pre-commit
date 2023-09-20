#!/usr/bin/env python3

import os
import subprocess
from ruamel.yaml import YAML
from pathlib import Path


RESULT_FILE = '.result.yml'

def update(path):
    file = path / RESULT_FILE

    yaml = YAML(typ='safe')
    yaml.default_flow_style = False
    yaml.explicit_start = True
    yaml.indent(mapping=2, sequence=4, offset=2)

    docs = [ns_prefix(path, doc) for doc in yaml.load_all(file)]
    yaml.dump_all(docs, file)

    return file

def ns_prefix(path, doc):
    (p, e) = os.path.split(path)
    dash = lambda c: '-'.join([p, e, c])

    if 'metadata' in doc:
        if 'namespace' in doc['metadata']:
            current = doc['metadata']['namespace']
            doc['metadata']['namespace'] = dash(current)

    if 'subjects' in doc:
        for subject in doc['subjects']:
            if 'namespace' in subject:
                current = subject['namespace']
                subject['namespace'] = dash(current)

    return doc

def git_stage(files):
    subprocess.call(
        ['git', 'add'] + files
    )

def main():
    directories = [
        k.parent for k in Path().rglob('kustomization.yml')
    ]

    files = [ update(d) for d in directories ]

    git_stage(files)

if __name__ == '__main__':
    main()
