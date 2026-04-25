import os
import re
import subprocess
import time
import markdown2
from bs4 import BeautifulSoup


def extract_yt_term(command):
    match = re.search(r'play\s+(.*)', command, re.IGNORECASE)
    if match:
        term = match.group(1).strip()
        term = term.replace("on youtube", "").strip()
        if term:
            return term
    return command


def remove_words(input_string, words_to_remove):
    # Split the input string into words
    words = input_string.split()

    # Remove unwanted words
    filtered_words = [word for word in words if word.lower() not in words_to_remove]

    # Join the remaining words back into a string
    result_string = ' '.join(filtered_words)

    return result_string



# Check if ADB is connected to a device
def adb_connected():
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=5)
        lines = result.stdout.strip().split('\n')
        # First line is "List of devices attached", actual devices follow
        devices = [l for l in lines[1:] if l.strip() and 'device' in l]
        return len(devices) > 0
    except Exception:
        return False

# key events like receive call, stop call, go back
def keyEvent(key_code):
    if not adb_connected():
        print("[ADB] No device connected. Cannot send key event.")
        return False
    command =  f'adb shell input keyevent {key_code}'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ADB] keyEvent failed: {result.stderr.strip()}")
        return False
    time.sleep(1)
    return True

# Tap event used to tap anywhere on screen
def tapEvents(x, y):
    if not adb_connected():
        print("[ADB] No device connected. Cannot send tap event.")
        return False
    command =  f'adb shell input tap {x} {y}'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ADB] tapEvents failed: {result.stderr.strip()}")
        return False
    time.sleep(1)
    return True

# Input Event is used to insert text in mobile
def adbInput(message):
    if not adb_connected():
        print("[ADB] No device connected. Cannot send input.")
        return False
    command =  f'adb shell input text "{message}"'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ADB] adbInput failed: {result.stderr.strip()}")
        return False
    time.sleep(1)
    return True

# to go complete back
def goback(key_code):
    for i in range(6):
        keyEvent(key_code)

# To replace space in string with %s for complete message send
def replace_spaces_with_percent_s(input_string):
    return input_string.replace(' ', '%s')

# Gemini API chatbot function
def markdown_to_text(md):
    html = markdown2.markdown(md)
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text().strip()