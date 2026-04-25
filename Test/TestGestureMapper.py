import unittest
import os
import shutil
import cv2
import numpy as np

from GestureMapper import GestureMapper


class TestGestureMapper(unittest.TestCase):



    def setUp(self):
        self.test_folder = "test_images"

        if not os.path.exists(self.test_folder):
            os.makedirs(self.test_folder)

        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(os.path.join(self.test_folder, "test_meme.png"), test_img)

        self.mapper = GestureMapper(self.test_folder, 200, 200)


    def tearDown(self):
        shutil.rmtree(self.test_folder)


    def test_list_images(self):
        images = self.mapper.list_images()
        self.assertIn("test_meme.png", images)


    def test_add_mapping_and_get_image(self):
        self.mapper.add_mapping("surprised", "no_hand", "test_meme.png")
        result = self.mapper.get_image("surprised", "no_hand")
        self.assertIsNotNone(result)


    def test_face_only_fallback(self):
        self.mapper.add_mapping("pouting", "no_hand", "test_meme.png")
        result = self.mapper.get_image("pouting", "hands_together")
        self.assertIsNotNone(result)


    def test_invalid_mapping_image(self):
        with self.assertRaises(ValueError):
            self.mapper.add_mapping("surprised", "no_hand", "missing.png")


    def test_unknown_gesture_returns_none(self):
        result = self.mapper.get_image("unknown", "unknown")
        self.assertIsNone(result)




if __name__ == "__main__":
    unittest.main()