from playsound import playsound
import os

sound_path = r"www\assets\audio\start_sound.mp3"
print(f"Testing playsound with {sound_path}...")
try:
    playsound(sound_path)
    print("Sound played successfully.")
except Exception as e:
    print(f"Error playing sound: {e}")
