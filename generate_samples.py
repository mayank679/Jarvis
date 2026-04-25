import cv2
import os
import numpy as np
import random

# Clear existing samples for ID 1
samples_dir = r"engine\auth\samples"
if not os.path.exists(samples_dir):
    os.makedirs(samples_dir)

for file in os.listdir(samples_dir):
    if file.startswith("face.1."):
        os.remove(os.path.join(samples_dir, file))

# Load the uploaded image
image_path = r"C:\Users\asus\.gemini\antigravity\brain\971befd0-6ab9-460c-b366-7875c66e8572\media__1776362674232.jpg"
img = cv2.imread(image_path)
if img is None:
    print("Failed to load image!")
    exit(1)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
detector = cv2.CascadeClassifier(r'engine\auth\haarcascade_frontalface_default.xml')
faces = detector.detectMultiScale(gray, 1.3, 5)

if len(faces) == 0:
    print("No faces detected in the image.")
    exit(1)

for (x,y,w,h) in faces:
    face_roi = gray[y:y+h, x:x+w]
    
    # Save 100 slight variations (for better LBPH training)
    count = 0
    while count < 100:
        count += 1
        # Add slight random shifts to x, y, or resize to augment the sample
        scale = random.uniform(0.9, 1.1)
        shift_x = random.randint(-5, 5)
        shift_y = random.randint(-5, 5)
        
        M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
        augmented = cv2.warpAffine(face_roi, M, (w, h))
        
        file_name = f"face.1.{count}.jpg"
        cv2.imwrite(os.path.join(samples_dir, file_name), augmented)
    
    print(f"Successfully generated 100 samples for ID 1 (Mayank)")
    break
