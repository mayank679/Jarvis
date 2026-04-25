import sys
import os
sys.path.append(os.getcwd())

print("Starting import check...")
print("Importing eel...")
import eel
print("Importing engine.features...")
try:
    from engine.features import *
except Exception as e:
    print(f"Error importing engine.features: {e}")
    import traceback
    traceback.print_exc()
print("Importing engine.command...")
try:
    from engine.command import *
except Exception as e:
    print(f"Error importing engine.command: {e}")
    import traceback
    traceback.print_exc()
print("Importing engine.auth.recoganize...")
try:
    from engine.auth import recoganize
except Exception as e:
    print(f"Error importing engine.auth.recoganize: {e}")
    import traceback
    traceback.print_exc()
print("Importing engine.settings_controller...")
import engine.settings_controller
print("Importing engine.auth_api...")
import engine.auth_api
print("Importing engine.chat_storage...")
import engine.chat_storage
print("All imports completed.")
