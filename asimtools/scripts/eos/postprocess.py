'''.Xauthority'''

from typing import Dict, Tuple
import numpy as np
import matplotlib.pyplot as plt
from ase.eos import EquationOfState
from ase.io import read
from ase. units import GPa
# from asimtools.job import load_output_images, load_input_images
from asimtools.utils import (
    write_csv_from_dict,
    get_images,
)

def postprocess(
    images: Dict = None,
) -> Tuple[None,Dict]:
    ''' plot things '''
    # Should we standardize to using pandas? Issue is that switching
    # between np and pandas is probably not good

    # Should change this to load_jobs_from_directory once we
    # know everything else works
    images = get_images(**images)
    volumes = np.array([at.get_volume() for at in images])
    energies = np.array([at.get_potential_energy() for at in images])
    write_csv_from_dict(
        'eos_output.csv',
        {'volumes': volumes, 'energies': energies}
    )
    eos_fit = EquationOfState(volumes, energies)

    try:
        v0, e0, B = eos_fit.fit()
    except ValueError:
        print('ERROR: Could not fit EOS, check structures')
        v0, e0, B = None, None, None

    fig, ax = plt.subplots()
    if v0 is not None:
        B_GPa = B / GPa # eV/Ang^3 to GPa
        eos_fit.plot(ax=ax)

        # Get equilibrium lattice scaling by interpolation
        xs = [atoms.info['scale'] for atoms in images]
        vs = []
        atoms = read('../step-0/input_image.xyz')
        for x in xs:
            samp_atoms = atoms.copy()
            samp_atoms.cell = samp_atoms.cell*x
            vs.append(samp_atoms.get_volume())
        x0 = np.interp(v0, vs, xs)

        results = {
            'equilibrium_volume': float(v0),
            'equilibrium_energy': float(e0),
            'equilibrium_scale': float(x0),
            'bulk_modulus': float(B_GPa),
            'bulk_modulus_unit': 'GPa',
        }
    else:
        ax.plot(volumes, energies)
        results = {}
    ax.set_xlabel(r'Volume ($\AA$)')
    ax.set_ylabel(r'Energy (eV)')
    plt.savefig('eos.png')
    plt.close(fig)
    return results
