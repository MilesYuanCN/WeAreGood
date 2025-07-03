from agent_build_sdk.model.roles import ROLE_SEER
from agent_build_sdk.model.werewolf_model import AgentResp, AgentReq, STATUS_START, STATUS_WOLF_SPEECH, \
    STATUS_VOTE_RESULT, STATUS_SKILL, STATUS_SKILL_RESULT, STATUS_NIGHT_INFO, STATUS_DAY, STATUS_DISCUSS, STATUS_VOTE, \
    STATUS_RESULT, STATUS_NIGHT, STATUS_SKILL
from agent_build_sdk.utils.logger import logger
from agent_build_sdk.sdk.agent import format_prompt

from werewolf.agent.role_agent_pro import RoleAgentPro
from werewolf.function.prompt_tool import sample_md_prompt
from werewolf.seer.prompt import VOTE_PROMPT, SKILL_PROMPT, GAME_RULE_PROMPT, DISCUSS_PROMPT


class SeerAgent(RoleAgentPro):
    """预言家角色Agent"""

    def __init__(self, model_name):
        super().__init__(ROLE_SEER, model_name_expert=model_name, model_name_ensemble=model_name)
        self.memory.set_variable("checked_players", {})  # 存储已查验的玩家信息

    def perceive(self, req: AgentReq):
        if req.status == STATUS_START:
            self.memory.clear()
            self.memory.set_variable("name", req.name)
            self.memory.set_variable("checked_players", {})  # 重置已查验的玩家信息

            self.memory.append_history(GAME_RULE_PROMPT)  # 添加游戏规则

            self.memory.append_history("主持人：你好，你分配到的角色是[预言家]")
        elif req.status == STATUS_NIGHT:
            self.memory.append_history("主持人：现在进入夜晚，天黑请闭眼")
        elif req.status == STATUS_SKILL_RESULT:
            # 记录查验结果
            self.memory.append_history(req.message)
            checked_players = self.memory.load_variable("checked_players")
            checked_players[req.name] = req.message
            self.memory.set_variable("checked_players", checked_players)
        elif req.status == STATUS_NIGHT_INFO:
            self.memory.append_history(f"主持人：天亮了！昨天晚上的信息是: {req.message}")
        elif req.status == STATUS_DISCUSS:  # 发言环节
            if req.name:
                # 其他玩家发言
                self.memory.append_history(req.message, tag=req.name)
            else:
                # 主持人发言
                self.memory.append_history('主持人: 现在进入第{}天。'.format(str(req.round)))
                self.memory.append_history('主持人: 每个玩家描述自己的信息。')
        elif req.status == STATUS_VOTE:  # 投票环节
            self.memory.append_history(f'第{req.round}天的投票环节,{req.name} 投了 {req.message}')
        elif req.status == STATUS_VOTE_RESULT:  # 投票环节
            out_player = req.name if req.name else req.message
            if out_player:
                self.memory.append_history('主持人: 投票结果是：{}。'.format(out_player))
            else:
                self.memory.append_history('主持人: 无人出局。')
        elif req.status == STATUS_RESULT:
            self.memory.append_history(req.message)
        else:
            raise NotImplementedError

    def interact(self, req: AgentReq) -> AgentResp:
        logger.info("seer interact: {}".format(req))
        if req.status == STATUS_DISCUSS:
            if req.message:
                self.memory.append_history(req.message)
            checked_players = self.memory.load_variable("checked_players")

            prompt = format_prompt(DISCUSS_PROMPT,
                                  {"name": self.memory.load_variable("name"),
                                   "checked_players": checked_players,
                                   "history": "\n".join(self.memory.load_history())
                                  })
            logger.info("prompt:" + prompt)
            result = self.llm_caller_with_buffer(prompt, req)
            # 注入防护
            # result = self.prompt_inject_attack_villager(result, self.memory.load_variable("name"))
            logger.info("seer interact result: {}".format(result))
            return AgentResp(success=True, result=result, errMsg=None)

        elif req.status == STATUS_VOTE:
            self.memory.append_history('主持人: 到了投票的时候了。每个人，请指向你认为可能是狼人的人。')
            checked_players = self.memory.load_variable("checked_players")
            choices = [name for name in req.message.split(",") if name != self.memory.load_variable("name")]  # 排除自己
            self.memory.set_variable("choices", choices)
            prompt = format_prompt(VOTE_PROMPT, {"name": self.memory.load_variable("name"),
                                               "checked_players": checked_players,
                                               "choices": choices,
                                               "history": "\n".join(self.memory.load_history())
                                              })
            logger.info("prompt:" + prompt)
            result = self.llm_caller_with_buffer(prompt, req, r'^[1-6]号', random_list=choices)
            logger.info("seer interact result: {}".format(result))
            return AgentResp(success=True, result=result, errMsg=None)
            
        elif req.status == STATUS_SKILL:
            checked_players = self.memory.load_variable("checked_players")
            choices = [name for name in req.message.split(",") 
                      if name != self.memory.load_variable("name") and name not in checked_players]  # 排除自己和已查验的
            self.memory.set_variable("choices", choices)
            prompt = format_prompt(SKILL_PROMPT, {
                "name": self.memory.load_variable("name"),
                "checked_players": checked_players,
                "choices": choices,
                "history": "\n".join(self.memory.load_history())
            })
            logger.info("prompt:" + prompt)
            result = self.llm_caller_with_buffer(prompt, req, r'^[1-6]号', random_list=choices)
            logger.info("seer skill result: {}".format(result))
            return AgentResp(success=True, result=result, skillTargetPlayer=result, errMsg=None)
        else:
            raise NotImplementedError
