import pywinauto
from pywinauto import Desktop

print("Looking for WhatsApp window...")
windows = Desktop(backend="uia").windows(title="WhatsApp")
if not windows:
    print("WhatsApp window not found!")
    exit(1)

main_window = windows[0]
print(f"Found: {main_window.window_text()}")
print("Drawing outline around WhatsApp window...")
main_window.draw_outline()

print("\nSearching for Call buttons in the window...")
buttons = main_window.descendants(control_type="Button")
for b in buttons:
    try:
        text = b.window_text()
        if text:
            print(f"- Button: {text}")
    except:
        pass
