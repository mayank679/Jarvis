"""End-to-end test: open a WhatsApp chat and click the voice call button."""
import subprocess
import time
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Step 1: Open WhatsApp chat via deep link
print("=== Step 1: Opening WhatsApp chat ===")
whatsapp_url = "whatsapp://send?phone=+917050479912"
subprocess.run(f'start "" "{whatsapp_url}"', shell=True)
print("Waiting 5 seconds for chat to open...")
time.sleep(5)

# Step 2: Call the function
print("\n=== Step 2: Calling _click_wa_call_button(is_video=False) ===")
# Import after chat is open
sys.path.insert(0, '.')
from engine.features import _click_wa_call_button
_click_wa_call_button(is_video=False)

print("\n=== TEST COMPLETE ===")
