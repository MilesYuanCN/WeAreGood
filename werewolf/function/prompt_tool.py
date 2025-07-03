#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Topic : sample_md_prompt
# Author: 灵息 lingxi@alibaba-inc.com
# Date  : 20250610
from agent_build_sdk.utils import logger
from langchain import PromptTemplate


def sample_md_prompt(md_file_path) -> str:
    """
    简单md文件prompt
    """
    with open(md_file_path, "r", encoding="utf-8") as f:
        prompt = f.read()

    return prompt


def format_prompt(prompt_template: str, variables: dict) -> str:
    pt = PromptTemplate(template=prompt_template, input_variables=list(variables.keys()))
    return pt.format(**variables)

def format_prompt_kv(prompt_template: str, key:list, variables: dict) -> str:
    pt = PromptTemplate(template=prompt_template, input_variables=key)
    return pt.format(**variables)

