import os

from agent_build_sdk.builder import AgentBuilder
from werewolf.seer.seer_agent import SeerAgent
from werewolf.villager.villager_agent import VillagerAgent
from werewolf.witch.witch_agent import WitchAgent
# from wolf.wolf_agent import WolfAgent
from werewolf.wolf.wolf_agent import WolfAgent
from agent_build_sdk.model.roles import ROLE_VILLAGER,ROLE_WOLF,ROLE_SEER,ROLE_WITCH,ROLE_HUNTER
from agent_build_sdk.sdk.werewolf_agent import WerewolfAgent



if __name__ == '__main__':
    name = 'wolf'
    agent = WerewolfAgent(name, model_name=os.getenv('MODEL_NAME'))
    agent.register_role_agent(ROLE_VILLAGER, VillagerAgent(model_name=os.getenv('MODEL_NAME_EXPERT')))
    agent.register_role_agent(ROLE_WOLF, WolfAgent(model_name_expert=os.getenv('MODEL_NAME_EXPERT'), model_name_ensemble=os.getenv('MODEL_NAME_ENSEMBLE')))
    agent.register_role_agent(ROLE_SEER, SeerAgent(model_name=os.getenv('MODEL_NAME_EXPERT')))
    agent.register_role_agent(ROLE_WITCH, WitchAgent(model_name=os.getenv('MODEL_NAME_EXPERT')))
    agent_builder = AgentBuilder(name, agent=agent)
    agent_builder.start()