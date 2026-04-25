import os
import eel

from engine.features import *
from engine.command import *
from engine.auth import recoganize
import engine.settings_controller
import engine.auth_api
import engine.chat_storage
def start():
    
    eel.init("www")

    playAssistantSound()
    @eel.expose
    def init():
        import time
        # Start ADB connection in background (non-blocking)
        try:
            subprocess.Popen([r'device.bat'], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("[ADB] Device connection started in background.")
        except Exception as e:
            print(f"[ADB] Could not start device.bat: {e} — phone features will be unavailable.")
        
        # Add a 6 second delay so the UI shows 'Initializing...' before the auth screen
        time.sleep(6)
        eel.hideLoader()
        speak("Authentication Required")

    @eel.expose
    def on_auth_success():
        eel.hideFaceAuth()
        speak("Authentication Successful")
        eel.hideFaceAuthSuccess()
        speak("Welcome to the AI Assistant , Hi Mayank , How can i Help You")
        eel.hideStart()
        playAssistantSound()
    os.system('start msedge.exe --app="http://localhost:8000/index.html"')

    eel.start('index.html', mode=None, host='localhost', block=True)