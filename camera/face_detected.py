import cv2
import mediapipe as mp
import math
import numpy as np
import pyttsx3
from collections import deque

# Initialisation MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()

# Synthèse vocale
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Points pour les yeux
LEFT_EYE_CENTER = [33, 133, 159, 145, 153, 154]
RIGHT_EYE_CENTER = [263, 362, 386, 374, 380, 381]
LEFT_EYE_REGION = [33, 133, 160, 159, 158, 144]
LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 145
NOSE_TIP = 1

# Variables d’attention
attention_scores = deque(maxlen=50)
eye_closed_counter = 0
alert_triggered = False
parole_jouée = False

def average_point(landmarks, indices, w, h):
    x = sum([landmarks[i].x for i in indices]) / len(indices)
    y = sum([landmarks[i].y for i in indices]) / len(indices)
    return int(x * w), int(y * h)

def get_angle(p1, p2):
    return math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))

def detect_gaze_direction(frame, eye_landmarks, w, h):
    x_coords = [int(landmark.x * w) for landmark in eye_landmarks]
    y_coords = [int(landmark.y * h) for landmark in eye_landmarks]
    xmin, xmax = min(x_coords), max(x_coords)
    ymin, ymax = min(y_coords), max(y_coords)

    eye_img = frame[ymin:ymax, xmin:xmax]
    if eye_img.size == 0:
        return "indéfini"

    gray = cv2.cvtColor(eye_img, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)

    M = cv2.moments(threshold)
    if M['m00'] == 0:
        return "indéfini"
    cx = int(M['m10'] / M['m00'])
    pos = cx / (xmax - xmin)

    if pos < 0.35:
        return "gauche"
    elif pos > 0.65:
        return "droite"
    else:
        return "centre"

def is_eye_closed(landmarks, top_idx, bottom_idx, w, h, threshold=5):
    top_y = int(landmarks[top_idx].y * h)
    bottom_y = int(landmarks[bottom_idx].y * h)
    distance = abs(bottom_y - top_y)
    return distance < threshold

# Démarrer la webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)

    h, w, _ = frame.shape
    message = "Regard normal"
    score = 100

    if result.multi_face_landmarks:
        for face_landmarks in result.multi_face_landmarks:
            x_coords = [int(lm.x * w) for lm in face_landmarks.landmark]
            y_coords = [int(lm.y * h) for lm in face_landmarks.landmark]
            xmin, xmax = min(x_coords), max(x_coords)
            ymin, ymax = min(y_coords), max(y_coords)

            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 255), 2)

            left_eye = average_point(face_landmarks.landmark, LEFT_EYE_CENTER, w, h)
            right_eye = average_point(face_landmarks.landmark, RIGHT_EYE_CENTER, w, h)
            nose = int(face_landmarks.landmark[NOSE_TIP].x * w), int(face_landmarks.landmark[NOSE_TIP].y * h)

            angle = get_angle(left_eye, right_eye)
            cv2.putText(frame, f"Angle yeux: {angle:.2f}", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            eye_points = [face_landmarks.landmark[i] for i in LEFT_EYE_REGION]
            gaze = detect_gaze_direction(frame, eye_points, w, h)
            eye_closed = is_eye_closed(face_landmarks.landmark, LEFT_EYE_TOP, LEFT_EYE_BOTTOM, w, h)

            if eye_closed:
                eye_closed_counter += 1
                attention_scores.append(0)

                if eye_closed_counter >= 210:  # 7 secondes
                    message = "⚠️ Somnolence détectée"

                    if not alert_triggered:
                        print(">> 🔊 VOIX : Somnolence détectée")
                        try:
                            engine.say("Attention, somnolence détectée. Veuillez vous reconcentrer.")
                            engine.runAndWait()
                            parole_jouée = True
                        except Exception as e:
                            print("Erreur synthèse vocale :", e)

                        alert_triggered = True
                else:
                    message = "Inattention détectée (œil fermé)"
                    alert_triggered = False
            else:
                eye_closed_counter = 0
                alert_triggered = False
                parole_jouée = False
                if abs(angle) > 15 or gaze != "centre":
                    attention_scores.append(0)
                    message = "Inattention détectée"
                else:
                    attention_scores.append(1)

            cv2.circle(frame, left_eye, 3, (255, 0, 0), -1)
            cv2.circle(frame, right_eye, 3, (255, 0, 0), -1)

    if len(attention_scores) > 0:
        score = sum(attention_scores) / len(attention_scores) * 100

    with open("score.txt", "w") as f:
        f.write(f"{score:.1f}")

    if score >= 70:
        color = (0, 255, 0)
    elif score >= 40:
        color = (0, 165, 255)
    else:
        color = (0, 0, 255)

    bar_x, bar_y = 30, 120
    bar_width, bar_height = 200, 20
    filled = int(score / 100 * bar_width)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 1)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + filled, bar_y + bar_height), color, -1)
    cv2.putText(frame, "Niveau attention", (bar_x, bar_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.putText(frame, message, (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    cv2.putText(frame, f"Score Attention: {score:.1f}%", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    cv2.imshow("AI Involvement", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
