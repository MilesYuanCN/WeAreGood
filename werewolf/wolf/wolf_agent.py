from agent_build_sdk.model.roles import ROLE_WOLF
from agent_build_sdk.model.werewolf_model import AgentResp, AgentReq, STATUS_START, STATUS_WOLF_SPEECH, \
    STATUS_VOTE_RESULT, STATUS_SKILL, STATUS_SKILL_RESULT, STATUS_NIGHT_INFO, STATUS_DAY, STATUS_DISCUSS, STATUS_VOTE, \
    STATUS_RESULT, STATUS_NIGHT, STATUS_SKILL
from agent_build_sdk.utils.logger import logger
from agent_build_sdk.sdk.agent import format_prompt
from langchain import PromptTemplate

from werewolf.wolf.prompt import VOTE_PROMPT, KILL_PROMPT, WOLF_SPEECH_PROMPT, GAME_RULE_PROMPT, DISCUSS_PROMPT

from werewolf.agent.role_agent_pro import RoleAgentPro


class WolfAgent(RoleAgentPro):
    """狼人角色Agent"""

    def __init__(self, model_name_expert, model_name_ensemble):
        super().__init__(ROLE_WOLF, model_name_expert=model_name_expert, model_name_ensemble=model_name_ensemble)
        self.memory.set_variable("teammates", [])  # 存储队友信息

    def perceive(self, req: AgentReq):
        if req.status == STATUS_START:
            self.memory.clear()
            self.memory.set_variable("name", req.name)
            self.memory.set_variable("teammates", [])  # 重置队友信息

            self.memory.append_history(GAME_RULE_PROMPT)    # 添加游戏规则

            self.memory.append_history("主持人：你好，你分配到的角色是[狼人]")
            if req.message:  # 如果有队友信息
                teammates = req.message.split(",")
                self.memory.set_variable("teammates", teammates)
                self.memory.append_history(f"主持人：你的狼人队友是: {req.message}")
        elif req.status == STATUS_NIGHT:
            self.memory.append_history("主持人：现在进入夜晚，天黑请闭眼")
        elif req.status == STATUS_WOLF_SPEECH:
            # 狼人之间的交流
            if req.name:
                self.memory.append_history(f"狼人{req.name}说: {req.message}")
            else:
                self.memory.append_history("主持人：狼人请睁眼，狼人请互相确认身份，并选择要击杀的对象")
        elif req.status == STATUS_SKILL_RESULT:
            self.memory.append_history(f"主持人：狼人请今晚选择击杀的目标是:{req.name}")
        elif req.status == STATUS_NIGHT_INFO:
            self.memory.append_history(f"主持人：天亮了！昨天晚上的信息是: {req.message}")

        # 发言环节
        elif req.status == STATUS_DISCUSS:
            if req.name:
                # 其他玩家发言
                self.memory.append_history(req.message, tag=req.name)
            else:
                # 主持人发言
                self.memory.append_history(f'主持人: 现在进入第{str(req.round)}天。')
                self.memory.append_history('主持人: 每个玩家描述自己的信息。')

        # 投票环节
        elif req.status == STATUS_VOTE:
            self.memory.append_history(f'第{req.round}天的投票环节,{req.name} 投了 {req.message}')
        elif req.status == STATUS_VOTE_RESULT:  # 投票环节
            out_player = req.name if req.name else req.message
            if out_player:
                self.memory.append_history(f'主持人: 投票结果是：{out_player}。')
            else:
                self.memory.append_history('主持人: 无人出局。')
        elif req.status == STATUS_RESULT:
            self.memory.append_history(req.message)
        else:
            raise NotImplementedError

    def interact(self, req: AgentReq) -> AgentResp:
        logger.info("wolf interact: {}".format(req))

        if req.status == STATUS_DISCUSS:
            if req.message:
                self.memory.append_history(req.message)
            teammates = self.memory.load_variable("teammates")

            expert_prompt = DISCUSS_PROMPT

            expert_prompt = PromptTemplate(template=expert_prompt, input_variables=['name', 'teammates', 'history'])\
                .format(
                **{"name": self.memory.load_variable("name"),
                   "teammates": teammates,
                   "history": "\n".join(self.memory.load_history())
                }
            )
            # expert_prompt_list = [expert_prompt] * 3
            #
            # ensemble_prompt = PromptTemplate(template=ensemble_prompt, input_variables=['name', 'teammates', 'history'])\
            #     .format(
            #     **{"name": self.memory.load_variable("name"),
            #        "teammates": teammates,
            #        "history": "\n".join(self.memory.load_history())
            #     }
            # )
            #
            # result = self.moe_caller(expert_prompt_list, ensemble_prompt)

            result = self.llm_caller_with_buffer(expert_prompt, req)
            # result = self.prompt_inject_attack_wolf(result, self.memory.load_variable("name"))
            logger.info("wolf interact result: {}".format(result))
            return AgentResp(success=True, result=result, errMsg=None)

        elif req.status == STATUS_VOTE:
            self.memory.append_history('主持人: 到了投票的时候了。每个人，请指向你认为可能是狼人的人。')
            teammates = self.memory.load_variable("teammates")
            choices = [name for name in req.message.split(",") 
                      if name != self.memory.load_variable("name") and name not in teammates]  # 排除自己和队友
            self.memory.set_variable("choices", choices)
            prompt = format_prompt(VOTE_PROMPT, {"name": self.memory.load_variable("name"),
                                               "teammates": teammates,
                                               "choices": choices,
                                               "history": "\n".join(self.memory.load_history())
                                              })
            logger.info("prompt:" + prompt)
            result = self.llm_caller_with_buffer(prompt, req, r'^[1-6]号')
            logger.info("wolf interact result: {}".format(result))
            return AgentResp(success=True, result=result, errMsg=None)
            
        elif req.status == STATUS_WOLF_SPEECH:
            teammates = self.memory.load_variable("teammates")
            prompt = format_prompt(WOLF_SPEECH_PROMPT, {
                "name": self.memory.load_variable("name"),
                "teammates": teammates,
                "history": "\n".join(self.memory.load_history())
            })
            logger.info("prompt:" + prompt)
            result = self.llm_caller_with_buffer(prompt, req)
            logger.info("wolf speech result: {}".format(result))
            return AgentResp(success=True, result=result, errMsg=None)
            
        elif req.status == STATUS_SKILL:
            teammates = self.memory.load_variable("teammates")
            choices = [name for name in req.message.split(",") 
                      if name != self.memory.load_variable("name") and name not in teammates]  # 排除自己和队友
            self.memory.set_variable("choices", choices)
            prompt = format_prompt(KILL_PROMPT, {
                "name": self.memory.load_variable("name"),
                "choices": choices,
                "history": "\n".join(self.memory.load_history())
            })
            logger.info("prompt:" + prompt)
            result = self.llm_caller_with_buffer(prompt, req, r'^[1-6]号', random_list=choices)
            logger.info("wolf kill result: {}".format(result))
            return AgentResp(success=True, result=result, skillTargetPlayer=result, errMsg=None)
        else:
            raise NotImplementedError