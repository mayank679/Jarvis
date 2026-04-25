import pywinauto
from pywinauto import Desktop

windows = Desktop(backend="uia").windows()
print("Open Windows:")
for w in windows:
    try:
        title = w.window_text()
        if title:
            print(f"- {title}")
    except:
        pass
