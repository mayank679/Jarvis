import os
from shlex import quote
import re
import sqlite3
import struct
import subprocess
import base64
import time
import webbrowser
from playsound import playsound
import eel
import pyaudio
import pyautogui
from engine.command import speak
from engine.config import ASSISTANT_NAME, LLM_KEY, GEMINI_API_KEY
# Playing assiatnt sound function
import pywhatkit as kit
import pvporcupine

from engine.helper import extract_yt_term, markdown_to_text, remove_words

con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

@eel.expose
def playAssistantSound():
    music_dir = os.path.join("www", "assets", "audio", "start_sound.mp3")
    playsound(music_dir)

    
def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")

       

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)


def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
       
        # pre trained keywords    
        porcupine=pvporcupine.create(keywords=["jarvis","alexa"]) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

            # processing keyword comes from mic 
            keyword_index=porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index>=0:
                print("hotword detected")

                # pressing shorcut key win+j
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()


# find contacts
def findContact(query):
    
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
# Helper: click the Voice/Video call button in WhatsApp Desktop
def _click_wa_call_button(is_video=False):
    """Use Windows UI Automation (pywinauto) to click the call button in WhatsApp Desktop.

    WhatsApp Desktop (Windows) has a SINGLE 'Video call' button in the chat header.
    Clicking it opens a dropdown with 'Voice call' and 'Video call' menu items.
    Falls back to the legacy pixel-offset method if UIA fails.
    """
    call_type = "Video call" if is_video else "Voice call"
    print(f"[WhatsApp] Attempting UIA call: '{call_type}' ...")

    try:
        from pywinauto import Application

        # Connect by window title (process may be WhatsApp.exe or WhatsApp.Root.exe)
        try:
            app = Application(backend="uia").connect(title_re=".*WhatsApp.*")
        except Exception:
            for proc_name in ["WhatsApp.Root.exe", "WhatsApp.exe"]:
                try:
                    app = Application(backend="uia").connect(path=proc_name)
                    break
                except Exception:
                    continue
            else:
                raise RuntimeError("Could not connect to WhatsApp via UIA")

        main_window = app.window(title_re=".*WhatsApp.*")
        main_window.wait('visible', timeout=10)

        # --- Strategy 1: Find the chat-header 'Video call' button ---
        # The chat header has: [contact name] [Video call] [Search] [Menu]
        # There may be many 'Video call' buttons (from call history), so we need
        # the one near 'Search' and 'Menu' buttons in the chat header area.
        buttons = main_window.descendants(control_type="Button")
        header_call_btn = None

        for i, btn in enumerate(buttons):
            if btn.window_text() == 'Video call':
                # Check if nearby buttons are 'Search' and 'Menu' (chat header pattern)
                nearby_names = []
                for j in range(max(0, i-2), min(len(buttons), i+3)):
                    nearby_names.append(buttons[j].window_text())
                if 'Search' in nearby_names or 'Menu' in nearby_names:
                    header_call_btn = btn
                    print(f"[WhatsApp] Found chat-header 'Video call' button (index {i})")
                    break

        if header_call_btn is None:
            # Fallback: just use the first 'Video call' button found
            for btn in buttons:
                if btn.window_text() == 'Video call':
                    header_call_btn = btn
                    print("[WhatsApp] Using first 'Video call' button as fallback")
                    break

        if header_call_btn is None:
            raise RuntimeError("No 'Video call' button found in WhatsApp")

        # Click the Video call button to open the dropdown
        header_call_btn.click_input()
        print("[WhatsApp] Clicked 'Video call' button, waiting for dropdown ...")
        time.sleep(1.5)

        # --- Now select the right option from the dropdown ---
        # WhatsApp Desktop shows a GroupBox popup with 'Voice' and 'Video' as ListItems
        dropdown_name = "Video" if is_video else "Voice"

        name_variants = [dropdown_name, call_type, f"{dropdown_name} call"]
        ctrl_types = ["ListItem", "MenuItem", "Button"]
        for name in name_variants:
            for ctrl_type in ctrl_types:
                try:
                    option = main_window.child_window(title=name, control_type=ctrl_type, found_index=0)
                    option.wait('visible', timeout=2)
                    option.click_input()
                    print(f"[WhatsApp] UIA: Selected '{name}' ({ctrl_type}, index=0). SUCCESS!")
                    return
                except Exception:
                    continue

        # If dropdown selection failed but we already clicked the call button,
        # for video call the button itself might have initiated it directly
        if is_video:
            print("[WhatsApp] Dropdown not found, but 'Video call' button was clicked - call may have started directly.")
            return

        raise RuntimeError(f"Could not select '{call_type}' from dropdown")

    except Exception as e:
        print(f"[WhatsApp] UIA method failed: {e}")
        print("[WhatsApp] Falling back to pixel-offset method ...")
        _click_wa_call_button_fallback(is_video)


def _click_wa_call_button_fallback(is_video=False):
    """Legacy fallback: find WhatsApp window by title, maximize & focus, click by pixel offset."""
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32

    found_handles = []
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

    def _enum_cb(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                if 'WhatsApp' in buf.value:
                    found_handles.append(hwnd)
                    return False
        return True

    cb_ref = WNDENUMPROC(_enum_cb)
    user32.EnumWindows(cb_ref, 0)

    if not found_handles:
        print("[WhatsApp] FALLBACK ERROR: Could not find the WhatsApp window!")
        return

    hwnd = found_handles[0]
    print(f"[WhatsApp] Fallback – Found window handle: {hwnd}")

    user32.ShowWindow(hwnd, 3)            # SW_MAXIMIZE
    time.sleep(0.5)

    user32.keybd_event(0x12, 0, 0, 0)     # Alt-down
    user32.keybd_event(0x12, 0, 2, 0)     # Alt-up
    user32.SetForegroundWindow(hwnd)
    time.sleep(1)

    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w = rect.right - rect.left
    print(f"[WhatsApp] Fallback – Window: L={rect.left} T={rect.top} R={rect.right} B={rect.bottom} (width={w})")

    call_x = rect.right - 100
    call_y = rect.top + 46
    print(f"[WhatsApp] Fallback – Clicking Call button at ({call_x}, {call_y})")
    pyautogui.click(call_x, call_y)
    time.sleep(1)

    if is_video:
        pyautogui.click(call_x, call_y + 72)
    else:
        pyautogui.click(call_x, call_y + 36)
    time.sleep(0.5)


# Whatsapp Message 
def whatsApp(mobile_no, message, flag, name):
    if flag == 'message':
        jarvis_message = "message sent successfully to " + name
    elif flag == 'call':
        message = ''   # Don't pre-fill any text for calls
        jarvis_message = "calling " + name
    else:
        message = ''   # Don't pre-fill any text for video calls
        jarvis_message = "starting video call with " + name

    # Build the WhatsApp deep-link URL
    encoded_message = quote(message)
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp to the contact's chat
    subprocess.run(full_command, shell=True)
    time.sleep(5)

    if flag == 'message':
        # The URL pre-filled the text; just press Enter to send
        pyautogui.press('enter')

    elif flag == 'call':
        _click_wa_call_button(is_video=False)

    elif flag == 'video':
        _click_wa_call_button(is_video=True)

    speak(jarvis_message)



# API Key for Groq LLM
from groq import Groq
def geminai(query):
    try:
        query = query.replace(ASSISTANT_NAME, "")
        query = query.replace("search", "")
        
        client = Groq(api_key=LLM_KEY)
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant. Always keep your responses concise and strictly limited to 100-120 words maximum, no matter what topic is asked. Be informative but brief."
                },
                {
                    "role": "user", 
                    "content": query
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        
        response_text = chat_completion.choices[0].message.content
        filter_text = markdown_to_text(response_text)
        speak(filter_text)
    except Exception as e:
        print("Error:", e)
        if "Quota exceeded" in str(e) or "429" in str(e):
            speak("Sir, the API quota has been exceeded. Please update the API key in the config file.")
        else:
            speak("Sorry sir, the API is not responding.")

@eel.expose
def analyze_image(base64_data):
    try:
        eel.receiverText("Analyzing the uploaded media...")()
        eel.DisplayMessage("Analyzing the media, please wait.")()
        speak("Analyzing the media, please wait.")
        
        # Parse the base64 data (format: "data:image/jpeg;base64,...")
        header, b64 = base64_data.split(';base64,')
        mime_type = header.replace('data:', '')
        import base64
        image_bytes = base64.b64decode(b64)
        
        # Use the original Gemini key strictly for image analysis since Groq lacks vision
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = "Analyze the contents of this uploaded media. If it is an image, describe it in a concise manner. If it is a document (like a PDF), summarize its key points. Important: Limit your entire response to approximately 30 words maximum."
        
        response = model.generate_content([
            {'mime_type': mime_type, 'data': image_bytes},
            prompt
        ])
        
        description = response.text
        from engine.helper import markdown_to_text
        filter_text = markdown_to_text(description)
        
        eel.receiverText(filter_text)()
        eel.DisplayMessage(filter_text)()
        speak(filter_text)
        eel.ShowHood()
        
    except Exception as e:
        print("Error analyzing image:", e)
        error_msg = "Sorry sir, the image analysis API is currently overloaded. Please try again in a minute."
        eel.receiverText(error_msg)()
        speak(error_msg)
        eel.ShowHood()



# android automation

def makeCall(name, mobileNo):
    from engine.helper import adb_connected
    mobileNo = mobileNo.replace(" ", "")
    if not adb_connected():
        speak("Sorry sir, no Android device is connected via ADB. Please connect your phone first.")
        return
    speak("Calling "+name)
    command = 'adb shell am start -a android.intent.action.CALL -d tel:'+mobileNo
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ADB] makeCall failed: {result.stderr.strip()}")
        speak("Failed to make the call. Please check the ADB connection.")


# to send message
def sendMessage(message, mobileNo, name):
    from engine.helper import replace_spaces_with_percent_s, goback, keyEvent, tapEvents, adbInput, adb_connected
    if not adb_connected():
        speak("Sorry sir, no Android device is connected via ADB. Please connect your phone first.")
        return
    message = replace_spaces_with_percent_s(message)
    mobileNo = replace_spaces_with_percent_s(mobileNo)
    speak("sending message")
    goback(4)
    time.sleep(1)
    keyEvent(3)
    # open sms app
    tapEvents(136, 2220)
    #start chat
    tapEvents(819, 2192)
    # search mobile no
    adbInput(mobileNo)
    #tap on name
    tapEvents(601, 574)
    # tap on input
    tapEvents(390, 2270)
    #message
    adbInput(message)
    #send
    tapEvents(957, 1397)
    speak("message send successfully to "+name)