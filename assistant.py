import sounddevice as sd
import soundfile as sf
import queue
import time
import numpy as np
from openwakeword.model import Model
from chatgptclient import chatgptclient
import urllib3
from playsound import playsound
import asyncio
from api_client import ApiClient
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Get microphone stream
FRAME_SIZE = 1280
RATE = 16000


class JarvisAssistant:
    def __init__(self):
        self.command_frames = []
        self.record_until=0
        self.is_recording_command = False
        self.wake_detection_cooldown = 0
        self.wake_latched = False
        self.recording_started_at = 0
        self.last_speech_time = 0
        self.silence_timeout = 2.0
        self.min_record_time = 1.0
        self.WAKE_THRESHOLD = 0.5
        self.RESET_THRESHOLD = 0.2

        self.owwModel = Model(["hey_jarvis"])
        self.audio_queue = queue.Queue()
        self.aiclient = chatgptclient()
        self.api_client = ApiClient()
        self.api_client.on_response_recieved = self.emit_response
        self.api_client.on_context_changed = self.emit_context

        self.on_status_changed = None
        self.on_transcript = None
        self.on_response = None
        self.on_action = None
        self.on_context_changed = None

    def emit_status(self, status):
        print(status)
        if self.on_status_changed:
            self.on_status_changed(status)
    
    def emit_transcript(self, transcipt):
        print(transcipt)
        if self.on_transcript:
            self.on_transcript(transcipt)
    
    def emit_response(self, response):
        print(response)
        if self.on_response:
            self.on_response(response)
    
    def emit_context(self, context):
        if self.on_context_changed:
            self.on_context_changed(context)

    def is_speech(self, audio_int16, threshold = 500):
        rms = np.sqrt(
            np.mean(
                audio_int16.astype(np.float32) ** 2
            )
        )
        return rms > threshold

    async def play_beep(self):
        await asyncio.to_thread(playsound, "Beep.mp3")

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.audio_queue.put(indata[:, 0].copy())
    def run(self):
        self.emit_status("idle")

        with sd.InputStream(
            channels=1,
            samplerate=RATE,
            blocksize=FRAME_SIZE,
            dtype="float32",
            callback=self.audio_callback
        ):
            print("Listenting for wake work")
            while True:
                audio_float = self.audio_queue.get()
                audio_int16 = (audio_float * 32767).astype(np.int16)

                if self.is_recording_command:
                    self.handle_recording(audio_int16)
                    continue
            
                self.handle_wakeword(audio_int16)

    def handle_wakeword(self, audio_int16):
        prediction = self.owwModel.predict(audio_int16)
        max_score = max(prediction.values()) if prediction else 0

        if self.wake_latched:
            if max_score < self.RESET_THRESHOLD:
                self.wake_latched = False
            return

        if time.time() < self.wake_detection_cooldown:
            return
        for wakeword, score in prediction.items():
            if score > self.WAKE_THRESHOLD:
                self.wake_latched = True
                asyncio.run(self.play_beep())
                self.is_recording_command = True
                self.command_frames = []

                self.recording_started_at = time.time()
                self.last_speech_time = time.time()

                self.emit_status("listening")
                break

    def handle_recording(self, audio_int16):
        self.command_frames.append(audio_int16)
        if self.is_speech(audio_int16):
            self.last_speech_time = time.time()
        
        record_duration = time.time() - self.recording_started_at
        is_long_enough = record_duration > self.min_record_time
        is_silent_long_enough = (time.time() - self.last_speech_time) > self.silence_timeout

        if is_long_enough and is_silent_long_enough:
            self.is_recording_command = False
            self.emit_status("processing audio")
            asyncio.run(self.process_finished_command())


    async def process_finished_command(self):
            self.emit_status("thinking")

            command_audio = np.concatenate(self.command_frames)
            self.command_frames = []

            print("Finished Recording")

            sf.write("command.wav", command_audio, RATE)

            text = self.aiclient.speech_to_text()
            self.emit_transcript(text)

            ai_response = self.aiclient.get_response(text)

            await self.api_client.handle_command(ai_response, self.aiclient)
            
            self.wake_detection_cooldown = time.time() + 2

            self.emit_status("idle")