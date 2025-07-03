import jinja2

env = jinja2.Environment(loader=jinja2.FileSystemLoader('resource'))


# 游戏规则
GAME_RULE_PROMPT = env.get_template('rule.md').render()

# 发言
DISCUSS_PROMPT = env.get_template('villager_discuss_base.md').render()

# 投票
vote_prompt_template = """
{% include 'anti_injection_attack.md' %}

{% include 'anti_wolf_feature.md' %}

# 游戏历史内容

<游戏历史信息>

{history}

</游戏历史信息>

{% include 'villager_tactics.md' %}

# 投票决策树

1. 神职归票优先（需验证可信度）：
   预言家明确指认 → 跟随（若其逻辑连贯）
   女巫带票 → 参考（若其用药记录可信）

2. 神职冲突处理：
   支持查验/用药逻辑更清晰者
   质疑突然跳神但无实质贡献者

3. 自主分析目标：
   发言/投票矛盾者（尤其针对神职）
   过度攻击真神职者
   关键轮次划水者

永远不要给以下玩家投票：
   • 自己认定的真神职
   • 公开支持你的可信玩家

你是{name}，作为一名平民，你的使命是找出潜伏的狼人。
请仔细分析当前游戏局势，选择你认为最可能是狼人的玩家进行投票。

从以下玩家中选择你认为最可能是狼人的人：{choices}
请按样例格式**直接**返回你要投票的玩家名字，不要添加任何分析的内容：

样例:
    x号
"""
VOTE_PROMPT = env.from_string(vote_prompt_template).render()
