import eel
import cv2
import numpy as np
import base64
import bcrypt
import time

# --- Password Authentication Setup ---
DEFAULT_PASSWORD = b"admin"
# In a real application, you would load this from a database. 
# Here we just generate a hash of 'admin' to validate against.
PASSWORD_HASH = bcrypt.hashpw(DEFAULT_PASSWORD, bcrypt.gensalt())

failed_attempts = 0
lockout_time = 0

@eel.expose
def password_login(password):
    global failed_attempts, lockout_time
    
    current_time = time.time()
    if lockout_time > current_time:
        remaining = int(lockout_time - current_time)
        return {"success": False, "message": f"Account locked. Try again in {remaining}s."}
        
    try:
        if bcrypt.checkpw(password.encode('utf-8'), PASSWORD_HASH):
            failed_attempts = 0
            return {"success": True, "message": "Login successful"}
        else:
            failed_attempts += 1
            if failed_attempts >= 3:
                lockout_time = current_time + 15  # Lock for 15 seconds
                return {"success": False, "message": "Max attempts reached. Locked for 15s."}
            return {"success": False, "message": f"Incorrect password. {3 - failed_attempts} tries left."}
    except Exception as e:
        return {"success": False, "message": "Authentication error."}

# --- Face Authentication Setup ---
# Pre-load models to improve response time during the login flow
try:
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_recognizer.read('engine/auth/trainer/trainer.yml')
    cascadePath = "engine/auth/haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascadePath)
    models_loaded = True
except Exception as e:
    print(f"Failed to load face recognition models: {e}")
    models_loaded = False

@eel.expose
def face_login(data_url):
    if not models_loaded:
        return {"success": False, "message": "Face recognition models not loaded."}
        
    try:
        # Decode base64 image
        encoded_data = data_url.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Min window size based on typical webcam resolution (like in recoganize.py)
        faces = face_cascade.detectMultiScale(
            converted_image,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(64, 48),
        )

        for(x, y, w, h) in faces:
            id, accuracy = face_recognizer.predict(converted_image[y:y+h, x:x+w])
            # If accuracy < 100, it's considered a match according to original recoganize.py
            if accuracy < 100:
                return {"success": True, "message": "Face Authentication Successful"}
        
        return {"success": False, "message": "Face not recognized."}
    except Exception as e:
        return {"success": False, "message": f"Error during face scan: {str(e)}"}
