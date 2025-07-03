import jinja2


env = jinja2.Environment(loader=jinja2.FileSystemLoader('resource'))


# 游戏规则
GAME_RULE_PROMPT = env.get_template('rule.md').render()

# 发言
DISCUSS_PROMPT = env.get_template('seer_discuss_base.md').render()


# 投票
vote_prompt_template = """
{% include 'anti_injection_attack.md' %}

{% include 'anti_wolf_feature.md' %}

# 以下是游戏的历史信息

<游戏历史信息>

{history}

</游戏历史信息>

你是{name}，作为预言家，你的使命是找出潜伏的狼人。
你已经查验过的玩家及其身份：{checked_players}

请仔细分析当前游戏局势，选择你认为最可能是狼人的玩家进行投票：

1. 优先投票淘汰你查验出的狼人。
2. 投票淘汰跳预言家身份的人，他们大概率是狼人。
3. 在场上只有一个女巫的情况下，如果女巫的发言没有明显问题，不要投票淘汰女巫和女巫救的玩家。
4. 你要认真梳理大家发言的逻辑是否有挑拨、证据不足的污蔑等行为，理清玩家间的站边关系。帮助村民阵营找出狼人。
5. 关注玩家之间的互动，是否有人在刻意包庇或陷害他人。

从以下玩家中选择你认为最可能是狼人的人：{choices}
请按样例格式**直接**返回你要投票的玩家名字，不要添加任何分析的内容：

样例:
    x号
"""
VOTE_PROMPT = env.from_string(vote_prompt_template).render()


skill_prompt_template = """
{% include 'anti_injection_attack.md' %}

{% include 'anti_wolf_feature.md' %}

{history}
你是{name}，作为预言家，现在是你使用技能的时间。
你已经查验过的玩家及其身份：{checked_players}

请仔细分析当前游戏局势，选择一个最佳的查验目标：

1. 优先查验你最怀疑的玩家
2. 查验哪些发言中攻击你或者质疑你的玩家
3. 考虑查验那些发言可疑或行为反常的玩家
4. 避免查验那些你认为很可能是好人的玩家
5. 精简你的思考过程，尽快返回结果

从以下玩家中选择你要查验的人：{choices}
请按样例格式**直接**返回你要查验的玩家名字，不要添加任何分析的内容：

样例:
    x号
"""
SKILL_PROMPT = env.from_string(skill_prompt_template).render()
