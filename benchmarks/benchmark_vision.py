import time
import os
import shutil
import tempfile
from PIL import Image
from vision.llava_client import VisionModel

MODEL = "llava-next"


def main():
    vision = VisionModel(MODEL)
    tmp_dir = tempfile.mkdtemp()
    images = []
    for i in range(5):
        path = os.path.join(tmp_dir, f"img_{i}.png")
        Image.new("RGB", (1, 1), color="white").save(path)
        images.append(path)

    start = time.time()
    try:
        for img in images:
            vision.describe(img)
    finally:
        end = time.time()
        shutil.rmtree(tmp_dir)
    print("Vision throughput", len(images) / (end - start), "img/s")


if __name__ == "__main__":
    main()
