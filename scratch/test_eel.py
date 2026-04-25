import eel
import os

eel.init('www')

@eel.expose
def test_call():
    print("JS called Python!")

try:
    print("Starting Eel test on port 8000...")
    eel.start('index.html', mode=None, port=8000, block=False)
    print("Eel started successfully.")
    import time
    time.sleep(5)
    print("Closing Eel test.")
except Exception as e:
    print(f"Error starting Eel: {e}")
