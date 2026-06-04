import asyncio
import httpx
import json

class ApiClient:
    def __init__(self):
        self.returned_data = []
        self.send_another_request = False
        self.follow_up_depth = 0
        self.max_follow_up_depth = 3
        self.on_response_recieved = None
        self.on_context_changed = None

    def emit_vocal_response(self, text):
        if self.on_response_recieved:
            self.on_response_recieved(text)
    
    def emit_context(self, context):
        if self.on_context_changed:
            self.on_context_changed(context)

    async def parse_chatgpt_response(self, actions):
        for action in actions:
            endpoint = action["apiendpoint"]
            parameters = action["parameters"]
            store_response = action["store_response"]
            if store_response:
                self.send_another_request = True
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.post(
                    endpoint,
                    json=parameters,
                    timeout=15
                )
                self.returned_data.append(response.text)

    async def follow_up_request(self, aiclient):
        airesponse = aiclient.get_response("This is a follow-up request you should have all you need within the context.")
        await self.handle_command(airesponse, aiclient)

    async def handle_command(self, command_json, aiclient):
        command = json.loads(command_json)
        actions = command["actions"]
        vocal_response = command["response"]
        self.emit_vocal_response(vocal_response)
        await asyncio.gather(
            self.parse_chatgpt_response(actions),
            aiclient.generate_and_play_tts(vocal_response)
        )
        aiclient.context = command["context"] + ' - '.join(self.returned_data)
        self.emit_context(aiclient.context)
        if self.send_another_request and self.follow_up_depth <= self.max_follow_up_depth:
            self.send_another_request = False
            self.follow_up_depth += 1 
            await self.follow_up_request(aiclient)
        else:
            self.follow_up_depth = 0
            self.returned_data = []

    