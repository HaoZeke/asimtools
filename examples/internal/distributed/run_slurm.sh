#!/usr/bin/env bash

# These examples explicitly specify a choice of env_input.yaml and calc_input.yaml
# If you want to use the globally set ones instead, it is not necessary to specify
# them.

# Run the asimmodule in an interactive job
asim-execute distributed_batch_sim_input.yaml -c ../calc_input.yaml -e ../env_input.yaml

# Run the asimmodule in a batch job
asim-execute distributed_mixed_sim_input.yaml -c ../calc_input.yaml -e ../env_input.yaml
