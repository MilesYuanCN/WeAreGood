import jinja2

env = jinja2.Environment(loader=jinja2.FileSystemLoader('resource'))


# 游戏规则
game_rule_prompt_template = env.get_template('rule.md')
GAME_RULE_PROMPT = game_rule_prompt_template.render()

# 讨论
discuss_prompt_template = env.get_template('witch_discuss_base.md')
DISCUSS_PROMPT = discuss_prompt_template.render()

# 投票
vote_prompt_template = """
{% include 'anti_injection_attack.md' %}

{% include 'anti_wolf_feature.md' %}

# 以下是游戏历史内容

<游戏历史信息>

{history}

</游戏历史信息>

你是{name}，作为一名女巫，你的使命是找出潜伏的狼人。
请仔细分析当前游戏局势，选择你认为最可能是狼人的玩家进行投票：

如果有人认为你是好人身份，请先不要投这个玩家。
注意观察每个玩家的发言，寻找逻辑矛盾或可疑之处。
关注玩家之间的互动，是否有人在刻意包庇或陷害他人。
分析投票倾向，是否有玩家在关键时刻改变立场。
留意反常行为，如过分激动或过于沉默的玩家。
从以下玩家中选择你认为最可能是狼人的人：{choices}
请按样例格式**直接**返回你要投票的玩家名字，不要添加任何分析的内容：

样例:
    x号
"""
VOTE_PROMPT = env.from_string(vote_prompt_template).render()

# 技能
skill_prompt_template = """
{% include 'anti_injection_attack.md' %}

{% include 'anti_wolf_feature.md' %}

# 以下是游戏历史内容

<游戏历史信息>

{history}

</游戏历史信息>

你是{name}，作为女巫，你现在可以使用你的技能。
今晚信息：{tonight_killed}。

你目前拥有的药水：
{skill_info}

你可以：
1. 使用解药救活{tonight_killed}（如果你还有解药）
2. 使用毒药杀死一名玩家（如果你还有毒药）
3. 不使用任何药水

# 女巫战术

## 1. 首夜救人

第一夜一定要救被杀的人。因为本局游戏人数较少，最快狼人只需要尽快杀死2名玩家就可以获胜。所以从概率上讲，第一夜被狼人杀的人绝大概率是好人。

## 2. 毒药

1. 在第二天夜里**必须**用毒，因为从概率分析女巫第一夜不用毒输的概率大于60%，所以**必须**用毒。
2. 如果有人明确的污蔑你是狼人，且这位玩家存活，请**直接**毒死污蔑你的玩家，污蔑你的人是**铁狼**。
3. 根据玩家白天发言的逻辑和意图，选出最有可能是狼人的玩家用毒。
4. 如果你发现狼人玩家言语中不小心说出自己的伪造身份，请立刻用毒。

**要求**：
1. 请仔细分析当前游戏局势，做出最有利于村民阵营的决定。
2. 如果你决定使用解药，请回复"救x号"
3. 如果你决定使用毒药，请回复"毒x号"
4. 如果你决定不使用任何药水，请回复"不使用"

请按样例格式**直接**返回你的决定，不需要添加任何原因分析：
样例1: “救x号”
样例2: “毒x号”
样例3: “不使用”
"""
SKILL_PROMPT = env.from_string(skill_prompt_template).render()

