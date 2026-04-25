import os
import shutil
from GestureMapper import GestureMapper

print("Running upload test.........................")

base_dir = os.getcwd()
image_dir = os.path.join(base_dir, "images")

mapper = GestureMapper(image_dir, 300, 300)


test_file = "test_upload.png"


import cv2
import numpy as np


img = np.zeros((100, 100, 3), dtype=np.uint8)
cv2.imwrite(test_file, img)

destination = os.path.join(image_dir, test_file)



if not os.path.exists(destination):
    shutil.copy(test_file, destination)

mapper.load_images()


try:
    mapper.add_mapping("surprised", "no_hand", test_file)
    print("Upload test passed: mapping added successfully")
except Exception as e:
    print("Upload test failed:", e)





os.remove(test_file)
if os.path.exists(destination):
    os.remove(destination)