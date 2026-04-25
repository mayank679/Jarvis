"""Open a WhatsApp chat first, then scan for call buttons."""
import subprocess
import time
import sys

# First, open a WhatsApp chat (using a test number)
print("=== Opening WhatsApp chat via deep link ===")
whatsapp_url = "whatsapp://send?phone=+917050479912"
subprocess.run(f'start "" "{whatsapp_url}"', shell=True)
print("Waiting 5 seconds for chat to open...")
time.sleep(5)

print("\n=== Scanning for call buttons in open chat ===")
from pywinauto import Application

try:
    app = Application(backend="uia").connect(title_re=".*WhatsApp.*")
    main_window = app.window(title_re=".*WhatsApp.*")
    main_window.wait('visible', timeout=10)
    print(f"Connected to: {main_window.window_text()}")

    # List ALL buttons in the window
    buttons = main_window.descendants(control_type="Button")
    print(f"\nTotal buttons: {len(buttons)}")
    print("\nAll buttons with call/voice/video/audio-related names:")
    for btn in buttons:
        name = btn.window_text()
        if any(kw in name.lower() for kw in ["call", "voice", "video", "audio", "phone"]):
            print(f"  -> '{name}'")
    
    print("\n--- First 40 button names (for reference) ---")
    for i, btn in enumerate(buttons[:40]):
        print(f"  [{i}] '{btn.window_text()}'")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
