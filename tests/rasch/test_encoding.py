import re
from collections import defaultdict


def dict_safe_function():
    return False 

class TestSimpleSwitchInstance():
    def test_model_is_not_empty(self,json_simple_switch_map_from_instance):
        assert json_simple_switch_map_from_instance['models'] != [], f"No models in solution JSON. {json_simple_switch_map_from_instance['models']}"

    def test_agent_starts_from_start(self,json_simple_switch_map_from_instance):
        first_model = json_simple_switch_map_from_instance["models"][0]

        pattern0 = re.compile(r'trans\(0,\(1,2\),.*,0\)')
        pattern1 = re.compile(r'trans\(1,\(1,0\),.*,0\)') #pattern "trans(1,(1,0),...,0)"
        found_0 = False
        found_1 = False

        for entry in first_model:
            matches_0 = re.findall(pattern0, entry)
            matches_1 = re.findall(pattern1, entry)
            if matches_0:
                found_0 = True
            if matches_1:
                found_1 = True
        assert found_0 & found_1

    def test_agent_ends_at_end(self,json_simple_switch_map_from_instance):
        first_model = json_simple_switch_map_from_instance["models"][0]

        pattern0 = re.compile(r'trans\(0,.*,\(1,0\).*\)') #pattern "trans(0,...,(1,0)..."
        pattern1 = re.compile(r'trans\(1,.*,\(1,2\).*\)')
        found_0 = False
        found_1 = False

        for entry in first_model:
            matches_0 = re.findall(pattern0, entry)
            matches_1 = re.findall(pattern1, entry)
            if matches_0:
                found_0 = True
            if matches_1:
                found_1 = True
        assert found_0 & found_1

    def test_correct_timesteps_agent0(self,get_trans_unsorted):
        pattern_timestep = re.compile(r'(\d+)(?!.*\d)') #match timestep
        sorted_trans_agent0 = defaultdict(dict_safe_function) #returns false when key not found
        max = 0

        for entry in get_trans_unsorted[0]: #iterate through trans of agent 0
            timestep = re.findall(pattern_timestep, entry)[0]
            if not sorted_trans_agent0[timestep]: #if timestep is not already in dict
                sorted_trans_agent0[timestep] = entry 
                max += 1
            else:
                raise AssertionError(f'double timesteps at {entry}') #timestep is already in dict
            
        assert len(get_trans_unsorted[0]) == max, f"Skipped timestep, length != {max}"
    