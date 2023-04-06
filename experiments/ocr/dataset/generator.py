import os
from PIL import Image
from datetime import datetime
from trdg.utils import load_dict, load_fonts
from glob import glob
from trdg.generators import GeneratorFromStrings
from random import shuffle
import re

def get_all_wine_characters():
    files = glob("../../automation/wine_info/*.json")

    char_set = set()

    for file in files:
       char_set = char_set.union(set([char for char in file if char not in "_/\\-.'json"]))

    for number in range(0, 10):
        char_set.add(str(number))

    char_list = list(char_set)
    shuffle(char_list)

    print(f"[INFO] char: len{len(char_list)}")
    return char_list


def get_wine_names():
    wine_files = glob("../../automation/wine_info/*.json")
    wine_2x_list = [re.split(',| ', wine.replace("'", "").replace("°", "").replace("+", "").split("-")[-1].split(".")[0].strip()) for wine in wine_files]

    wine_list = sum(wine_2x_list, [])
    wine_list = [item for item in wine_list if len(item) > 0]
    shuffle(wine_list)
    return wine_list


def get_chars(items):
    char_set = set()
    for item in items:
        char_set = char_set.union([char for char in item])

    return "".join(char_set)


if __name__ == "__main__":
    now_str = datetime.now().strftime("%Y%m%d_%H%M")
    wines = get_wine_names()
    print(f"'{get_chars(wines)}'")
    cnt_limit = 100
    for stage in ["training", "validation"]:
        for target in ["MJ", "ST"]:
            # The generators use the same arguments as the CLI, only as parameters
            print(f"[INFO] Start Gen {stage}/{target} samples: {cnt_limit}")
            generator = GeneratorFromStrings(
                wines,
                blur=1,
                random_blur=True,
                language="ko",
                fonts=[
                    os.path.abspath(item) for item in glob("./fonts/ko/*") if item.endswith("ttf")
                ]
            )
            cnt = 0
            # os.mkdir(now_str)
            os.makedirs(f"{now_str}/{stage}/{target}/images", exist_ok=True)
            gt_str = ""
            for img, lbl in generator:
                if cnt >= cnt_limit:
                    print(f"[INFO] {stage}/{target} Done")
                    break
                if img is None:
                    print(f"[INFO] Img {img}, lbl {lbl}")
                    continue
                image_file = f"images/{str(cnt).zfill(8)}_{lbl.replace(' ', '')}.jpg"
                with open(f"{now_str}/{stage}/{target}/{image_file}", "w") as f:
                    img.save(f)
                gt_str += f"{image_file}\t{lbl}\n"

                cnt += 1

            with open(f"{now_str}/{stage}/{target}/gt.txt", "w", encoding="UTF-8") as f:
                f.write(gt_str)
