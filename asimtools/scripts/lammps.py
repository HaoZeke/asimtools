#!/usr/bin/env python
'''
Runs a user defined lammps script or template 

### BROKEN ###

Author: mkphuthi@github.com
'''
from typing import Dict
import subprocess
from asimtools.job import Job
from asimtools.utils import (
    get_atoms,
    join_names,
)

# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=dangerous-default-value

def lammps(
    calc_input: Dict,
    template: str,
    image: Dict = None,
    prefix: str = '',
    variables: Dict = {},
    **kwargs
) -> Dict:
    ''' 
    Runs a lammps simulation based on a template lammps input script
    '''
    job = Job(calc_input, {'prefix': prefix})
    job.start()

    lmp_txt = ''
    for variable, value in variables.items():
        lmp_txt += f'variable {variable} equal {value}\n'

    lmp_txt += '\n'
    with open(template, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        lmp_txt += line

    # Make sure the provided script follows standard for reading
    # in arbitrary image provided by asimtools
    if image is not None:
        assert 'read_data ${image_file}' in lmp_txt, \
            'Make sure "read_data " command is used \
            in lammps input script if you specify image keyword'
        atoms = get_atoms(**image)
        atoms.write('image_input.lmpdat', format='lammps-data')

    lmp_inp_file = join_names([prefix, 'input.lammps'])
    with open(lmp_inp_file, 'w', encoding='utf-8') as f:
        f.write(lmp_txt)

    lmp_cmd = calc_input.get('calc', {}).get('lmp_command', 'lmp ')
    command = lmp_cmd + f' -i {lmp_inp_file}'
    command = command.split(' ')
    if kwargs.get('submit', True):
        completed_process = subprocess.run(
                command, check=False, capture_output=True, text=True,
            )

        with open('lmp_stdout.txt', 'w', encoding='utf-8') as f:
            f.write(completed_process.stdout)

        if completed_process.returncode != 0:
            err_txt = f'Failed to run {lmp_inp_file}\n'
            err_txt += 'See lmp.stderr.txt for details.'
            print(err_txt)
            with open('lmp_stderr.txt', 'w', encoding='utf-8') as f:
                f.write(completed_process.stderr)
            completed_process.check_returncode()
            job.update_status('failed')
            return None

    job.add_output_files({'log': 'log.lammps'})
    job.complete()
    return job.get_output()
