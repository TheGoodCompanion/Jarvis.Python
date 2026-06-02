from openai import OpenAI
import os
import prompts
import base64
from pathlib import Path
import uuid
from faster_whisper import WhisperModel
import asyncio
from playsound import playsound

class chatgptclient:
    def __init__(self):
        self.client = client = OpenAI(
            api_key=os.environ["OPENAI_API_KEY_TWITCH"]
        )
        self.whisper_model = WhisperModel(
            "base.en",
            device="cpu",
            compute_type="int8"
        )
        self.context = ""

    def get_response(self, command):
        completion = self.client.chat.completions.create(
            model="gpt-5.5",
            messages= prompts.return_full_prompt(f"{command}. Context: {self.context}")
        )
        return completion.choices[0].message.content
    
    def openai_tts(self, text):
        with self.client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="coral",
            input=text,
            instructions="You have a recieved pronunciation english accent and you are mimicing the way Jarvis from Iron Man speaks.",
        ) as response:
            filename = f"speech_{uuid.uuid4()}.mp3"
            self.speech_file_path = Path(__file__).parent / filename
            response.stream_to_file(self.speech_file_path)
            return filename
        
    def speech_to_text(self, file_path="command.wav"):
        segments, info = self.whisper_model.transcribe(
            file_path,
            language="en",
            beam_size=5,
            vad_filter=True
        )

        text = " ".join(segment.text.strip() for segment in segments).strip()

        print(text)
        return text
    
    async def generate_and_play_tts(self, vocal_response):
        print(vocal_response)
        filename = await asyncio.to_thread(self.openai_tts, vocal_response)
        await asyncio.to_thread(playsound, filename)