"""Quick test to verify pywinauto can connect to WhatsApp and find call buttons."""
import sys
import time

print("=== Testing WhatsApp UIA Connection ===")

try:
    from pywinauto import Application

    # Test 1: Connect via window title
    print("\n[TEST 1] Connecting via title_re='.*WhatsApp.*' ...")
    try:
        app = Application(backend="uia").connect(title_re=".*WhatsApp.*")
        print("  SUCCESS: Connected to WhatsApp via title!")
    except Exception as e:
        print(f"  FAILED: {e}")
        # Test 1b: Connect via process name
        print("\n[TEST 1b] Connecting via path='WhatsApp.Root.exe' ...")
        try:
            app = Application(backend="uia").connect(path="WhatsApp.Root.exe")
            print("  SUCCESS: Connected to WhatsApp via process name!")
        except Exception as e2:
            print(f"  FAILED: {e2}")
            print("\n=== RESULT: Cannot connect to WhatsApp. Is it running? ===")
            sys.exit(1)

    # Test 2: Find the window
    print("\n[TEST 2] Finding WhatsApp main window ...")
    main_window = app.window(title_re=".*WhatsApp.*")
    main_window.wait('visible', timeout=10)
    print(f"  SUCCESS: Found window: {main_window.window_text()}")

    # Test 3: Look for call buttons
    print("\n[TEST 3] Scanning for call-related buttons ...")
    try:
        buttons = main_window.descendants(control_type="Button")
        print(f"  Found {len(buttons)} buttons total. Listing call-related ones:")
        for btn in buttons:
            name = btn.window_text()
            if any(kw in name.lower() for kw in ["call", "voice", "video", "audio", "phone"]):
                print(f"    -> Button: '{name}' (control_type={btn.friendly_class_name()})")
    except Exception as e:
        print(f"  Error scanning buttons: {e}")

    # Test 4: Try to find Voice call button specifically
    print("\n[TEST 4] Looking for 'Voice call' button ...")
    try:
        call_btn = main_window.child_window(title="Voice call", control_type="Button")
        call_btn.wait('visible', timeout=3)
        print(f"  SUCCESS: Found 'Voice call' button!")
    except Exception as e:
        print(f"  Not found: {e}")

    print("\n[TEST 5] Looking for 'Video call' button ...")
    try:
        call_btn = main_window.child_window(title="Video call", control_type="Button")
        call_btn.wait('visible', timeout=3)
        print(f"  SUCCESS: Found 'Video call' button!")
    except Exception as e:
        print(f"  Not found: {e}")

    print("\n=== ALL TESTS COMPLETE ===")

except Exception as ex:
    print(f"FATAL ERROR: {ex}")
    import traceback
    traceback.print_exc()
