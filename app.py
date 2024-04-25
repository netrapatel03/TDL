import cv2
import numpy as np
import mediapipe as mp
import pyautogui
import time
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
import keyboard

from sus import sus

# Load the pre-trained model for left hand gesture recognition
model = load_model('research\gesture_recognition.h5')

# Initialize MediaPipe hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Set the frequency of key presses
pyautogui.PAUSE = 0.0001 # Adjust this value as needed

# Pre-calculate constants outside the loop
center_x, center_y, radius = 0, 0, 0

# Initialize an empty array to fit the scaler later
landmarks_for_fitting = []

# Function to extract landmarks of the left hand, scale them, and classify
def classify_left_hand_landmarks(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            if hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x > hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x:
                if len(hand_landmarks.landmark) == 21:
                    landmarks = []
                    for landmark in hand_landmarks.landmark:
                        landmarks.append(landmark.x)
                        landmarks.append(landmark.y)
                        landmarks.append(landmark.z)

                    landmarks_for_fitting.append(landmarks)
                    landmarks_array = np.array(landmarks).reshape(1, -1)
                    predictions = model.predict(landmarks_array)
                    return predictions
    return None

# Open webcam for video capture
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally
    frame = cv2.flip(frame, 1)

    # Process the frame to extract hand landmarks
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # Draw diagonal lines on the frame for visual effect
    height, width = frame.shape[:2]
    
    if center_x != width // 2 or center_y != height // 2 or radius != min(width, height) // 8:
        center_x, center_y, radius = width // 2, height // 2, min(width, height) // 8
    
    bottom_layer = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.line(bottom_layer, (0, 0), (width, height), (255, 255, 255), 2)
    cv2.line(bottom_layer, (0, height), (width, 0), (255, 255, 255), 2)
    blended_frame = cv2.addWeighted(bottom_layer, 0.2, frame, 0.8, 0)
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Check if landmarks of index and middle fingers are detected
            if (hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP] and 
                hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]):
                
                # Get the coordinates of index and middle finger tips
                index_tip_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * width
                middle_tip_x = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x * width
                
                # Check if the index finger is to the left of the middle finger
                if index_tip_x < middle_tip_x:
                    # If so, it's likely the right hand
                    index_tip_y = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * height)
                    cv2.circle(blended_frame, (int(index_tip_x), index_tip_y), 5, (0, 255, 255), -1)
                    
                    if ((index_tip_x - center_x) ** 2 + (index_tip_y - center_y) ** 2) <= radius ** 2:
                        cv2.putText(blended_frame, "No Movement", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        pyautogui.keyUp('w')
                        pyautogui.keyUp('s')
                        pyautogui.keyUp('a')
                        pyautogui.keyUp('d')
                    
                    else: 
                        # Calculate slope and intercept of diagonal lines only once per frame
                        slope_top_right = -1 # Slope of top-right diagonal line
                        slope_bottom_left = 1 # Slope of bottom-left diagonal line
                        intercept_top_right = center_y - slope_top_right * center_x
                        intercept_bottom_left = center_y - slope_bottom_left * center_x
                        
                        # Check if the finger belongs to any of the regions
                        if index_tip_y < slope_top_right * index_tip_x + intercept_top_right:
                            if index_tip_y < slope_bottom_left * index_tip_x + intercept_bottom_left:
                                cv2.putText(blended_frame, "Move Front", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                                pyautogui.keyDown('w')
                                pyautogui.keyUp('s')
                                pyautogui.keyUp('a')
                                pyautogui.keyUp('d')
                                print("Up")
                            else:
                                cv2.putText(blended_frame, "Move left", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                                pyautogui.keyDown('a')
                                keyboard.press('w')
                                pyautogui.keyUp('s')
                                pyautogui.keyUp('d')
                                print("Left")
                                
                        else:
                            if index_tip_y < slope_bottom_left * index_tip_x + intercept_bottom_left:
                                cv2.putText(blended_frame, "Move Right", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                                pyautogui.keyDown('d')
                                keyboard.press('w')
                                pyautogui.keyUp('a')
                                pyautogui.keyUp('s')
                                print("Right")
                                
                            else:
                                cv2.putText(blended_frame, "Move Back", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                                pyautogui.keyDown('s')
                                pyautogui.keyUp('a')
                                pyautogui.keyUp('d')
                                pyautogui.keyUp('w')
                                
                                print("Down")
                else:
                    # Left hand for gesture recognition using a pre-trained model
                    predictions = classify_left_hand_landmarks(frame)
                    if predictions is not None:
                        if predictions >= 0.999:
                            text = 'Shoot'
                            pyautogui.press('space')
                        else:
                            text = 'Hold'
                            
                        cv2.putText(blended_frame, text, (50,height -50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Draw the circle on top layer
    cv2.circle(blended_frame, (center_x, center_y), radius, (255, 255, 255), -1)
    
    # Display the frame
    cv2.imshow('Hand Gesture Recognition', blended_frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Fit the StandardScaler with the collected landmarks
scaler = StandardScaler()
scaler.fit_transform(np.array(landmarks_for_fitting))

# Release resources
cap.release()
cv2.destroyAllWindows()
hands.close()

sus()