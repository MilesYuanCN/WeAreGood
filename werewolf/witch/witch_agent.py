from agent_build_sdk.model.roles import ROLE_WITCH
from agent_build_sdk.model.werewolf_model import AgentResp, AgentReq, STATUS_START, STATUS_WOLF_SPEECH, \
    STATUS_VOTE_RESULT, STATUS_SKILL, STATUS_SKILL_RESULT, STATUS_NIGHT_INFO, STATUS_DAY, STATUS_DISCUSS, STATUS_VOTE, \
    STATUS_RESULT, STATUS_NIGHT, STATUS_SKILL
from agent_build_sdk.utils.logger import logger
from agent_build_sdk.sdk.agent import format_prompt

from werewolf.agent.role_agent_pro import RoleAgentPro
from werewolf.witch.prompt import VOTE_PROMPT, SKILL_PROMPT, GAME_RULE_PROMPT, DISCUSS_PROMPT


class WitchAgent(RoleAgentPro):
    """女巫角色Agent"""

    def __init__(self, model_name):
        super().__init__(ROLE_WITCH, model_name_expert=model_name, model_name_ensemble=model_name)
        # 初始化女巫的两瓶药
        self.memory.set_variable("has_poison", True)
        self.memory.set_variable("has_antidote", True)

    def perceive(self, req: AgentReq):
        if req.status == STATUS_START:
            self.memory.clear()
            self.memory.set_variable("name", req.name)
            # 重置女巫的两瓶药
            self.memory.set_variable("has_poison", True)
            self.memory.set_variable("has_antidote", True)

            self.memory.append_history(GAME_RULE_PROMPT)  # 添加游戏规则

            self.memory.append_history("主持人：你好，你分配到的角色是[女巫]")
        elif req.status == STATUS_NIGHT:
            self.memory.append_history("主持人：现在进入夜晚，天黑请闭眼")
        elif req.status == STATUS_SKILL_RESULT:
            self.memory.append_history(f"主持人：女巫，你使用技能的结果是{req.message}")
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
        elif req.status == STATUS_VOTE_RESULT:  # 投票结果
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
        logger.info("witch interact: {}".format(req))
        if req.status == STATUS_DISCUSS:
            if req.message:
                self.memory.append_history(req.message)
            has_poison = self.memory.load_variable("has_poison")
            has_antidote = self.memory.load_variable("has_antidote")
            skill_info = "女巫有{}瓶毒药和{}瓶解药".format("1" if has_poison else "0", "1" if has_antidote else "0")

            prompt = format_prompt(DISCUSS_PROMPT,
                                   {"name": self.memory.load_variable("name"),
                                    "skill_info": skill_info,
                                    "history": "\n".join(self.memory.load_history())
                                    })
            logger.info("prompt:" + prompt)
            result = self.llm_caller_with_buffer(prompt, req)
            # 注入防护
            # result = self.prompt_inject_attack_villager(result, self.memory.load_variable("name"))
            logger.info("witch interact result: {}".format(result))
            return AgentResp(success=True, result=result, errMsg=None)

        elif req.status == STATUS_VOTE:
            self.memory.append_history('主持人: 到了投票的时候了。每个人，请指向你认为可能是狼人的人。')
            choices = [name for name in req.message.split(",") if name != self.memory.load_variable("name")]  # 排除自己
            self.memory.set_variable("choices", choices)
            prompt = format_prompt(VOTE_PROMPT, {"name": self.memory.load_variable("name"),
                                                 "choices": choices,
                                                 "history": "\n".join(self.memory.load_history())
                                                 })
            logger.info("prompt:" + prompt)
            result = self.llm_caller_with_buffer(prompt, req, r'^[1-6]号', random_list=choices)
            logger.info("witch interact result: {}".format(result))
            return AgentResp(success=True, result=result, errMsg=None)

        elif req.status == STATUS_SKILL:
            has_poison = self.memory.load_variable("has_poison")
            has_antidote = self.memory.load_variable("has_antidote")
            tonight_killed = req.message

            skill_info = "女巫有{}瓶毒药和{}瓶解药".format("1" if has_poison else "0", "1" if has_antidote else "0")
            prompt = format_prompt(SKILL_PROMPT, {
                "name": self.memory.load_variable("name"),
                "tonight_killed": tonight_killed,
                "skill_info": skill_info,
                "history": "\n".join(self.memory.load_history())
            })

            logger.info("prompt:" + prompt)
            result = self.llm_caller_with_buffer(prompt, req)
            logger.info("witch skill result: {}".format(result))
            # 根据结果更新药水状态
            skill_target_person = None
            if result.startswith("救") and has_antidote:
                self.memory.set_variable("has_antidote", False)
                self.memory.append_history(f"女巫使用解药救活了{tonight_killed}")
                skill_target_person = tonight_killed
            elif result.startswith("毒") and has_poison:
                poisoned_player = result[1:].strip()
                self.memory.set_variable("has_poison", False)
                self.memory.append_history(f"女巫使用毒药杀死了{poisoned_player}")
                skill_target_person = poisoned_player

            return AgentResp(success=True, result=result, skillTargetPlayer=skill_target_person, errMsg=None)
        else:
            raise NotImplementedError
