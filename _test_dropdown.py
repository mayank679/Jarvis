"""After clicking Video call button, scan what appears in the dropdown."""
import time, sys, io, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pywinauto import Application

# Open chat first
subprocess.run('start "" "whatsapp://send?phone=+917050479912"', shell=True)
time.sleep(5)

app = Application(backend="uia").connect(title_re=".*WhatsApp.*")
main_window = app.window(title_re=".*WhatsApp.*")
main_window.wait('visible', timeout=10)

# Find and click the header Video call button
buttons = main_window.descendants(control_type="Button")
header_btn = None
for i, btn in enumerate(buttons):
    if btn.window_text() == 'Video call':
        nearby = [buttons[j].window_text() for j in range(max(0,i-2), min(len(buttons),i+3))]
        if 'Search' in nearby or 'Menu' in nearby:
            header_btn = btn
            break

if header_btn:
    print("Clicking Video call button...")
    header_btn.click_input()
    time.sleep(2)
    
    print("\n=== All control types and names after dropdown ===")
    # Scan for new elements that appeared
    for el in main_window.descendants():
        try:
            name = el.window_text()
            ctrl = el.friendly_class_name()
            if name and any(kw in name.lower() for kw in ["voice", "video", "audio", "call"]):
                rect = el.rectangle()
                print(f"  {ctrl}: '{name}' at ({rect.left},{rect.top})-({rect.right},{rect.bottom})")
        except:
            pass
    
    # Also check popups/dialogs
    print("\n=== Checking for popup windows ===")
    for win in app.windows():
        try:
            print(f"  Window: '{win.window_text()}'")
        except:
            pass

    # Press escape to cancel
    import pyautogui
    pyautogui.press('escape')
else:
    print("Could not find header Video call button!")
