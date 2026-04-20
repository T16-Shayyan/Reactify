import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import os

from GestureDetector import GestureDetector
from GestureMapper import GestureMapper

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Reactify")
        self.geometry("1400x900")
        self.configure(fg_color="black")

        # Make window start invisible
        self.attributes("-alpha", 0.0)

        # ===== STARTUP FRAME =====
        self.startup_frame = ctk.CTkFrame(self, fg_color="black")
        self.startup_frame.pack(fill="both", expand=True)

        self.title_label = ctk.CTkLabel(
            self.startup_frame,
            text="Reactify",
            font=("Arial", 80, "bold"),
            text_color="#8b5cf6"
        )
        self.title_label.place(relx=0.5, rely=0.5, anchor="center")

        self.fade_in()

    # =============================
    # SMOOTH FADE IN
    # =============================
    def fade_in(self):
        alpha = self.attributes("-alpha")

        if alpha < 1.0:
            alpha += 0.05
            self.attributes("-alpha", alpha)
            self.after(15, self.fade_in)
        else:
            self.after(400, self.fade_out_title)

    # =============================
    # TITLE FADE OUT
    # =============================
    def fade_out_title(self):
        current_color = self.title_label.cget("text_color")

        # Gradually darken text
        fade_steps = 20
        duration = 15

        def step(i):
            if i <= fade_steps:
                fade_ratio = 1 - (i / fade_steps)
                r = int(139 * fade_ratio)
                g = int(92 * fade_ratio)
                b = int(246 * fade_ratio)
                color = f"#{r:02x}{g:02x}{b:02x}"
                self.title_label.configure(text_color=color)
                self.after(duration, lambda: step(i + 1))
            else:
                self.start_main_app()

        step(0)

    # =============================
    # MAIN APP LOAD
    # =============================
    def start_main_app(self):
        self.startup_frame.destroy()
        self.configure(fg_color="#0a0a0f")

        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_dir = os.path.join(base_dir, "images")
        mapping_path = os.path.join(base_dir, "mappings.json")

        self.detector = GestureDetector()
        self.mapper = GestureMapper(image_dir, WINDOW_WIDTH, WINDOW_HEIGHT)

        self.mapper.load_images()
        self.mapper.load_mappings(mapping_path)

        self.cap = cv2.VideoCapture(0)
        self.current_meme = self.get_default_meme()
        self.running = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.camera_label = ctk.CTkLabel(self, text="", fg_color="#0a0a0f")
        self.camera_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.meme_label = ctk.CTkLabel(self, text="", fg_color="#0a0a0f")
        self.meme_label.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.status_frame = ctk.CTkFrame(self, fg_color="#0a0a0f")
        self.status_frame.grid(row=1, column=0, columnspan=2, pady=10)

        self.face_label = ctk.CTkLabel(self.status_frame, text="Face: -", font=("Arial", 16))
        self.face_label.pack(side="left", padx=15)

        self.hand_label = ctk.CTkLabel(self.status_frame, text="Hand: -", font=("Arial", 16))
        self.hand_label.pack(side="left", padx=15)

        self.button_frame = ctk.CTkFrame(self, fg_color="#0a0a0f")
        self.button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.upload_btn = ctk.CTkButton(
            self.button_frame,
            text="Upload Image",
            fg_color="#2563eb",
            command=lambda: print("Upload clicked")
        )
        self.upload_btn.pack(side="left", padx=15)

        self.quit_btn = ctk.CTkButton(
            self.button_frame,
            text="Quit",
            fg_color="red",
            command=self.quit_app
        )
        self.quit_btn.pack(side="left", padx=15)

        self.after(200, self.start_camera)

    # =============================
    def get_default_meme(self):
        default = self.mapper.get_image("neutral", "no_hand")

        if default is not None:
            return default.copy()

        if self.mapper.images:
            return list(self.mapper.images.values())[0].copy()

        return np.full((WINDOW_HEIGHT, WINDOW_WIDTH, 3), 40, dtype=np.uint8)

    # =============================
    def start_camera(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.update_loop, daemon=True).start()

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

            self.face_label.configure(text=f"Face: {face_gesture}")
            self.hand_label.configure(text=f"Hand: {hand_gesture}")

            cam_img = Image.fromarray(rgb)
            meme_img = Image.fromarray(cv2.cvtColor(self.current_meme, cv2.COLOR_BGR2RGB))

            cam_tk = ImageTk.PhotoImage(cam_img)
            meme_tk = ImageTk.PhotoImage(meme_img)

            self.camera_label.configure(image=cam_tk)
            self.camera_label.image = cam_tk

            self.meme_label.configure(image=meme_tk)
            self.meme_label.image = meme_tk

    def quit_app(self):
        self.running = False
        self.cap.release()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()