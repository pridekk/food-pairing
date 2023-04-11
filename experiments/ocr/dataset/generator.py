import os
from datetime import datetime
from glob import glob
from trdg.generators import GeneratorFromStrings
from random import shuffle, randint
import re
import yaml


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

    with open("../../automation/emart.txt", "r", encoding="UTF-8") as emart:
        print("[INFO] Reading Emart names")
        for item in emart.readlines():
            wine_list.append(item.replace("\n", ""))

    shuffle(wine_list)
    return ["아발론까쇼", "샤또"] + wine_list


def get_chars(items):

    char_set = {"0", "1", "2", "3", "4", "5", '6', '7', '8', '9'}
    for item in items:
        char_set = char_set.union([char for char in item])

    return "".join(char_set)


def get_prices():
    p_list = set()
    for i in range(1, 200):
        rd = randint(5, 200)
        p_list.add(str(rd*100))
    return list(p_list)


custom_config = {
    "network_params": {
        "input_channel": 1,
        "output_channel": 256,
        "hidden_size": 256
    },
    "imgH": 64,
    "lang_list": ["ko"],
    "character_list": ""
}

if __name__ == "__main__":
    now_str = datetime.now().strftime("%Y%m%d_%H%M")
    wines = get_wine_names()
    print(f"'{get_chars(wines)}'")

    data = wines + get_prices()
    shuffle(data)

    with open("./custom.yaml", "w", encoding="UTF-8") as f:
        custom_config["character_list"] = get_chars(wines)
        yaml.dump(custom_config, f, encoding="UTF-8", indent=4, allow_unicode=True)

    LIMIT = {
        "training": 100000,
        "validation": 10000,
        "test": 100,
    }
    for stage in ["training", "validation", "test"]:

        # The generators use the same arguments as the CLI, only as parameters
        print(f"[INFO] Start Gen {stage} samples: {LIMIT[stage]}")
        generator = GeneratorFromStrings(
            data,
            language="ko",
            # distorsion_type=3,
            background_type=0,
            fonts=[
                os.path.abspath(item) for item in glob("./fonts/ko/*") if item.endswith("ttf")
            ]
        )
        cnt = 0
        # os.mkdir(now_str)
        os.makedirs(f"{now_str}/{stage}/images", exist_ok=True)
        gt_str = ""
        for img, lbl in generator:
            if cnt >= LIMIT[stage]:
                print(f"[INFO] {stage} Done")
                break
            if img is None:
                print(f"[INFO] Img {img}, lbl {lbl}")
                continue
            if stage == "test":
                image_file = f"images/{str(cnt).zfill(8)}_{lbl}.jpg"
            else:
                image_file = f"images/{str(cnt).zfill(8)}.jpg"
            with open(f"{now_str}/{stage}/{image_file}", "w") as f:
                img.save(f)
            gt_str += f"{image_file}\t{lbl}\n"

            cnt += 1

        with open(f"{now_str}/{stage}/gt.txt", "w", encoding="UTF-8") as f:
            f.write(gt_str)
