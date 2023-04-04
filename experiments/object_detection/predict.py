from multiprocessing import freeze_support

import matplotlib.pyplot as plt
from ultralytics import YOLO
import cv2
import urllib
from PIL import Image
from glob import glob

if __name__ == '__main__':
    freeze_support()
    model = YOLO("last.pt")

    # model.train(cfg='default.yaml')
    for file in glob("./dataset/wines/test/clip*"):
        result = model(file)
        #
        pl = result[0].plot()
        #
        name = "".join(file.split(".")[:-1])
        name = name.split("\\")[-1]
        Image.fromarray(pl).save(f"result/result_{name}.jpg")



    #
    # plt.imshow(result)