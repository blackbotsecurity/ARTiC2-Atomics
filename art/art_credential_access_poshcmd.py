from blackbot.core.utils import get_path_in_package, print_good
from blackbot.core.srv.atomic import Atomic
from terminaltables import SingleTable

import os
import json

class Atomic(Atomic):
    def __init__(self):
        self.name = 'CredentialAccess/hybrid'
        self.controller_type = ''
        self.version = ''
        self.language = 'boo'
        #self.description = 'Chains Defense DE techniques (AMSI and Logging Bypass) to obtain accesss to unmanaged PowerShell runtime space'
        self.description = self.get_description()
        self.last_updated_by = 'Blackbot, Inc. All Rights reserved'
        self.references = ["System.Management.Automation"]
        self.options = {
            'Atomic': {
                'Description'   :   'Atomic test you want to execute',
                'Required'      :   True,
                'Value'         :   '',
            },
            'OutString': {
                'Description'   :   'Appends Out-String to the PowerShellCode',
                'Required'      :   False,
                'Value'         :   True,
            },
            'BypassLogging': {
                'Description'   :   'Bypasses ScriptBlock and Techniques logging',
                'Required'      :   False,
                'Value'         :   True,
            },
            'BypassAmsi': {
                'Description'   :   'Bypasses AMSI',
                'Required'      :   False,
                'Value'         :   True,
            }

        }

    @property
    def blackbot_id(self):
        global alias_map
        alias_map = self.get_alias_map()

        if self.options['Atomic']['Value'] not in alias_map:
            raise Exception('Atomic test does not exist: {}'.format(self.options['Atomic']['Value']))

        ttp = alias_map[self.options['Atomic']['Value']]
        return ttp

    @property
    def external_id(self):
        external_id = self.blackbot_id
        external_id = external_id.split('-')[0]

        return external_id

    def payload(self):
        with open(get_path_in_package('core/srv/ttp/art/src/hybrid.boo'), 'r') as ttp_src:
            src = ttp_src.read()
            hybrid_script = get_path_in_package(f'core/srv/ttp/art/posh_cmd_scripts/credentialAccess/{self.options["Atomic"]["Value"]}')

            with open(hybrid_script) as hybrid:
                ps1_script = ''
                cmd_script = ''
                cmd_script_starts = False

                for line in hybrid.readlines():
                    if line.strip('\n') == '#commands':
                        cmd_script_starts = True
                    
                    if cmd_script_starts:
                        cmd_script += line
                    else:
                        ps1_script += line

                src = src.replace("POWERSHELL_SCRIPT", ps1_script)
                src = src.replace("CMD_SCRIPT", cmd_script)
                src = src.replace("OUT_STRING", str(self.options["OutString"]["Value"]).lower())
                src = src.replace("BYPASS_LOGGING", str(self.options["BypassLogging"]["Value"]).lower())
                src = src.replace("BYPASS_AMSI", str(self.options["BypassAmsi"]["Value"]).lower())
                return src

    def walking_in_directory(self):
        path = get_path_in_package('core/srv/ttp/art/posh_cmd_scripts/credentialAccess/')

        (root, _, filenames) = next(os.walk(path))
        return (root, _, filenames)

    def get_description(self):
        root, _, scripts = self.walking_in_directory()
        scripts.sort()

        full_description = {}
        for s in scripts:
            with open(root + s) as text:
                head = [next(text) for l in range(2)]
                technique_name = head[0].replace('#TechniqueName: ', '').strip('\n')
                atomic_name = head[1].replace('#AtomicTestName:', '').strip('\n')

                if technique_name not in full_description:
                    full_description[technique_name] = [(atomic_name, s)]
                else:
                    full_description[technique_name].append((atomic_name, s))
        
        description_display = ''
        table_data = []
        for key, values in full_description.items():
            table_data.append([f'\n#{key}', ''])
            
            for ttp_variant in values:
                table_data.append([f'  {ttp_variant[0]}', ttp_variant[1]])

        table = SingleTable(table_data, title='Atomics')
        table.inner_column_border = False
        table.inner_heading_row_border = False
        table.inner_row_border = False
        table.outer_border = False

        description_display += table.table

        return description_display 


    def get_alias_map(self):
        root, _, scripts = self.walking_in_directory()
        scripts.sort()

        alias_map = {}
        for s in scripts:
            alias_map[s] = f'{s}'

        return alias_map




