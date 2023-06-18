# Atomic SIMulation Tools

This package is for optimizing and standardizing production runs for atomistic simulations. By using in-built or user-defined scripts,
users can run their own simulation recipes and scale them on slurm based clusters. The core idea is to separate the dependence of the
atomistic potential/calculator and the simulations steps thereby allowing the same simulation to be run with multiple calculators and
the same calculator to be used for multiple simulations. Input and output files must follow a strict format so that consistent 
analysis pipelines can be used across users

## Getting Started

These instructions will give you a copy of the project up and running on
your local machine for development and testing purposes.

### Installing
You can install asimtools in a new conda environment using:
```
conda create -n asimtools python=3.9
conda activate asimtools

conda install ase -c conda-forge

git clone https://github.com/BattModels/asimtools.git
cd asimtools
pip install -e .
```

This installs the base package in developer mode so that you do not have to
reinstall every time you make changes.

Individual calculators may need external packages for loading those calculators. It is up to the user to make sure those are installed.

You sill also need to setup some environment variables, these variables point
to a `env_input.yaml` and `calc_input.yaml` with your favorite configs since
these are commonly shared among simulations. You can also directly specify them
when running `asim-execute` but this might be buggy (See `asim-execute -h`). 
Examples of these files can be found in the `singlepoint` example.

Add the following to your `.bashrc`
```
export ASIMTOOLS_ENV_INPUT=/path/to/my/env_input.yaml
export ASIMTOOLS_CALC_INPUT=/path/to/my/calc_input.yaml
```

### Custom scripts
To enable users to write their own scripts without touching the source code,
you can also specify a ASIMTOOLS_SCRIPT_PATH where ASIMTools will look for 
scripts in addition to the core scripts. This is not implemented and tested yet
but the idea is to have a `.asimtools` dotfile where all these environment 
variables will be defined

## Examples
Below are a few examples on how to run already implemented scripts.

The first thing to understand is the difference between `asim-execute sim_input.yaml` and 
`asim-run sim_input.yaml`. The latter runs the chosen script in whatever location 
and environment it happens to be launched from i.e. equivalent to 
`python my_script.py sim_input.yaml` whereas the latter runs submits the job 
that runs the script e.g. it will go to the work directory and launch a slurm job 
from there containing `asim-run sim_input.yaml`.  `asim-execute` is essentially 
"environment-aware" and runs the script in the environment specified by `env_id`
whereas `asim-run` does not use `env_id` at all.

The philosophy is to build "simulations" using building blocks of scripts. 
These scripts can be as complicated/efficient using any external packages 
you want and can be optimized with time but can still be run within the 
framework. This allows a test friendly way to transition from say a tutorial
on the ASE/pymatgen website to an asimtools script. So while 
complicated wrappers are discouraged, they would still work as long as the 
script works. The benefit out of the box is that you can make your script 
independent of calculator or input structures and submit them easily.

A template is provided for writing a new script called `template.py`

We provide a standard set of building block scripts for simulations/workflows that tend
to form components of large simulations. Let us consider some examples. 
To see details of their arguments (`args`), see their docstrings (which don't exist yet :( )

1. The simplest are "unit" scripts which do not internally call other scripts 
or depend on results from other scripts. 
The simplest example is `singlepoint.py` which runs an energy/force/stress calculation
on a single structure. To launch in your environment of choice specified by
`env_id` in `sim_input.yaml` use `asim-execute sim_input.yaml`. See `asim-execute -h`. 
For all scripts, you have the ability to specify the `env_input.yaml` and `calc_input.yaml` or 
skip them to use the global files specified in `ASE_CALC_INPUT` and 
`ASE_ENV_INPUT`. Note that many scripts don't need `calc_input.yaml` if they 
just do some preprocessing or analysis. Another example is `atom_relax.py`.
*Exercise: Add `cell_relax.py` based on `atom_relax.py`*

2. Another type are "parent" scripts which launch multiple "child" scripts in parallel.
An example is `image_array.py` which runs the same simulation on multiple
images e.g. you want the energies of all the structures in a database. Note
that you only need to point to the images, the env and the calc in the sim_input,
The script, which uses a DistributedJob object automatically handles whether to
submit jobs using a slurm array, individual slurm jobs or one after the other
depending on the specified `env_id`. Another example is 
`strong_scaling.strong_scaling.py`. 
*Exercise: Implement `env_array.py` and `calc_array.py` based on `image_array.py` and `strong_scaling.py`.*

3. The last major type of "parent" script are chained scripts. These scripts run one 
**UnitJob** after the other based on a specified workflow. The job automatically runs
one job after another or submits slurm jobs with appropriate dependencies. Note
that if one of the unitjobs internally calls another script such as 
`image_array.py`, then the slurm dependencies will fail but everything else should work.
In this casea, the current workaround is to set `submit=false` for the stages of 
the chain that would fail due to a previous array/chain job. Then rerun `asim-execute`
again with `submit=true`, It should automatically skip the completed steps. See `eos.eos.py` 
and the corresponding example. An example to help understand the genera; chained sim_input is 
`chained`

4. Hybrid jobs combine multiple of these elements e.g. `eos.eos.py` runs a
`preprocessing` script to prepare the scaled structures followed by a UnitJob that submits
an `image_array` for each scaled structure and finally a unitjob to `postprocess`
the results from the array. It is possible to 
- build hybrid scripts in python without using existing asimtools scripts
- running a `chained.py` on a `sim_input.yaml` with the correct format that runs scripts that are already defined
- to write a script such that it directly manipulates Job objects. This is the most flexible and robust but ofcourse most complicated
*Exercise: Run the eos calculation without writing any new scripts, simply using the scripts in the core (image_array) and eos subfolder (preprocessing and postprocessing).* 
The key is being able to to point to the correct files for each step before the calculation is run.

## Running the tests

To run all tests from the tests directory, call:

    pytest

To run the test suite on a component `component.py` , call:

    pytest test_component.py
    
<!-- ## Basic example

Simulations are run by providing a `*calc_input.yaml` and `*sim_input.yaml` file which specify 
the calculator (and the environment it runs in) and the simulation parameters which are specific 
to the simulation being run. The recommended method for calling scripts is to use

```
asim-run *calc_input.yaml *sim_input.yaml
``` -->

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code
of conduct, and the process for submitting pull requests to us.

## Authors

  - **Keith Phuthi**
    [mkphuthi](https://github.com/mkphuthi)

See also the list of
[contributors](https://github.com/BattModels/asimtools.git/contributors)
who participated in this project.

## License

This project is licensed under the ABC License

## Acknowledgments

  - Hat tip to anyone whose code is used
