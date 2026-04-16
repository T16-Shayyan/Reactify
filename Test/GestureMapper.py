import os
import json
import cv2


class GestureMapper:
    def __init__(self, image_folder, width, height):
        self.image_folder = image_folder
        self.width = width
        self.height = height
        self.mapping = {}
        self.images = {}
        self.load_images()

    def load_images(self):
        self.images = {}

        if not os.path.exists(self.image_folder):
            os.makedirs(self.image_folder)

        for filename in os.listdir(self.image_folder):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(self.image_folder, filename)
                img = cv2.imread(path)

                if img is not None:
                    img = cv2.resize(img, (self.width, self.height))
                    self.images[filename] = img

    def list_images(self):
        return sorted(self.images.keys())

    def add_mapping(self, face, hand, image_name):
        if image_name in self.images:
            self.mapping[(face, hand)] = image_name
        else:
            raise ValueError(f"Image '{image_name}' not found in image folder.")

    def get_image(self, face, hand):
        image_name = None

        if (face, hand) in self.mapping:
            image_name = self.mapping[(face, hand)]
        elif (face, "no_hand") in self.mapping:
            image_name = self.mapping[(face, "no_hand")]
        elif ("neutral", hand) in self.mapping:
            image_name = self.mapping[("neutral", hand)]

        if image_name and image_name in self.images:
            return self.images[image_name]

        return None

    def save_mappings(self, json_path):
        data = []

        for (face, hand), image_name in self.mapping.items():
            data.append({
                "face": face,
                "hand": hand,
                "image": image_name
            })

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_mappings(self, json_path):
        self.mapping = {}

        if not os.path.exists(json_path):
            return

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            face = item["face"]
            hand = item["hand"]
            image_name = item["image"]

            if image_name in self.images:
                self.mapping[(face, hand)] = image_name