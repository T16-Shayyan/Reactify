import cv2

cap = cv2.VideoCapture(0)

print("Running camera test...")

if not cap.isOpened():
    print("Camera failed to open")
else:
    print("Camera opened successfully")

    ret, frame = cap.read()

    if ret:
        print("Frame captured successfully")
        print("Frame shape:", frame.shape)
    else:
        print("Failed to capture frame")


cap.release()