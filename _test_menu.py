"""Check the Menu dropdown for voice/audio call options."""
import time
from pywinauto import Application

print("=== Connecting to WhatsApp ===")
app = Application(backend="uia").connect(title_re=".*WhatsApp.*")
main_window = app.window(title_re=".*WhatsApp.*")
main_window.wait('visible', timeout=10)
print(f"Connected: {main_window.window_text()}")

# The chat should already be open from previous test
# Find all buttons first to locate the header Menu
buttons = main_window.descendants(control_type="Button")
print(f"\nLooking for header area buttons near 'Video call'...")

# Find the Menu button right after Video call
found_video = False
for i, btn in enumerate(buttons):
    name = btn.window_text()
    if name == 'Video call' and not found_video:
        found_video = True
        print(f"  [{i}] '{name}' <- Video call found")
        # Print nearby buttons
        for j in range(max(0, i-3), min(len(buttons), i+5)):
            print(f"  [{j}] '{buttons[j].window_text()}'")
        break

# Now click the Menu button (should be near Video call)
print("\n=== Clicking Menu button to see dropdown ===")
# Find Menu buttons - the one near the Video call
menu_buttons = [b for b in buttons if b.window_text() == 'Menu']
if len(menu_buttons) >= 2:
    # Second Menu button is typically the chat header menu
    chat_menu = menu_buttons[1]
    print(f"Clicking chat header Menu button...")
    chat_menu.click_input()
    time.sleep(2)
    
    # Now scan for menu items
    print("\n=== Scanning for menu items after click ===")
    menu_items = main_window.descendants(control_type="MenuItem")
    print(f"Found {len(menu_items)} menu items:")
    for mi in menu_items:
        print(f"  MenuItem: '{mi.window_text()}'")
    
    # Also check for any new buttons or list items
    all_elements = main_window.descendants()
    print(f"\nLooking for call-related elements after menu click:")
    for el in all_elements:
        name = el.window_text()
        if any(kw in name.lower() for kw in ["voice", "audio", "call"]):
            print(f"  {el.friendly_class_name()}: '{name}'")
else:
    print(f"Found {len(menu_buttons)} Menu buttons, expected at least 2")
    for i, mb in enumerate(menu_buttons):
        print(f"  Menu button {i}: '{mb.window_text()}'")
