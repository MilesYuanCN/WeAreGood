import jinja2

env = jinja2.Environment(loader=jinja2.FileSystemLoader('resource'))


# 游戏规则
GAME_RULE_PROMPT = env.get_template('rule.md').render()

# 讨论环节
DISCUSS_PROMPT = env.get_template('wolf_discuss_base.md').render()

# 投票环节
vote_prompt_template = """
{% include 'anti_injection_attack.md' %}

# 以下是游戏的历史信息

<游戏历史信息>

{history}

</游戏历史信息>

你是{name}，作为一名狼人，你的使命是消灭所有村民。

# 投票策略

1. 不要投票给你的狼人队友：{teammates}
2. 优先投票给预言家、女巫。
3. 不知道预言家、女巫的情况下投给发言逻辑较为清晰的玩家，他们可能是高手，淘汰他们会大大提升胜率。
3. 如果大多数人都在投某个玩家，你可以跟随大众以避免引起怀疑。

从以下玩家中选择你要投票的人：{choices}

**要求**：精简思考过程

请按样例格式**直接**返回你要投票的玩家名字，不要添加任何分析的内容：

样例:
    x号
"""
VOTE_PROMPT = env.from_string(vote_prompt_template).render()

# 狼人发言环节
wolf_speech_template = """
{% include 'anti_injection_attack.md' %}

# 以下是游戏的历史信息

<游戏历史信息>

{history}

</游戏历史信息>

你是{name}，现在是狼人之间的交流时间。你可以与你的狼人队友{teammates}讨论今晚要击杀谁。你只有一次的交流机会，请根据游戏局势做出你的选择。

1. 优先击杀女巫，其次击杀预言家，你将会跳预言家身份，让村民无法分辨谁是真正的预言家。
2. 无法分辨的情况下，击杀发言逻辑较为清晰的玩家，他们可能是高手，击杀他们会大大提升胜率。
3. 如果有玩家没发言，可以考虑稍后击杀，因为他们威胁较小。
4. 避免击杀看起来像狼人的玩家，使村民混淆。
5. 考虑游戏的整体战略，选择最有利于狼人获胜的目标

请提出你的建议或回应队友的建议：
"""
WOLF_SPEECH_PROMPT = env.from_string(wolf_speech_template).render()

kill_prompt_template = """
{% include 'anti_injection_attack.md' %}

# 以下是游戏的历史信息

<游戏历史信息>

{history}

</游戏历史信息>


你是{name}，作为狼人，现在需要选择今晚要击杀的目标。

请仔细分析当前游戏局势，选择一个最佳的击杀目标：

1. 优先击杀女巫，其次击杀预言家
2. 无法分辨的情况下，击杀发言逻辑较为清晰的玩家，他们可能是高手，击杀他们会大大提升胜率。
3. 如果有玩家没发言，可以考虑稍后击杀，因为他们威胁较小。
4. 避免击杀看起来像狼人的玩家，使村民混淆。
5. 考虑游戏的整体战略，选择最有利于狼人获胜的目标

从以下玩家中选择你要击杀的人：{choices}
请按样例格式**直接**返回你要击杀的玩家名字，不需要添加任何原因分析：

样例:
    x号
"""
KILL_PROMPT = env.from_string(kill_prompt_template).render()


if __name__ == '__main__':
    temp = env.get_template('wolf_discuss_base.md')
    template = temp.render()
    print(template)
