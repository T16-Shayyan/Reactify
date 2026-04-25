import cv2
import time
from GestureDetector import GestureDetector


detector = GestureDetector()
cap = cv2.VideoCapture(0)

last_print_time = 0
print_interval = 1.0  # print every sec

while True:
    ret, frame = cap.read()

    if not ret:
        print("Camera not found")
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_results = detector.process_face(rgb_frame)
    hand_results = detector.process_hands(rgb_frame)

    face_gesture = "no_face"
    hand_gesture = "no_hand"

    mouth_opening = None
    mouth_width = None
    mouth_ratio = None
    hand_distance = None

    # FACE
    if face_results.multi_face_landmarks:
        face_landmarks = face_results.multi_face_landmarks[0]

        upper_lip = face_landmarks.landmark[13]
        lower_lip = face_landmarks.landmark[14]
        left_corner = face_landmarks.landmark[61]
        right_corner = face_landmarks.landmark[291]

        mouth_opening = abs(upper_lip.y - lower_lip.y)
        mouth_width = abs(left_corner.x - right_corner.x)

        if mouth_width > 0:
            mouth_ratio = mouth_opening / mouth_width
        else:
            mouth_ratio = 0

        face_gesture = detector.detect_face_gesture(face_landmarks)

    # HAND
    if hand_results.multi_hand_landmarks:
        hand_gesture = detector.detect_hand_gesture(hand_results.multi_hand_landmarks)

        if len(hand_results.multi_hand_landmarks) >= 2:
            hand1 = hand_results.multi_hand_landmarks[0]
            hand2 = hand_results.multi_hand_landmarks[1]

            c1x, c1y = detector.get_palm_center(hand1)
            c2x, c2y = detector.get_palm_center(hand2)

            hand_distance = ((c1x - c2x) ** 2 + (c1y - c2y) ** 2) ** 0.5




    current_time = time.time()
    if current_time - last_print_time >= print_interval:

        print("-----")
        print("Face:", face_gesture)
        print("Hand:", hand_gesture)

        if mouth_opening is not None:
            print("mouth_opening:", round(mouth_opening, 4))
            print("mouth_width:", round(mouth_width, 4))
            print("mouth_ratio:", round(mouth_ratio, 4))
        else:
            print("No face detected")

        if hand_distance is not None:
            print("hand_distance:", round(hand_distance, 4))
        else:
            print("No 2-hand distance")


        last_print_time = current_time