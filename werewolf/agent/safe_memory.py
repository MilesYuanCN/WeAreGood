#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Topic : safe_memory
# Author: 灵息 lingxi@alibaba-inc.com
# Date  : 20250612
from typing import Dict, Any, List


class SafeMemory:
    """Simple memory for storing context or other information that shouldn't
    ever change between prompts.
    """

    memories: Dict[str, Any] = dict()

    def load_variable(self, variable: str) -> Any:
        return self.memories[variable]

    def set_variable(self, variable: str, value: Any):
        self.memories[variable] = value

    def has_variable(self, variable: str):
        return variable in self.memories

    def append_history(self, message: str, tag: str = '主持人'):
        if self.has_variable("history"):
            history: List[str] = self.load_variable("history")
        else:
            history = []
        if message:
            message = self.anti_injection_tag(message, tag)
            history.append(message)

        self.set_variable("history", history)

    def load_history(self):
        if self.has_variable("history"):
            history: List[str] = self.load_variable("history")
        else:
            history = []
        return history

    def clear(self) -> None:
        """Nothing to clear, got a memory like a vault."""
        self.memories.clear()

    @staticmethod
    def anti_injection_tag(message: str, tag: str) -> str:
        return f'<{tag}>{message}</{tag}>'


if __name__ == '__main__':
    memory = SafeMemory()
    memory.set_variable('test', 'test')
    v = memory.load_variable('test')
    print(v)
