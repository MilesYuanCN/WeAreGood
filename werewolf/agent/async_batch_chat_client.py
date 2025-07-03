#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Topic : batch_chat_creator
# Author: 灵息 lingxi@alibaba-inc.com
# Date  : 20250610
import asyncio
from typing import Union

import httpx
import logging


class AsyncBatchChatClient:
    logger = logging.getLogger(__name__)
    """本地批量提交prompt"""
    def __init__(self, access_key, model: str = 'deepseek-r1-0528',
                 base_url: str = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
                 temperature: float = 0.0,
                 is_stream_response: bool = False,
                 extra_params: dict = None,
                 max_concurrency=10):

        self.access_key = access_key
        self.model: str = model
        self.base_url: str = base_url

        self.temperature: float = temperature
        self.is_stream_response: bool = is_stream_response
        self.extra_params: dict = extra_params
        self.max_concurrency: int = max_concurrency



    def complete(self, prompt_list: list, system_prompt: Union[str, list, None]=None, timeout=180):

        system_prompt_list = [None] * len(prompt_list)
        if type(system_prompt) is str:
            system_prompt_list = [system_prompt for _ in range(len(prompt_list))]
        elif type(system_prompt) is list:
            system_prompt_list = [system_prompt[i] if i < len(system_prompt) else None for i in range(len(prompt_list))]

        res = asyncio.run(self._complete_all(prompt_list, system_prompt_list, timeout))
        return res

    async def _complete_one(self, client: httpx.AsyncClient, async_id: int,
                            prompt: str, system_prompt: str,
                            semaphore: asyncio.Semaphore, timeout: int):
        """
        异步请求
        """
        self.logger.info(f'Start completion: {async_id}.')
        async with semaphore:
            try:
                headers = {
                    'Authorization': 'Bearer ' + self.access_key,
                    'Content-Type': 'application/json'
                }

                messages = []
                if system_prompt:
                    messages.append({
                            'role': 'system',
                            'content': f'{system_prompt}'
                        })

                messages.append({
                            'role': 'user',
                            'content': f'{prompt}'
                        })

                payload = {
                    'model': self.model,
                    'messages': messages
                }

                if self.extra_params is not None:
                    payload.update(self.extra_params)

                response = await client.post(self.base_url, headers=headers, json=payload, timeout=timeout)
                return response

            except Exception as e:
                self.logger.error(f'{e}')
                return None


    async def _complete_all(self, prompt_list: list, system_prompt_list: list, timeout):
        semaphore = asyncio.Semaphore(self.max_concurrency)
        async with httpx.AsyncClient() as client:
            tasks = [
                self._complete_one(client=client, async_id=i, prompt=prompt_list[i], system_prompt=system_prompt_list[i],
                                   semaphore=semaphore, timeout=timeout)
                for i in range(len(prompt_list))
            ]

            results = await asyncio.gather(*tasks)

        return results

    def decode_openai_response(self, response: httpx.Response):
        if response.status_code == 200:
            res_body = response.json()
            content = res_body['choices'][0]['message']['content']
            return content

        else:
            self.logger.error(f'Status code: {response.status_code}')
            self.logger.error(f'Response body: {response.text}')
            return None


if __name__ == '__main__':
    agent = AsyncBatchChatClient(access_key='')
    p_list = [''] * 2
    print(p_list)

    res_list = agent.complete(p_list)
    for res in res_list:
        print(agent.decode_openai_response(res))



