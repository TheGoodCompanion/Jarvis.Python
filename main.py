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
audio_queue = queue.Queue()
command_frames = []
record_until=0
is_recording_command = False
wake_detection_cooldown = 0
owwModel = Model(["hey_jarvis"])
wake_latched = False
WAKE_THRESHOLD = 0.5
RESET_THRESHOLD = 0.2
aiclient = chatgptclient()
api_client = ApiClient()

async def play_beep():
    await asyncio.to_thread(playsound, "Beep.mp3")

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata[:, 0].copy())

with sd.InputStream(
    channels=1,
    samplerate=RATE,
    blocksize=FRAME_SIZE,
    dtype="float32",
    callback=audio_callback
):
    print("Listenting for wake work")
    while True:
        audio_float = audio_queue.get()
        audio_int16 = (audio_float * 32767).astype(np.int16)

        if is_recording_command:
            command_frames.append(audio_int16)
            if time.time() >= record_until:
                is_recording_command = False
                command_audio = np.concatenate(command_frames)

                command_frames = []
                print("Finished Recording")
                sf.write("command.wav", command_audio, RATE)
                text = aiclient.speech_to_text()
                ai_response = aiclient.get_response(text)
                asyncio.run(api_client.handle_command(ai_response, aiclient))
                wake_detection_cooldown = time.time() + 2
            continue

        prediction = owwModel.predict(audio_int16)
        max_score = max(prediction.values()) if prediction else 0

        if wake_latched:
            if max_score < RESET_THRESHOLD:
                wake_latched = False
            continue

        if time.time() < wake_detection_cooldown:
            continue
        for wakeword, score in prediction.items():
            if score > WAKE_THRESHOLD:
                wake_latched = True
                asyncio.run(play_beep())
                is_recording_command = True
                command_frames = []
                record_until = time.time() + 5
                break