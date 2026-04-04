"""
Tongue Detection Meme Display
A MediaPipe + OpenCV application that detects when your tongue is out
and displays different meme images accordingly.

See TUTORIAL.md for detailed explanations
"""

import cv2
import mediapipe as mp
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
    

        # ========================================================================
        # CHECK IF OUR MEMES ARE THERE FIRST HERE
        # ========================================================================
    
    # Check if required image files exist
    if not os.path.exists('apple.png'):
        print("\n[ERROR] apple.png not found!")
        print("Please add this image to the project directory.")
        print("This image is displayed when tongue is NOT out.")
        return
    
    if not os.path.exists('appletongue.png'):
        print("\n[ERROR] appletongue.png not found!")
        print("Please add this image to the project directory.")
        print("This image is displayed when tongue IS out.")
        return
    
    # Load images using OpenCV (images are loaded in BGR format)
    apple_img = cv2.imread('apple.png')
    appletongue_img = cv2.imread('appletongue.png')
    
    # Verify images loaded successfully
    if apple_img is None or appletongue_img is None:
        print("\n[ERROR] Could not load meme images.")
        print("Please check that the files are valid PNG images.")
        return
    
    print("[OK] Meme images loaded successfully!")
    
    # Resize images to fit the output window
    # This ensures consistent display regardless of original image size
    apple_img = cv2.resize(apple_img, (WINDOW_WIDTH, WINDOW_HEIGHT))
    appletongue_img = cv2.resize(appletongue_img, (WINDOW_WIDTH, WINDOW_HEIGHT))
    
        # ========================================================================
        # our blank screen and mappers and detectors add more here later
        # ========================================================================


    #dont forget add more meme here
    #hereeeeee
    #hereeeeee
    #hereeeee
    #hereeee
    detector = GestureDetector()
    mapper = GestureMapper()

    mapper.add_mapping("tongue_out", "no_hand", appletongue_img)
    mapper.add_mapping("tongue_out", "unknown", appletongue_img)

    mapper.add_mapping("neutral", "no_hand", apple_img)
    mapper.add_mapping("neutral", "unknown", apple_img)

    blank_screen = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype=np.uint8)

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
    
    # Default state - start with normal apple image
    current_meme = apple_img.copy()
    
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
        hand_gesture = detector.detect_hand_gesture(hand_results.multi_hand_landmarks)


        
        # ====================================================================
        # Detect tongue and select appropriate meme
        # ====================================================================
        
        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                face_gesture = detector.detect_face_gesture(face_landmarks)
                break

        mapped_image = mapper.get_image(face_gesture, hand_gesture)

        if mapped_image is not None:
            current_meme = mapped_image.copy()
        elif not face_results.multi_face_landmarks and hand_gesture == "no_hand":
            current_meme = blank_screen.copy()
        else:
            current_meme = apple_img.copy()

        if face_results.multi_face_landmarks:
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

