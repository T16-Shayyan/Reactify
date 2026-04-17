
import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import os
import shutil
from tkinter import filedialog

from GestureDetector import GestureDetector
from GestureMapper import GestureMapper

# ==============================
# CONFIG
# ==============================
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.configure(fg_color="#0a0a0f") #background color

        self.title("Reactify")
        self.geometry("1400x900")

        # ==============================
        # BACKEND
        # ==============================
        self.detector = GestureDetector()
        self.mapper = GestureMapper("images", WINDOW_WIDTH, WINDOW_HEIGHT)
        self.mapper.load_mappings("mappings.json")

        self.cap = cv2.VideoCapture(0)
        self.current_meme = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype=np.uint8)

        self.running = False

        # ==============================
        # UI LAYOUT
        # ==============================
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Camera
        self.camera_label = ctk.CTkLabel(
            self,
            text="",
            fg_color="#0a0a0f",
            corner_radius=20
        )
        self.camera_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Meme
        self.meme_label = ctk.CTkLabel(
            self,
            text="",
            fg_color="#0a0a0f",
            corner_radius=20
        )
        self.meme_label.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # ==============================
        # STATUS BAR
        # ==============================
        self.status_frame = ctk.CTkFrame(self, fg_color="#0a0a0f")
        self.status_frame.grid(row=1, column=0, columnspan=2, pady=10)

        self.face_label = ctk.CTkLabel(self.status_frame, text="Face: -", font=("Arial", 16))
        self.face_label.pack(side="left", padx=15)

        self.hand_label = ctk.CTkLabel(self.status_frame, text="Hand: -", font=("Arial", 16))
        self.hand_label.pack(side="left", padx=15)

        self.eye_label = ctk.CTkLabel(self.status_frame, text="Eyes: -", font=("Arial", 16))
        self.eye_label.pack(side="left", padx=15)

        # ==============================
        # BUTTONS
        # ==============================
        self.button_frame = ctk.CTkFrame(self, fg_color="#0a0a0f")
        self.button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.upload_btn = ctk.CTkButton(self.button_frame, text="Upload Image", command=self.upload)
        self.upload_btn.pack(side="left", padx=10)

        self.quit_btn = ctk.CTkButton(self.button_frame, text="Quit", fg_color="red", command=self.quit_app)
        self.quit_btn.pack(side="left", padx=10)

        # Start intro
        self.after(100, self.show_intro)

        # Safety fallback
        self.after(3500, self.start_camera)

    # ==============================
    # INTRO SCREEN
    # ==============================
    def show_intro(self):
        self.intro = ctk.CTkFrame(self, fg_color="black")
        self.intro.place(relwidth=1, relheight=1)

        label = ctk.CTkLabel(
            self.intro,
            text="Reactify",
            font=("Helvetica", 72, "bold"),
            text_color="#6366F1"
        )
        label.place(relx=0.5, rely=0.5, anchor="center")

        # Fade OUT by lowering opacity (no color change → no white flash)
        def fade(alpha=1.0):
            if alpha > 0:
                alpha -= 0.03
                try:
                    self.attributes("-alpha", alpha)  # fade whole window
                except:
                    pass
                self.after(20, fade, alpha)
            else:
                # restore full opacity
                self.attributes("-alpha", 1.0)

                if hasattr(self, "intro"):
                    self.intro.destroy()
                    del self.intro

                self.start_camera()

        self.after(1200, fade)
    # ==============================
    # BUTTONS
    # ==============================
    def upload(self):
        path = filedialog.askopenfilename()
        if path:
            filename = os.path.basename(path)
            dest = os.path.join("images", filename)
            shutil.copy(path, dest)
            self.mapper.load_images()
            print("Uploaded:", filename)

    def quit_app(self):
        self.running = False
        self.cap.release()
        self.destroy()

    # ==============================
    # CAMERA START
    # ==============================
    def start_camera(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.update_loop, daemon=True).start()

    # ==============================
    # MAIN LOOP
    # ==============================
    def update_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (WINDOW_WIDTH, WINDOW_HEIGHT))

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face = self.detector.process_face(rgb)
            hand = self.detector.process_hands(rgb)

            face_gesture = "neutral"
            hand_gesture = "no_hand"

            if hand and hand.multi_hand_landmarks:
                hand_gesture = self.detector.detect_hand_gesture(hand.multi_hand_landmarks)

            if face and face.multi_face_landmarks:
                face_gesture = self.detector.detect_face_gesture(face.multi_face_landmarks[0])

            mapped = self.mapper.get_image(face_gesture, hand_gesture)

            if mapped is not None:
                self.current_meme = mapped.copy()

            # ==============================
            # UPDATE STATUS TEXT
            # ==============================
            eye_state = "detected" if face and face.multi_face_landmarks else "none"

            def colorize(label, text, color):
                label.configure(text=text, text_color=color)

            colorize(self.face_label, f"Face: {face_gesture}",
                     "#22c55e" if face_gesture != "neutral" else "#eab308")

            colorize(self.hand_label, f"Hand: {hand_gesture}",
                     "#3b82f6" if hand_gesture != "no_hand" else "#9ca3af")

            colorize(self.eye_label, f"Eyes: {eye_state}",
                     "#a855f7" if eye_state != "none" else "#9ca3af")

            # ==============================
            # FIX COLOR DISPLAY
            # ==============================
            cam_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            meme_img = Image.fromarray(cv2.cvtColor(self.current_meme, cv2.COLOR_BGR2RGB))

            cam_tk = ImageTk.PhotoImage(cam_img)
            meme_tk = ImageTk.PhotoImage(meme_img)

            self.camera_label.configure(image=cam_tk)
            self.camera_label.image = cam_tk

            self.meme_label.configure(image=meme_tk)
            self.meme_label.image = meme_tk


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app = App()
    app.mainloop()