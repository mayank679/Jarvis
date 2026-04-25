"""Click Menu button and find voice call option."""
import time, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pywinauto import Application

app = Application(backend="uia").connect(title_re=".*WhatsApp.*")
main_window = app.window(title_re=".*WhatsApp.*")
main_window.wait('visible', timeout=10)

buttons = main_window.descendants(control_type="Button")

# Find Menu buttons
menu_buttons = [b for b in buttons if b.window_text() == 'Menu']
print(f"Found {len(menu_buttons)} Menu buttons")

if len(menu_buttons) >= 2:
    chat_menu = menu_buttons[1]
    print("Clicking chat header Menu...")
    chat_menu.click_input()
    time.sleep(2)
    
    # Scan ALL descendants for anything call-related
    print("\n=== All call-related elements after menu click ===")
    for el in main_window.descendants():
        try:
            name = el.window_text()
            if name and any(kw in name.lower() for kw in ["voice", "audio", "call"]):
                print(f"  {el.friendly_class_name()}: '{name}'")
        except:
            pass

    # List all menu items
    print("\n=== All MenuItems ===")
    for el in main_window.descendants(control_type="MenuItem"):
        try:
            print(f"  MenuItem: '{el.window_text()}'")
        except:
            pass

    # Also list items
    print("\n=== All ListItems ===")
    for el in main_window.descendants(control_type="ListItem"):
        try:
            name = el.window_text()
            if name:
                print(f"  ListItem: '{name}'")
        except:
            pass
    
    # Press Escape to close menu
    import pyautogui
    pyautogui.press('escape')
