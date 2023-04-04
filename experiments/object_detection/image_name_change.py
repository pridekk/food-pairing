from glob import glob
import os
from datetime import datetime
import uuid

files = glob("./images/*")

print(files)

now = datetime.now().strftime("%Y-%m-%d_%H%M%S")

cnt = 0
for file in files:
    if "food-pairing" not in file:
        ext = file.split(".")[-1]
        new_file = f"./images/food-pairing-{now}-{uuid.uuid4()}.{ext}"
        print(f"[INFO] Changing a file name from {file} to {new_file}")
        os.rename(file, new_file)
        cnt += 1


print(f"{cnt} Changed")
