import asyncio
import httpx
import json

class ApiClient:
    def __init__(self):
        self.blah = ""

    async def parse_chatgpt_response(self, actions):
        for action in actions:
            endpoint = action["apiendpoint"]
            parameters = action["parameters"]
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.post(
                    endpoint,
                    json=parameters
                )
                print(response.json())

    async def handle_command(self, command_json, aiclient):
        command = json.loads(command_json)
        actions = command["actions"]
        vocal_response = command["response"]
        await asyncio.gather(
            self.parse_chatgpt_response(actions),
            aiclient.generate_and_play_tts(vocal_response)
        )
        aiclient.context = command["context"]