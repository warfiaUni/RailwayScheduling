import getopt
import random
import sys
import time
from typing import Tuple

import numpy as np

from flatland.core.env_observation_builder import DummyObservationBuilder
from flatland.core.grid.rail_env_grid import RailEnvTransitions
from flatland.core.transition_map import GridTransitionMap
from flatland.envs.line_generators import sparse_line_generator
from flatland.envs.rail_env import RailEnv
from flatland.envs.rail_generators import rail_from_grid_transition_map
from flatland.utils.misc import str2bool
from flatland.utils.rendertools import RenderTool

# --sleep-for-animation=True --do_rendering=True

def custom_rail_map() -> Tuple[GridTransitionMap, np.array]:
    # We instantiate a very simple rail network on a 7x10 grid:
    #  0 1 2 3 4 5 6 7 8 9  10
    # 0        /-------------\
    # 1        |             |
    # 2        |             |
    # 3 _ _ _ /_  _ _        |
    # 4              \   ___ /
    # 5               |/
    # 6               |
    # 7               |
    transitions = RailEnvTransitions()
    cells = transitions.transition_list

    empty = cells[0]
    dead_end_from_south = cells[7]
    right_turn_from_south = cells[8]
    right_turn_from_west = transitions.rotate_transition(right_turn_from_south, 90)
    right_turn_from_north = transitions.rotate_transition(right_turn_from_south, 180)
    dead_end_from_west = transitions.rotate_transition(dead_end_from_south, 90)
    dead_end_from_north = transitions.rotate_transition(dead_end_from_south, 180)
    dead_end_from_east = transitions.rotate_transition(dead_end_from_south, 270)
    vertical_straight = cells[1]
    simple_switch_north_left = cells[2]
    simple_switch_north_right = cells[10]
    simple_switch_left_east = transitions.rotate_transition(simple_switch_north_left, 90)
    horizontal_straight = transitions.rotate_transition(vertical_straight, 90)
    double_switch_south_horizontal_straight = horizontal_straight + cells[6]
    double_switch_north_horizontal_straight = transitions.rotate_transition(
        double_switch_south_horizontal_straight, 180)
    rail_map = np.array(
        [[empty] * 3 + [right_turn_from_south] + [horizontal_straight] * 5 + [right_turn_from_west]] +
        [[empty] * 3 + [vertical_straight] + [empty] * 5 + [vertical_straight]] * 2 +
        [[dead_end_from_east] + [horizontal_straight] * 2 + [simple_switch_left_east] + [horizontal_straight] * 2 + [
            right_turn_from_west] + [empty] * 2 + [vertical_straight]] +
        [[empty] * 6 + [simple_switch_north_right] + [horizontal_straight] * 2 + [right_turn_from_north]] +
        [[empty] * 6 + [vertical_straight] + [empty] * 3] +
        [[empty] * 6 + [dead_end_from_north] + [empty] * 3], dtype=np.uint16)
    rail = GridTransitionMap(width=rail_map.shape[1],
                             height=rail_map.shape[0], transitions=transitions)
    rail.grid = rail_map
    city_positions = [(0, 3), (6, 6)]
    train_stations = [
        [((0, 3), 0)],
        [((6, 6), 0)],
    ]
    city_orientations = [0, 2]
    agents_hints = {'city_positions': city_positions,
                    'train_stations': train_stations,
                    'city_orientations': city_orientations
                    }
    optionals = {'agents_hints': agents_hints}
    print(optionals)
    return rail, rail_map, optionals

def create_env():
    rail, rail_map, optionals = custom_rail_map()
    env = RailEnv(width=rail_map.shape[1],
                  height=rail_map.shape[0],
                  rail_generator=rail_from_grid_transition_map(rail, optionals),
                  line_generator=sparse_line_generator(),
                  number_of_agents=2,
                  obs_builder_object=DummyObservationBuilder(),
                  )
    return env, optionals


def exampleMapToASP(sleep_for_animation, do_rendering):
    random.seed(100)
    np.random.seed(100)

    env, optionals = create_env()
    env.reset()
    
    #testing
    print(env.rail.grid)

    filename = "map.lp"
    # iterate through grid to define ASP syntax and write to file
    with open(filename, 'w') as file:
        stations = optionals['agents_hints']['train_stations']
        for element in stations:
            file.write("stations" + str(element[0]) + ". \n") #TODO: remove ", 0)" from the stations
        for i, row in enumerate(env.rail.grid):
            for j, element in enumerate(row):
                #skip empty cells
                if(element == 0):
                    continue

                #convert to binary
                bin = "{0:016b}".format(element)
                facingNorth = bin[:4]
                facingEast = bin[4:8]
                facingSouth = bin[8:12]
                facingWest = bin[4:]

                direction = 0  #0=N|1=E|2=S|3=w
                for bit in facingNorth:
                    # cell((Y,X),orientation train, direction)
                    if(bit == "1"):
                        lp = "cell((" + str(i) + "," + str(j) + "),0,"+ str(direction) + "). \n"
                        file.write(lp)

                direction = 0  #0=N|1=E|2=S|3=w
                for bit in facingEast:
                    # cell((Y,X),orientation train, direction)
                    if(bit == "1"):
                        lp = "cell((" + str(i) + "," + str(j) + "),1,"+ str(direction) + "). \n"
                        file.write(lp)
                        direction += 1

                direction = 0  #0=N|1=E|2=S|3=w
                for bit in facingSouth:
                    # cell((Y,X),orientation train, direction)
                    if(bit == "1"):
                        lp = "cell((" + str(i) + "," + str(j) + "),2,"+ str(direction) + "). \n"
                        file.write(lp)
                        direction += 1

                direction = 0  #0=N|1=E|2=S|3=w
                for bit in facingWest:
                    # cell((Y,X),orientation train, direction)
                    if(bit == "1"):
                        lp = "cell((" + str(i) + "," + str(j) + "),3,"+ str(direction) + "). \n"
                        file.write(lp)
                        direction += 1

    if do_rendering:
        env_renderer = RenderTool(env)
        env_renderer.render_env(show=True, show_observations=False)

    if sleep_for_animation:
        time.sleep(5)
        env_renderer.close_window()

    # uncomment to keep the renderer open
    #input("Press Enter to continue...")
    

def main(args):
    try:
        opts, args = getopt.getopt(args, "", ["sleep-for-animation=", "do_rendering=", ""])
    except getopt.GetoptError as err:
        print(str(err))  # will print something like "option -a not recognized"
        sys.exit(2)
    sleep_for_animation = True
    do_rendering = True
    for o, a in opts:
        if o in ("--sleep-for-animation"):
            sleep_for_animation = str2bool(a)
        elif o in ("--do_rendering"):
            do_rendering = str2bool(a)
        else:
            assert False, "unhandled option"

    # execute example
    exampleMapToASP(False, False)


if __name__ == '__main__':
    if 'argv' in globals():
        main(argv)
    else:
        main(sys.argv[1:])
