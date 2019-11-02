import copy
import json

def select_next_generation(old_generation, current_generation):
    with open("tools/parameters.json") as f:
        parameters = json.load(f)

    if 'parent_to_child_size' in parameters['config1'].keys():
        parent_to_child_size = parameters['config1']['parent_to_child_size']
    else:
        parent_to_child_size = parameters['default']['parent_to_child_size']

    old_generation_temp = copy.deepcopy(old_generation)
    current_generation_temp = copy.deepcopy(current_generation)

    old_generation_temp.sort(key=lambda x: x[len(x) - 1])
    current_generation_temp.sort(key=lambda x: x[len(x) - 1])

    return sorted(old_generation_temp[0:int(len(old_generation_temp) * parent_to_child_size)] +
                  current_generation_temp[0:int(len(current_generation_temp) * (1 - parent_to_child_size))]
                  , key=lambda x: x[len(x) - 1])
