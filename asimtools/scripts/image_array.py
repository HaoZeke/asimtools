#!/usr/bin/env python
'''
Apply the same script on multiple images

Author: mkphuthi@github.com

'''

from typing import Dict, Sequence, Optional
from copy import deepcopy
from asimtools.job import DistributedJob
from asimtools.utils import get_images

def image_array(
    images: Dict,
    subscript_input: Dict,
    calc_input: Optional[Dict] = None,
    env_input: Optional[Dict] = None,
    ids: Sequence[str] = None,
    env_ids: Sequence[str] = None,
    array_max: Optional[int] = None,
) -> Dict:
    """Submit the same script on multiple images and if specified, use
    different env_ids

    :param images: Image config, see :func:`asimtools.utils.get_atoms`
    :type images: Dict
    :param subscript_input: sim_input of script to be run
    :type subscript_input: Dict
    :param calc_input: calc_input to override global file, defaults to None
    :type calc_input: Optional[Dict], optional
    :param env_input: env_input to override global file, defaults to None
    :type env_input: Optional[Dict], optional
    :param ids: Custom ids for each image, defaults to None
    :type ids: Sequence[str], optional
    :param env_ids: Sequence of envs for each image, must be the same length \
        as the total number of images, defaults to None
    :type env_ids: Sequence[str], optional
    :param array_max: Maximum jobs to run simultanteously in job array, \
        defaults to None
    :type array_max: Optional[int], optional
    :return: Dictionary of results
    :rtype: Dict
    """
    images = get_images(**images)
    array_sim_input = {}

    # Allow user to customize subdirectory names if needed
    if ids is None:
        ids = [str(i) for i in range(len(images))]
    else:
        assert len(ids) == len(images), \
            'Num. of images must match num. of ids'

    if env_ids is not None:
        assert len(env_ids) == len(images), \
            f'Num. images ({len(images)}) must match env_ids ({len(env_ids)})'

    # Make individual sim_inputs for each image
    for i, image in enumerate(images):
        new_subscript_input = deepcopy(subscript_input)
        new_subscript_input['args']['image'] = {
            'atoms': image
        }
        array_sim_input[f'{ids[i]}'] = new_subscript_input

        if env_ids is not None:
            new_subscript_input['env_id'] = env_ids[i]

    # Create a distributed job object
    djob = DistributedJob(array_sim_input, env_input, calc_input)
    job_ids = djob.submit(array_max=array_max)

    results = {'job_ids': job_ids}
    return results
