import pyttsx3
import speech_recognition as sr
import eel
import time
def speak(text):
    import json, os
    text = str(text)
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    
    settings_path = "engine/settings.json"
    voice_rate = 174
    voice_index = 0
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r") as f:
                settings = json.load(f)
                voice_rate = settings.get("voice_rate", 174)
                voice_index = settings.get("voice_index", 0)
        except:
            pass

    # Ensure index is within range
    if voice_index >= len(voices):
        voice_index = 0

    engine.setProperty('voice', voices[voice_index].id)
    engine.setProperty('rate', voice_rate)
    
    eel.DisplayMessage(text)
    engine.say(text)
    eel.receiverText(text)
    engine.runAndWait()


def takecommand():

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('listening....')
        eel.DisplayMessage('listening....')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        
        audio = r.listen(source, 10, 6)

    try:
        print('recognizing')
        eel.DisplayMessage('recognizing....')
        query = r.recognize_google(audio, language='en-in')
        print(f"user said: {query}")
        eel.DisplayMessage(query)
        time.sleep(2)
       
    except Exception as e:
        return ""
    
    return query.lower()

@eel.expose
def allCommands(message=1):

    if message == 1:
        query = takecommand()
        print(query)
        eel.senderText(query)
    else:
        query = message
        eel.senderText(query)
    try:

        if ("youtube" in query and "play" in query) or ("on youtube" in query):
            from engine.features import PlayYoutube
            PlayYoutube(query)
        elif "open" in query:
            from engine.features import openCommand
            openCommand(query)
        
        elif "send message" in query or "phone call" in query or "video call" in query or "make a call" in query or "make call" in query or "whatsapp call" in query:
            from engine.features import findContact, whatsApp, makeCall, sendMessage
            contact_no, name = findContact(query)
            if(contact_no != 0):
                speak("Which mode you want to use whatsapp or mobile")
                preferance = takecommand()
                print(preferance)

                if "mobile" in preferance:
                    if "send message" in query or "send sms" in query: 
                        speak("what message to send")
                        message = takecommand()
                        sendMessage(message, contact_no, name)
                    elif "phone call" in query:
                        makeCall(name, contact_no)
                    else:
                        speak("please try again")
                elif "whatsapp" in preferance:
                    message = ""
                    if "send message" in query:
                        message = 'message'
                        speak("what message to send")
                        query = takecommand()
                                        
                    elif "video call" in query:
                        message = 'video'
                    else:
                        message = 'call'
                                        
                    whatsApp(contact_no, query, message, name)

        else:
            from engine.features import geminai
            geminai(query)
    except Exception as e:
        print(f"[Command Error] {type(e).__name__}: {e}")
    
    eel.ShowHood()

@eel.expose
def openSettings():
    speak("Opening settings...")
    print("[DEBUG] Settings function triggered")
    # You can add more settings logic here
