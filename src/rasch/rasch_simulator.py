import copy
import time
from logging import Logger

from flatland.envs.rail_env import RailEnv, RailEnvActions
from flatland.utils.rendertools import RenderTool

from rasch.action import Action
from rasch.rasch_config import RaSchConfig, get_config


class RaSchSimulator:
    def __init__(self, *,
                 environment: RailEnv,
                 renderer: RenderTool,
                 logger: Logger,
                 config: RaSchConfig = get_config()) -> None:
        self.environment = environment
        self._config = config
        self._logger = logger
        self.renderer = renderer
        self.agents_at_step = {}

    def simulate_actions(self,
                         agent_actions: dict,
                         max_steps: int = 30,
                         step_delay: float = 0.5,
                         render: bool = False) -> None:
        # Set Flatland horizon,
        # this should be similar to the ASP horizon
        self.environment._max_episode_steps = max_steps

        step = 0
        agents_step = {}
        for id, actions in agent_actions.items():
            self._logger.debug(f"Agent {id} action count {len(actions)}")

        while not self.environment.dones["__all__"] and step < max_steps:
            actionsdict = {}
            self._logger.debug(f"Actions for step: {step}")
            for idx, agent in enumerate(self.environment.agents):
                if agent.position:
                    if not self.environment.dones[idx]:
                        if idx in agents_step:
                            agents_step[idx] += 1
                        else:
                            agents_step[idx] = 0
                        actionsdict[agent.handle] = agent_actions[idx][agents_step[idx]]
                else:
                    actionsdict[agent.handle] = RailEnvActions.MOVE_FORWARD

                if idx in agents_step:
                    self._logger.debug(
                        f"Agent({idx}) is at {agent.position} and chose {Action(actionsdict[agent.handle])} at step {agents_step[idx]}/{len(agent_actions[idx])-1}.")
                else:
                    self._logger.debug(
                        f"Agent({idx}) not spawned yet. {agent.state}")

            self.environment.step(actionsdict)

            self.agents_at_step[step] = copy.deepcopy(
                self.environment.agents)

            if render:
                self.renderer.render_env(
                    show=True, show_rowcols=True, show_observations=False)

                time.sleep(step_delay)
            step += 1
        # Show last frame
        if render:
            self.renderer.render_env(
                show=True, show_rowcols=True, show_observations=False)
