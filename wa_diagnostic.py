"""Quick diagnostic to inspect WhatsApp Desktop UI elements."""
import time
import sys

print("=" * 60)
print("WhatsApp Desktop UI Inspector")
print("=" * 60)
print("\nPlease open WhatsApp Desktop and navigate to any chat.")
print("Waiting 5 seconds...\n")
time.sleep(5)

try:
    from pywinauto import Application

    # Try connecting to WhatsApp
    app = None
    for method in ["title", "path_root", "path_exe"]:
        try:
            if method == "title":
                app = Application(backend="uia").connect(title_re=".*WhatsApp.*")
            elif method == "path_root":
                app = Application(backend="uia").connect(path="WhatsApp.Root.exe")
            else:
                app = Application(backend="uia").connect(path="WhatsApp.exe")
            print(f"[OK] Connected via {method}")
            break
        except Exception as e:
            print(f"[FAIL] {method}: {e}")
            continue

    if app is None:
        print("\n[ERROR] Could not connect to WhatsApp Desktop at all!")
        print("Make sure WhatsApp is open and visible.")
        sys.exit(1)

    main_window = app.window(title_re=".*WhatsApp.*")
    print(f"\n[OK] Main window: '{main_window.window_text()}'")
    print(f"     Rectangle: {main_window.rectangle()}")

    # List ALL buttons
    print("\n--- ALL BUTTONS ---")
    buttons = main_window.descendants(control_type="Button")
    for i, btn in enumerate(buttons):
        try:
            name = btn.window_text()
            rect = btn.rectangle()
            print(f"  [{i:3d}] '{name}' at ({rect.left},{rect.top})-({rect.right},{rect.bottom})")
        except:
            print(f"  [{i:3d}] <error reading>")

    # List toolbar items
    print("\n--- TOOLBAR ITEMS ---")
    toolbars = main_window.descendants(control_type="ToolBar")
    for tb in toolbars:
        try:
            print(f"  Toolbar: '{tb.window_text()}'")
            for child in tb.children():
                print(f"    -> '{child.window_text()}' ({child.element_info.control_type})")
        except:
            pass

    # List menu items
    print("\n--- MENU ITEMS ---")
    menus = main_window.descendants(control_type="MenuItem")
    for m in menus:
        try:
            print(f"  '{m.window_text()}'")
        except:
            pass

    # Search for anything with "call" or "video" or "voice" in the name
    print("\n--- ELEMENTS CONTAINING 'call', 'video', 'voice', 'audio' ---")
    all_elements = main_window.descendants()
    for elem in all_elements:
        try:
            name = elem.window_text().lower()
            if any(kw in name for kw in ['call', 'video', 'voice', 'audio', 'phone']):
                ctrl_type = elem.element_info.control_type
                rect = elem.rectangle()
                print(f"  '{elem.window_text()}' ({ctrl_type}) at ({rect.left},{rect.top})-({rect.right},{rect.bottom})")
        except:
            pass

    print("\n" + "=" * 60)
    print("Diagnostic complete!")

except ImportError:
    print("[ERROR] pywinauto is not installed. Run: pip install pywinauto")
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
