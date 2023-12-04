import logging

from flatland.envs.rail_env import RailEnv

from rasch.direction import Direction

logger = logging.getLogger("railway")


def schedule_literal(agent) -> str:
    """ Get agent schedule as ASP literal."""
    return (f"schedule("
            f"{agent.handle}"
            f",{agent.initial_position}"
            f",{agent.target}"
            f",{Direction(agent.direction).name}"
            f",{agent.earliest_departure}"
            f").")


def cell_literal(x: int, y: int, agent_orientation: Direction, directions: list[Direction]) -> str:
    """ Get cell description as ASP literal."""
    return f"cell(({x},{y}),{agent_orientation.name},({';'.join([direction.name for direction in directions])}))."


def generate_instance_lines(env: RailEnv, limit: int) -> list[str]:
    """ Generate ASP instance lines from Flatland environment."""

    # TODO: Error handling? Yes? No? Maybe? I dont know! Can you repeat the question...
    if (env.rail is None):
        return []

    logger.info("Generating ASP instance.")

    limit_literal = f"limit({limit})."

    schedules = ["",
                 "% (agentID,start,target,starting-orientation,earliest-departure)",
                 *[schedule_literal(agent) for agent in env.agents]
                 ]

    logger.info(f"{len(schedules)} schedule literals done.")

    cells = [
        "",
        "%grid definition cell((Y,X),train orientation, (possible directions))"
    ]
    for y, row in enumerate(env.rail.grid):
        for x, cell in enumerate(row):
            if not cell:
                continue

            for i in range(4):
                facing_direction = (cell >> (12-4*i)) & 0xF

                valid_directions = []

                for j in range(4):
                    valid = (facing_direction >> (3 - j)) & 0xb1

                    if valid:
                        valid_directions.append(Direction(j))

                        # if the cell is a dead end
                        # add the possibility to move
                        # off of it in case the agent starts on it
                        if j == (i+2) % 4:
                            valid_directions.append(Direction(i))

                if len(valid_directions) > 0:
                    cells.append(cell_literal(
                        y, x, Direction(i), valid_directions))

    logger.info(f"{len(cells)} cell literals done.")

    diffs = [
        "",
        "% define differences to calculate adjacent cells",
        "diff(n, -1, 0). % North",
        "diff(e, 0, 1).  % East",
        "diff(s, 1, 0).  % South",
        "diff(w, 0, -1). % West",
    ]

    return [limit_literal, *schedules, *cells, *diffs]
