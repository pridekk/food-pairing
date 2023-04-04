from multiprocessing import freeze_support

import matplotlib.pyplot as plt
from ultralytics import YOLO
import cv2
import urllib
from PIL import Image


if __name__ == '__main__':
    freeze_support()
    model = YOLO("yolov8n.pt")

    model.train(cfg='default.yaml')
