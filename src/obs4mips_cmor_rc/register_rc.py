import json
import glob
import os

RC_MAPPINGS = {
    'key': 'Enter new Source Identifier: ',
    'source_name': 'Source Name (leave blank if identical to source_id): ',
    'source_label': 'Source Label (leave blank if identical to source_id): ',
    'release_year': 'Release Year: ',
    'source_description': 'Description of new source ID: ',
    'source_version_number': 'Source Version: ',
    'institution_id': 'Institution ID: ',
    'region': 'Region: ',
    'source_type': 'Source Type: ',
    'source_variables': 'Enter Applicable Variables (space delimited): '
}

VALIDATORS = {
    'key': None,
    'source_name': None,
    'source_label': None,
    'release_year': 'numeric',
    'source_description': None,
    'source_version_number': 'm1dnumeric',
    'institution_id': 'obs4MIPs_institution_id.json',
    'region': 'obs4MIPs_region.json',
    'source_type': 'obs4MIPs_source_type.json',
    'source_variables': 'variables'
}

NON_FILE_VALIDATION = {
    'source_variables': 'Variable must exist in one of the Tables',
    'source_version_number': 'Version must be of the form "vX.X" or similar',
    'release_year': "Release year must be numeric"
}

BLANK_MAP = {
    'source_name': 'key',
    'source_label': 'key'
}

BASE_DIR = "."

def check_all_files_for_variable(variables: list):

    allvars = []
    for file in glob.glob(f'{BASE_DIR}/Tables/*.json'):
        with open(file) as f:
            ref = json.load(f)
        if 'variable_entry' in ref:
            allvars += ref['variable_entry'].keys()

    for var in variables:
        if var not in allvars:
            print(f'Variable "{var}" is not recognised in any existing table')
            return False
        
    return True
        
def obtain_list_valid(key: str, validation: str | None) -> list | None:

    if validation is None:
        return False
    
    if not os.path.isfile(f'{BASE_DIR}/{validation}'):
        return False

    with open(f'{BASE_DIR}/{validation}') as f:
        refs = json.load(f)

    if isinstance(refs[key],list):
        return refs[key]
    else:
        return list(refs[key].keys())
    
def check_valid(key: str, value: str, validation: str | None) -> bool:

    if validation is None:
        return True
    
    if '.json' in validation:
        list_valid = obtain_list_valid(key, validation)
        return value in list_valid

    else:
        match validation:
            case 'numeric':
                return value.isnumeric()
            case 'm1dnumeric':
                v = value.replace('.','')
                return (not v.isnumeric() and v[1:].isnumeric())
            case 'variables':
                # Check variables in available files
                return check_all_files_for_variable(value.split(' '))
            
    return None

def collect_rc(key: str, message: str, validator: str | None = None) -> str:

    valid = False
    while not valid:
        value = input(message)
        if value == 'EXIT':
            raise KeyboardInterrupt
        elif value == 'LIST':

            list_valid = obtain_list_valid(key, validator)
            if list_valid:
                print(f'Valid Values: {", ".join(
                    list_valid
                )}')
            else:
                if key in NON_FILE_VALIDATION:
                    print(NON_FILE_VALIDATION[key])
                else:
                    print('No file-based validation for this facet - value list not available')
        elif validator:
            valid = check_valid(key, value, validator)
            if not valid:
                print(
                    f'Error: {value} is not valid for {key} - '
                    f'{NON_FILE_VALIDATION.get(key, "type LIST to see possible values.")}')
        else:
            valid = True

    return value

def collect_rcs():

    entry = {}
    for facet, request in RC_MAPPINGS.items():
        entry[facet] = collect_rc(facet, request, validator=VALIDATORS[facet])

    for key, map in BLANK_MAP.items():
        if entry[key] == '':
            entry[key] = entry[map]

    return entry
        
def main():
    entry = collect_rcs()
    key = entry.pop('key')

    # Display results
    print('')
    print(f'Adding source: {key}')
    for k, v in entry.items():
        print(f'> {k}: {v}')

    accept = input("Accept these parameters? (Y/N): ")
    if accept != 'Y':
        return

if __name__ == '__main__':
    main()