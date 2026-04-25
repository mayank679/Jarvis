import eel
import json
import os
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

SETTINGS_FILE = "engine/settings.json"

def get_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {"voice_rate": 174, "voice_index": 0}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

@eel.expose
def set_system_volume(level):
    try:
        level = float(level)
        devices = AudioUtilities.GetSpeakers()
        volume = devices.EndpointVolume
        
        # level is 0 to 100, we map it to scalar (0.0 to 1.0)
        scalar_volume = level / 100.0
        volume.SetMasterVolumeLevelScalar(scalar_volume, None)
        print(f"[Settings] Volume set to {level}%")
    except Exception as e:
        print(f"Error setting volume: {e}")

@eel.expose
def set_system_brightness(level):
    try:
        level = int(level)
        sbc.set_brightness(level)
        print(f"[Settings] Brightness set to {level}%")
    except Exception as e:
        print(f"Error setting brightness: {e}")

@eel.expose
def set_voice_rate(rate):
    try:
        settings = get_settings()
        settings["voice_rate"] = int(rate)
        save_settings(settings)
        print(f"[Settings] Voice rate set to {rate}")
    except Exception as e:
        print(f"Error setting voice rate: {e}")

@eel.expose
def set_voice_gender(gender_index):
    try:
        settings = get_settings()
        settings["voice_index"] = int(gender_index)
        save_settings(settings)
        print(f"[Settings] Voice gender set to index {gender_index}")
    except Exception as e:
        print(f"Error setting voice gender: {e}")

# HUD Backend Telemetry
import psutil

@eel.expose
def get_system_stats():
    try:
        cpu = psutil.cpu_percent(interval=None)
        battery = psutil.sensors_battery()
        bat_percent = battery.percent if battery else 100
        is_plugged = battery.power_plugged if battery else True
        
        return {
            "cpu": cpu,
            "battery": bat_percent,
            "plugged": is_plugged
        }
    except Exception as e:
        print(f"HUD Error: {e}")
        return {"cpu": 0, "battery": 100, "plugged": True}
