"""
Tongue Detection Meme Display
A MediaPipe + OpenCV application that detects when your tongue is out
and displays different meme images accordingly.

See TUTORIAL.md for detailed explanations
"""

import cv2
import numpy as np
import os
from GestureDetector import GestureDetector
from GestureMapper import GestureMapper

# ============================================================================
# CONFIGURATION SETTINGS
# ============================================================================

# Window settings - approximately half monitor size (1920x1080 / 2)
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 720


#UI functions
def get_available_images(mapper):
    mapper.load_images()
    return mapper.list_images()

def save_user_mapping(mapper, json_path, face, hand, image_name):
    mapper.load_images()
    mapper.load_mappings(json_path)
    mapper.app_mapping(face, hand, image_name)
    mapper.save_mappings(json_path)

def add_image(source_path, image_folder, mapper=None):
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Image not found: {source_path}")

    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    filename = os.path.basename(source_path)
    destination = os.path.join(image_folder, filename)

    shutil.copy2(source_path, destination)

    if mapper is not None:
        mapper.load_images()

    return filename



def main():
    """
    Main application loop.
    
    This function:
    1. Loads the meme images
    2. Initializes the webcam
    3. Creates display windows
    4. Runs the main detection loop
    5. Handles cleanup on exit
    """
    
    # ========================================================================
    # STEP 1: Load and prepare meme images
    # ========================================================================
    
    print("=" * 60)
    print("Reactify BABYYY")
    print("=" * 60)
    
    detector = GestureDetector()
    IMAGE_FOLDER = "images"
    MAPPINGS_FILE = "mappings.json"
    mapper = GestureMapper(IMAGE_FOLDER, WINDOW_WIDTH, WINDOW_HEIGHT)
    mapper.load_mappings(MAPPINGS_FILE)

    if not mapper.list_images():
        print("\nNo images found in the images folder.")
        return
	
    blank_screen = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype=np.uint8)

    if not mapper.mapping:
        mapper.add_mapping("neutral", "no_hand", "apple.png")
        mapper.add_mapping("tongue_out", "no_hand", "appletongue.png")
        mapper.add_mapping("tongue_out", "unknown", "appletongue.png")
        mapper.add_mapping("surprised", "no_hand", "surprised.jpeg")
        mapper.add_mapping("surprised", "unknown", "surprised.jpeg")
        mapper.add_mapping("pouting", "no_hand", "IshowSpeed.jpeg")
        mapper.add_mapping("pouting", "unknown", "IshowSpeed.jpeg")
        mapper.add_mapping("neutral", "peace", "peaceout.jpeg")
        mapper.save_mappings(MAPPINGS_FILE)

    default_image = mapper.get_image("neutral", "no_hand")
    current_meme = default_image.copy() if default_image is not None else blank_screen.copy()
     

    # ========================================================================
    # STEP 2: Initialize webcam
    # ========================================================================
    
    # Open the default webcam (index 0)
    # If you have multiple cameras, try changing 0 to 1, 2, etc.

    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("\n[ERROR] Could not open webcam.")
        print("Please check:")
        print("  - Webcam is connected")
        print("  - No other application is using the webcam")
        print("  - Webcam permissions are enabled")
        return
    
    # Set webcam resolution (may not match exactly depending on hardware)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WINDOW_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_HEIGHT)
    
    print("[OK] Webcam initialized successfully!")
    
    # ========================================================================
    # STEP 3: Create display windows
    # ========================================================================
    
    # Create two windows: one for camera input, one for meme output
    cv2.namedWindow('Camera Input', cv2.WINDOW_NORMAL)
    cv2.namedWindow('Meme Output', cv2.WINDOW_NORMAL)
    
    # Set window sizes
    cv2.resizeWindow('Camera Input', WINDOW_WIDTH, WINDOW_HEIGHT)
    cv2.resizeWindow('Meme Output', WINDOW_WIDTH, WINDOW_HEIGHT)
    
    print("\n" + "=" * 60)
    print("[OK] Application started successfully!")
    print("=" * 60)
    print("\n[CAMERA] Windows opened")
    print("[TONGUE] Stick your tongue out to change the meme!")
    print("[QUIT] Press 'q' to quit\n")
        
    # ========================================================================
    # STEP 4: Main detection loop
    # ========================================================================
    
    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()
        
        # Check if frame was captured successfully
        if not ret:
            print("\n[ERROR] Could not read frame from webcam.")
            break
        
        # Flip frame horizontally for mirror effect (makes it easier to use)
        # Without this, moving left would make the image move right
        frame = cv2.flip(frame, 1)
        
        # Ensure frame matches our target window size
        frame = cv2.resize(frame, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Convert BGR (OpenCV format) to RGB (MediaPipe format)
        # OpenCV uses BGR color order, but MediaPipe expects RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # chec both face and hand
        face_results = detector.process_face(rgb_frame)
        hand_results = detector.process_hands(rgb_frame)

        face_gesture = "neutral"
        hand_gesture = "no_hand"


        
        # ====================================================================
        # Detect and select appropriate meme
        # ====================================================================
        
        if hand_results and hand_results.multi_hand_landmarks:
            hand_gesture = detector.detect_hand_gesture(hand_results.multi_hand_landmarks)


        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                face_gesture = detector.detect_face_gesture(face_landmarks)
                break

        mapped_image = mapper.get_image(face_gesture, hand_gesture)

        if mapped_image is not None:
            current_meme = mapped_image.copy()
        elif (not face_results or not face_results.multi_face_landmarks) and hand_gesture == "no_hand":
            current_meme = blank_screen.copy()
        else:
            default_image = mapper.get_image("neutral", "no_hand")
            current_meme = default_image.copy() if default_image is not None else blank_screen.copy()

        if face_results and face_results.multi_face_landmarks:
            if face_gesture == "tongue_out":
                cv2.putText(frame, "TONGUE OUT!", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            elif face_gesture == "surprised":
                cv2.putText(frame, "SURPRISED", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 2)
            elif face_gesture == "pouting":
                cv2.putText(frame, "POUTING", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 255), 2)
            else:
                cv2.putText(frame, "NEUTRAL", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        else:
            cv2.putText(frame, "No face detected", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.putText(frame, "Hand: " + hand_gesture, (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # ====================================================================
        # Display windows
        # ====================================================================
        
        # Show camera feed with detection status
        cv2.imshow('Camera Input', frame)
        
        # Show current meme image
        cv2.imshow('Meme Output', current_meme)
        
        # ====================================================================
        # Handle keyboard input
        # ====================================================================
        
        # Wait 1ms for key press, check if 'q' was pressed
        # The & 0xFF is needed for compatibility with some systems
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n[QUIT] Quitting application...")
            break
    
    # ========================================================================
    # STEP 5: Cleanup and exit
    # ========================================================================
    
    # Release webcam
    cap.release()
    
    # Close all OpenCV windows
    cv2.destroyAllWindows()
    
    # Close MediaPipe Face Mesh
    detector.face_mesh.close()
    detector.hands.close()
    
    print("[OK] Application closed successfully.")
    print("Thanks for using Tongue Detection Meme Display!\n")

if __name__ == "__main__":
    main()

