import click
import glob
import os
import json

def map_dirs(repo: str):
    dirs = glob.glob(f'{repo}/*')

    dir_mappings = {}

    for d in dirs:
        if (not os.path.isdir(d)) or d.split('/')[1].startswith('_'):
            continue

        if not os.path.isfile(f'{d}/000_context.jsonld'):
            continue
        try:
            with open(f'{d}/000_context.jsonld') as f:
                refs = json.load(f)
        except Exception as err:
            print(f'Facet without data descriptor: {d}')
            continue

        mapping = refs['@context']['@base'].split('/')[-2]
        dir_mappings[mapping] = d
    
    return dir_mappings

def diffs(key: str, mapping1: dict, mapping2: dict, check_only: str = None):

    path1 = mapping1[key]
    files1 = [f for f in glob.glob(f'{path1}/*.json')]

    ids1 = []
    for f in files1:
        with open(f) as g:
            refs = json.load(g)
        ids1.append(refs['id'])
    
    path2 = mapping2[key]
    files2 = [f for f in glob.glob(f'{path2}/*.json')]

    ids2 = []
    for f in files2:
        with open(f) as g:
            refs = json.load(g)
        ids2.append(refs['id'])

    only_in_1 = [f for f in ids1 if f not in ids2]
    only_in_2 = [f for f in ids2 if f not in ids1]

    return only_in_1, only_in_2

def run_migrate(facets, pathA, pathB):
    """
    Copy facets from repoA to repoB
    """

    for f in facets:
        os.system(f'cp {pathA}/{f}.json {pathB}/{f}.json')

@click.command
@click.argument('repo1')
@click.argument('repo2')
@click.option('--check_only', type=str)
@click.option('--migrate', type=str)
def main(repo1: str, repo2: str, check_only: str = None, migrate: str = None):
    dir_mappings1 = map_dirs(repo1)
    dir_mappings2 = map_dirs(repo2)

    if migrate:
        migrate = migrate.split(',')
    else:
        migrate = []

    only_in_1, only_in_2 = None, None
    if check_only != '2':
        only_in_1 = [k for k in dir_mappings1.keys() if k not in dir_mappings2]
    if check_only != '1':
        only_in_2 = [k for k in dir_mappings2.keys() if k not in dir_mappings1]
    common = [k for k in dir_mappings1.keys() if k in dir_mappings2] + [k for k in dir_mappings2.keys() if k in dir_mappings1]
    common = set(common)

    if only_in_1:
        print(f'Only in {repo1}:')
        for k in only_in_1:
            print(f'- {k}')

    if only_in_2:
        print(f'Only in {repo2}:')
        for k in only_in_2:
            print(f'- {k}')

    print(f'Checking: {", ".join(common)}')


    print('Term differences:')
    for key in common:
        only_1, only_2 = diffs(key, dir_mappings1, dir_mappings2)
        if (only_1 and check_only == '1') or (only_2 and check_only == '2') or ((only_1 or only_2) and check_only is None):
            print()
            print(f'{key}:')

        if check_only != '2' and only_1:
            print(f'Only in {repo1}:')
            print(', '.join(only_1))
            if key in migrate:

                path1 = dir_mappings1[key]
                path2 = dir_mappings2[key]
                run_migrate(only_1, path1, path2)

        if check_only != '1' and only_2:
            print(f'Only in {repo2}:')
            print(', '.join(only_2))
            if key in migrate:

                path1 = dir_mappings1[key]
                path2 = dir_mappings2[key]
                run_migrate(only_2, path2, path1)


if __name__ == '__main__':
    main()
    

