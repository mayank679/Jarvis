import os
import time
import xml.etree.ElementTree as ET
import subprocess

def find_bounds_and_tap(content_desc):
    # Dump UI
    subprocess.run("adb shell uiautomator dump", shell=True, capture_output=True)
    subprocess.run("adb pull /sdcard/window_dump.xml", shell=True, capture_output=True)
    
    if not os.path.exists("window_dump.xml"):
        print("Failed to pull dump")
        return False
        
    try:
        tree = ET.parse("window_dump.xml")
        root = tree.getroot()
        
        for node in root.iter('node'):
            desc = node.attrib.get('content-desc', '')
            if content_desc.lower() in desc.lower():
                bounds = node.attrib.get('bounds', '')
                # format: [x1,y1][x2,y2]
                if bounds:
                    bounds = bounds.replace('[', '').replace(']', ',').split(',')
                    x1, y1, x2, y2 = map(int, bounds[:4])
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2
                    print(f"Found '{content_desc}' at {cx}, {cy}")
                    subprocess.run(f"adb shell input tap {cx} {cy}", shell=True)
                    return True
        print(f"Could not find '{content_desc}'")
        return False
    except Exception as e:
        print("Error parsing XML:", e)
        return False

# Open a dummy chat
subprocess.run('adb shell am start -a android.intent.action.VIEW -d "whatsapp://send?phone=+919876543210"', shell=True)
print("Waiting 5 seconds for chat to open...")
time.sleep(5)

# Try finding the Call button
print("Looking for Video call button...")
if not find_bounds_and_tap("Video call"):
    print("Looking for Voice call button...")
    find_bounds_and_tap("Voice call")
