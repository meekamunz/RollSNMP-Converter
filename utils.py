import re
import os
import json

from pathlib import Path

MIB_SOURCE_REGEX = r'<MIBSource.*href=".*?".*?>'

GLOBAL_TRANSLATION_DEF_LINK_REGEX = r'<GlobalTranslationDef.*link="(.*?)".*?>'
TRANSLATION_DEF_LINK_REGEX = r'(<TranslationDef.*link=")(.*?)(".*?>)'


# supervisor log file needs this.
def log(message):
    print(message, flush=True)


def get_includes_from_includes_json(snmp_library_dir, file):
    includes = []

    with open(file, "r") as f:
        try:
            includes_json = json.loads(f.read())
        except json.decoder.JSONDecodeError as e:
            log(f'Failed to parse JSON file "{file}: {e}"')
        for include in includes_json:
            includes_path = os.path.relpath(os.path.join(os.path.dirname(file), include), snmp_library_dir)
            href = includes_path.replace('\\', '/')
            includes.append(href)

    return includes


def get_driver_id(driver_dict):
    manufacturer = driver_dict["manufacturer"].strip().replace('_', '-').replace(' ', '-').upper()
    driver = driver_dict["driverName"].strip().replace('_', '-').replace(' ', '-').upper()
    version = re.sub("[^0-9.]", '', driver_dict["driverVersion"])
    return f'{manufacturer}_{driver}_{version}'


def get_driver_id_from_driver_json(file):
    with open(file, "r") as f:
        try:
            driver = json.loads(f.read())
        except json.decoder.JSONDecodeError as e:
            return ''

        return get_driver_id(driver)


def get_driver_json_from_driver_id(snmp_library_dir, driver_id):
    file = next(Path(snmp_library_dir).rglob(f'{driver_id}/*.json'), None)
    if file is not None:
        with open(file, "r") as f:
            try:
                return json.loads(f.read())
            except json.decoder.JSONDecodeError as e:
                return None
    return None


def get_includes_from_driver_json(snmp_library_dir, file):
    includes = []

    with open(file, "r") as f:
        try:
            driver = json.loads(f.read())
        except json.decoder.JSONDecodeError as e:
            log(f'Failed to parse JSON file "{file}: {e}"')
        if 'includes' in driver:
            for include in driver['includes']:
                driver_path = os.path.relpath(os.path.join(os.path.dirname(file), include), snmp_library_dir)
                href = driver_path.replace('\\', '/')
                includes.append(href)

    return includes


def get_includes(snmp_library_dir, path):
    includes = []

    # Parse includes file
    files = Path(path).rglob('includes.json')
    for file in files:
        includes.extend(get_includes_from_includes_json(snmp_library_dir, file))

    # Parse driver file
    files = Path(path).rglob('driver.json')
    for file in files:
        includes.extend(get_includes_from_driver_json(snmp_library_dir, file))
    return includes


def update_driver_mib_paths(snmp_library_dir, rsnmp_file):
    driver_dir = os.path.dirname(rsnmp_file)
    mibs_path = os.path.join(os.path.relpath(driver_dir, snmp_library_dir), 'MIBs')
    mibs_href = mibs_path.replace('\\', '/')
    
    with open(rsnmp_file, 'r') as f:
        content = re.sub(MIB_SOURCE_REGEX, f'<MIBSource href="{mibs_href}"/>', f.read())
        
    with open(rsnmp_file, 'w') as f:
        f.write(content)


def update_library_mib_paths(snmp_library_dir):
    files = Path(snmp_library_dir).rglob('*.rsnmp')
    for file in files:
        update_driver_mib_paths(snmp_library_dir, file)


def update_driver_type_name(driver_dir):
    driver_json_file = os.path.join(driver_dir, 'driver.json')
    driver_id = get_driver_id_from_driver_json(driver_json_file)
    files = Path(driver_dir).rglob('*.rsnmp')
    for rsnmp_file in files:
        with open(rsnmp_file, 'r') as f:
            text = f.read()
            regex = r'(<UnitTypeDef.*typeName=").*?(".*?>)'
            text = re.sub(regex, rf'\1{driver_id}\2', text)

        with open(rsnmp_file, 'w') as f:
            f.write(text)


def update_library_type_names(snmp_library_dir):
    files = Path(snmp_library_dir).rglob('driver.json')
    for file in files:
        driver_dir = os.path.dirname(file)
        update_driver_type_name(driver_dir)


def update_driver_link_names(driver_dir):
    driver_json_file = os.path.join(driver_dir, 'driver.json')
    driver_id = get_driver_id_from_driver_json(driver_json_file)

    rsnmp_files = Path(driver_dir).rglob('*.rsnmp')

    # Get existing link names
    links = []
    for file in rsnmp_files:
        with open(file, 'r') as f:
            matches = re.findall(GLOBAL_TRANSLATION_DEF_LINK_REGEX, f.read())
            links.extend(matches)

    rsnmp_files = Path(driver_dir).rglob('*.rsnmp')

    for file in rsnmp_files:
        with open(file, 'r') as f:
            text = f.read()

        for link in links:
            # Don't process links that have already been updated
            if '::' in link:
                continue

            new_link = f'{driver_id}::{link}'

            regex = rf'(<GlobalTranslationDef.*link="){link}(".*?>)'
            text = re.sub(regex, rf'\1{new_link}\2', text)

            regex = rf'(<TranslationDef.*link="){link}(".*?>)'
            text = re.sub(regex, rf'\1{new_link}\2', text)

        with open(file, 'w') as f:
            f.write(text)


def update_library_driver_link_names(snmp_library_dir):
    files = Path(snmp_library_dir).rglob('driver.json')
    for file in files:
        driver_dir = os.path.dirname(file)
        update_driver_link_names(driver_dir)


def update_library_driver_directory_name(driver_dir):
    driver_json_file = os.path.join(driver_dir, 'driver.json')
    driver_id = get_driver_id_from_driver_json(driver_json_file)
    new_driver_dir = os.path.join(os.path.dirname(driver_dir), driver_id)
    if driver_dir != new_driver_dir:
        os.rename(driver_dir, new_driver_dir)


def update_library_driver_directory_names(snmp_library_dir):
    files = Path(snmp_library_dir).rglob('driver.json')
    file_list = []
    for file in files:
        file_list.append(file)

    for file in file_list:
        driver_dir = os.path.dirname(file)
        update_library_driver_directory_name(driver_dir)


if __name__ == '__main__':
    import confighandler

    confighandler.CONFIG_FILE_PATH = 'C:\\src\\snmp\\rsnmp_service\\config\\config.rsnmp'

    update_library_mib_paths('C:\\src\\snmp\\rsnmp_service\\config\\snmp_library')
    update_library_type_names('C:\\src\\snmp\\rsnmp_service\\config\\snmp_library')
    update_library_driver_link_names('C:\\src\\snmp\\rsnmp_service\\config\\snmp_library')
    update_library_driver_directory_names('C:\\src\\snmp\\rsnmp_service\\config\\snmp_library')

    confighandler.get_instance().reload()
    confighandler.get_instance().write()

