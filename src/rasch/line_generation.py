from typing import Any, Optional

from flatland.core.transition_map import GridTransitionMap
from flatland.envs.line_generators import BaseLineGen
from flatland.envs.timetable_utils import Line
from matplotlib.pylab import RandomState


class FixedLineGen(BaseLineGen):
    """ This line generator assigns a predefined starting point, 
        end point and orientation to each agent.
    """

    def __init__(self, agent_settings: list[tuple[tuple[int, int], tuple[int, int], int]]):
        """ Create a new Fixed Line Generator.

            Parameters:
                agent_settings: A list of tuples defining start- and 
                                endpoints as well as starting orientation

            Example: agent_settings: {
                ((0,0), (4,5), 2)
            }

            The agent starts at position (0,0), it's destination is at (4,5) 
            and the starting orientation is south (2)
        """
        super().__init__()

        self.agent_settings = agent_settings

    def generate(self,
                 rail: GridTransitionMap,
                 number_of_agents: int,
                 hints: Any = None,
                 num_resets: int = 0,
                 np_random: Optional[RandomState] = None) -> Line:
        """ Generate a new line according to the predefined agent settings if possible."""

        if (number_of_agents != len(self.agent_settings)):
            raise Exception((
                f"number_of_agents {number_of_agents} does not match "
                f"the number of agents in settings {len(self.agent_settings)}"
            ))

        speeds = [1.0] * number_of_agents

        train_stations = hints['train_stations']

        agent_positions = []
        agent_orientations = []
        agent_targets = []

        possible_positions = set()

        for city in train_stations:
            for station in city:
                possible_positions.add(station[0])

        for settings in self.agent_settings:
            start = settings[0]
            target = settings[1]
            orientation = settings[2]

            if start not in possible_positions:
                raise Exception(
                    f"Position {start} is not a valid station position.\n Valid positions: {possible_positions}")
            if target not in possible_positions:
                raise Exception(
                    f"Position {target} is not a valid station position.\n Valid positions: {possible_positions}")

            if not rail.check_path_exists(start, orientation, target):
                raise Exception(
                    f"Orientation {orientation} does not lead to a valid path.")

            agent_positions.append(start)
            agent_targets.append(target)
            agent_orientations.append(orientation)

        return Line(agent_positions=agent_positions, agent_directions=agent_orientations,
                    agent_targets=agent_targets, agent_speeds=speeds)
