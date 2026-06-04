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

command_frames = []
record_until=0
is_recording_command = False
wake_detection_cooldown = 0
wake_latched = False
recording_started_at = 0
last_speech_time = 0
silence_timeout = 2.0
min_record_time = 1.0
WAKE_THRESHOLD = 0.5
RESET_THRESHOLD = 0.2

owwModel = Model(["hey_jarvis"])
audio_queue = queue.Queue()
aiclient = chatgptclient()
api_client = ApiClient()

def is_speech(audio_int16, threshold = 500):
    rms = np.sqrt(
        np.mean(
            audio_int16.astype(np.float32) ** 2
        )
    )
    return rms > threshold

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
            if is_speech(audio_int16):
                last_speech_time = time.time()
            
            record_duration = time.time() - recording_started_at
            is_long_enough = record_duration > min_record_time
            is_silent_long_enough = (time.time() - last_speech_time) > silence_timeout

            if is_long_enough and is_silent_long_enough:
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

                recording_started_at = time.time()
                last_speech_time = time.time()
                break