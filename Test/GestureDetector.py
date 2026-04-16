import mediapipe as mp


class GestureDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands

        self.face_mesh = self.mp_face_mesh.FaceMesh(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            max_num_faces=1
        )

        self.hands = self.mp_hands.Hands(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            max_num_hands=2
        )

        

    def process_face(self, rgb_frame):
        return self.face_mesh.process(rgb_frame)



    def process_hands(self, rgb_frame):
        return self.hands.process(rgb_frame)



    def detect_face_gesture(self, face_landmarks):
        upper_lip = face_landmarks.landmark[13]
        lower_lip = face_landmarks.landmark[14]
        left_corner = face_landmarks.landmark[61]
        right_corner = face_landmarks.landmark[291]

        mouth_opening = abs(upper_lip.y - lower_lip.y)
        mouth_width = abs(left_corner.x - right_corner.x)

        # surprised
        if mouth_opening > 0.05 and mouth_width > 0.06:
            return "surprised"

        # tongue out
        if mouth_opening > 0.03:
            return "tongue_out"

        # pouting 
        if mouth_width < 0.04 and mouth_opening < 0.02:
            return "pouting"

        return "neutral"

    def detect_hand_gesture(self, multi_hand_landmarks):

        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]

        if not multi_hand_landmarks:
            return "unknown"

        # two hands
        if len(multi_hand_landmarks) >= 2:
            hand1 = multi_hand_landmarks[0]
            hand2 = multi_hand_landmarks[1]
        
            close_count = 0
        
            for tip in tips:
                p1 = hand1.landmark[tip]
                p2 = hand2.landmark[tip]
    
                dist = ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5

                #change this to fix this
                if dist < 0.05:
                    close_count += 1
    
            if close_count >= 2:
                return "hands_together"
    
            return "two_hands"

        # single
        hand_landmarks = multi_hand_landmarks[0]

        index_up = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
        middle_up = hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
        ring_up = hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y
        pinky_up = hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y

        

        fingers_up = 0
        for tip, pip in zip(tips, pips):
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
                fingers_up += 1
    
        thumb_tip = hand_landmarks.landmark[4]
        thumb_ip = hand_landmarks.landmark[3]
        thumb_mcp = hand_landmarks.landmark[2]
    
        thumb_up = thumb_tip.y < thumb_ip.y < thumb_mcp.y
    
        if fingers_up == 4 and thumb_up:
            return "open_palm"
        elif index_up and middle_up and not ring_up and not pinky_up:
            return "peace"
        elif fingers_up == 0 and not thumb_up:
            return "fist"
        elif thumb_up and fingers_up == 0:
            return "thumbs_up"
    
        return "unknown"

    # def get_hand_center(self, hand_landmarks):
    #     x = 0
    #     y = 0

    #     for lm in hand_landmarks.landmark:
    #         x += lm.x
    #         y += lm.y

    #     return (x / len(hand_landmarks.landmark),
    #             y / len(hand_landmarks.landmark))
