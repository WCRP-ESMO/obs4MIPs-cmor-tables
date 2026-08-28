"""
Script to sync changes from obs4MIPs_CVs or obs4MIPs-cmor-tables repos

Can handle changes from both directions. If merging changes from both are required, please perform one sync then the other.
"""

import glob
import os
import json
import click

# The following are attributes that carry across to the CVs repo from the cmor-tables
CV_ATTRIBUTES = [
    'aux_uncertainty_id',
    'conventions',
    'data_specs_version',
    'frequency',
    'grid_label', # WCRP-universe: grid
    'has_aux_unc',
    'institution_id', # WCRP-universe: institution
    'nominal_resolution', # WCRP-universe: resolution
    'product',
    'realm',
    'region',
    'source_id',
    'source_type',
    'site_id',
    'site_location' # Missing from cmor-tables 14/07/2026
]

# Not included
# - required_global_attributes
# - table_id
# - license

def cmor_to_cv(label: str = 'obs4MIPs', facets: list = None, remote: bool = False, dryrun: bool = False):
    """
    Takes all obs4MIPs/obs4REF files and maps values to the CV repo

    obs4MIPs_<facet>.json -> CVs/<facet>/<value>.json
    """

    print('Migrating changes from cmor-tables to CV repo:')

    if remote:
        raise NotImplementedError
    
    if not facets:
        facets = CV_ATTRIBUTES

    for facet in facets:
        if not os.path.isfile(f'{label}-cmor-tables/{label}_{facet}.json'):
            print(f' - "{facet}" missing from cmor_tables - skipped')
            continue

        if not os.path.isfile(f'{label}_CVs/{facet}/000_context.jsonld'):
            print(f' - "{facet}" requires creation of new data descriptor in CV - skipped')
            continue
        
        with open(f'{label}-cmor-tables/{label}_{facet}.json') as f:
            refs = json.load(f)[facet]

        if isinstance(refs, list):
            refs = {k:None for k in refs}
        
        for v, desc in refs.items():

            vid = v.lower().replace(' ','-')
            content = {
                "@context": "000_context.jsonld",
                "id": vid,
                "type": facet,
                "drs_name": v
            }
            
            # Do not update the content if the file already exists
            updated_keys = True
            if os.path.isfile(f'{label}_CVs/{facet}/{vid}.json'):
                with open(f'{label}_CVs/{facet}/{vid}.json') as f:
                    old_content = json.load(f)
                
                updated_keys = [k for k in content.keys() if content[k] != old_content.get(k)]
                if updated_keys:
                    old_content.update(content)

                    print(f' > Updating file: {label}_CVs/{facet}/{vid}.json')
            else:
                print(f' > Creating file: {label}_CVs/{facet}/{vid}.json')


            if isinstance(desc, str):
                content['description'] = desc
            elif isinstance(desc, dict):
                content['description'] = desc['source_description']

            if not dryrun:
                with open(f'{label}_CVs/{facet}/{vid}.json','w') as f:
                    f.write(json.dumps(content))

def cv_to_cmor(label: str = 'obs4MIPs', facets: list = None, remote: bool = False, dryrun: bool = False):
    """
    Takes all obs4MIPs/obs4REF files and collects facet values into CMOR tables

    CVs/<facet>/<value>.json -> obs4MIPs_<facet>.json
    """
    print('Migrating changes from CV repo to cmor-tables')
    
    if remote:
        raise NotImplementedError
    
    if not facets:
        facets = CV_ATTRIBUTES

    for facet in facets:
        if not os.path.isfile(f'{label}-cmor-tables/{label}_{facet}.json'):
            print(f' - "{facet}" missing from cmor_tables - skipped')
            continue

        if not os.path.isfile(f'{label}_CVs/{facet}/000_context.jsonld'):
            print(f' - "{facet}" requires creation of new data descriptor in CV - skipped')
            continue

        values = {facet:{}}
        listed = True
        for file in glob.glob(f'{label}_CVs/{facet}/*.json'):

            with open(file) as f:
                content = json.load(f)

            name = content.get('drs_name', content['id'])

            description = content.get('description')

            if description is not None:
                listed = False
            
            values[facet][name] = description

        if listed:
            values[facet] = [i for i in values[facet].keys()]

        with open(f'{label}-cmor-tables/{label}_{facet}.json') as f:
            old_content = json.load(f)

        new_values = [v for v in values[facet] if v not in old_content[facet]]
        if new_values:
            
            print(f'> Updating {label}-cmor-tables/{label}_{facet}.json')
            print(f' > Adding {", ".join(new_values)}')

            if not dryrun:
                with open(f'{label}-cmor-tables/{label}_{facet}.json','w') as f:
                    f.write(json.dumps(values))

@click.command
@click.argument('mode',type=click.Choice(["to_cv","to_cmor","merge"]))
@click.option('-l','--label',type=str)
@click.option('-f','--facet',type=str)
@click.option('-r','--remote',is_flag=True)
@click.option('-d','--dryrun',is_flag=True)

def main(mode: str, label: str | None, facet: str, remote: bool = False, dryrun: bool = False):

    label = label or 'obs4MIPs'

    if facet:
        facets = facet.split(',')
    else:
        facets = None
    
    match mode:
        case 'to_cv':
            cmor_to_cv(label=label, facets=facets, remote=remote, dryrun=dryrun)
        case 'to_cmor':
            cv_to_cmor(label=label, facets=facets, remote=remote, dryrun=dryrun)
        case 'merge':
            cmor_to_cv(label=label, facets=facets, remote=remote, dryrun=dryrun)
            cv_to_cmor(label=label, facets=facets, remote=remote, dryrun=dryrun)


if __name__ == '__main__':
    main()