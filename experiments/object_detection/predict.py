from multiprocessing import freeze_support
import matplotlib.pyplot as plt
from ultralytics import YOLO
import cv2
from PIL import Image
from glob import glob
import easyocr
import numpy as np


def detect_text(path):
    """Detects text in the file."""
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')

    for text in texts:
        print('\n"{}"'.format(text.description))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])

        print('bounds: {}'.format(','.join(vertices)))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))


def extent_bounding_box(box: tuple):
    temp_box = list(box)
    temp_box[0] = box[0] - 0.1 * box[0]
    temp_box[1] = box[1]
    temp_box[2] = box[2] + 0.1 * box[2]
    temp_box[3] = box[3] + 0.2 * box[3]

    for idx in range(0, 4):
        if temp_box[idx] < 0:
            temp_box[idx] = 0

    return tuple(temp_box)


def label_box(box: tuple):
    temp_box = list(box)
    temp_box[0] = box[0] - 0.1 * (box[2] - box[0])
    temp_box[1] = box[3] - 0.2 * (box[3] - box[1])
    temp_box[2] = box[2] + 0.1 * (box[2] - box[0])
    temp_box[3] = box[3] + 0.2 * (box[3] - box[1])

    for idx in range(0, 4):
        if temp_box[idx] < 0:
            temp_box[idx] = 0

    return tuple(temp_box)


if __name__ == '__main__':
    freeze_support()
    model = YOLO("last.pt")
    reader = easyocr.Reader(['ko', 'en'])

    # model.train(cfg='default.yaml')
    for file in glob("./dataset/wines/test/wine*"):
        item = model(file)

        boxes = item[0].boxes

        cnt = 0
        for box in boxes:
            prob, label = round(float(box.conf[0]), 2), int(box.cls[0])

            if label != 1:
                continue

            bounding_box = box.xyxy
            bounding_box = tuple(int(edge) for edge in bounding_box[0])

            bounding_box = extent_bounding_box(bounding_box)

            file_name = file.split("\\")[-1]

            ori_image = Image.open(file)
            image = ori_image.crop(bounding_box)
            np_image = np.array(image)
            cv_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
            plt.savefig(f"result/{cnt}_{prob}_{label}_{file_name}",)
            # with open(f"result/{cnt}_{prob}_{label}_{file_name}", "w", encoding="UTF-8") as f:
            #     image.save(f)

            label_image = ori_image.crop(label_box(bounding_box))
            np_image = np.array(label_image)
            cv_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)

            result = reader.readtext(cv_image)

            THRESHOLD = 0.3

            for bbox, text, conf in result:
                if conf > THRESHOLD:
                    print(text)
                    print(bbox)
                    # cv2.rectangle(img, pt1=[bbox[0][0].astype('int'), bbox[0][1].astype('int')], pt2=[bbox[2][0].astype('int'), bbox[2][1].astype('int')], color=(0,255,0))
                    cv2.rectangle(cv_image, pt1=[int(bbox[0][0]), int(bbox[0][1])], pt2=[int(bbox[2][0]), int(bbox[2][1])],
                                  color=(0, 255, 0))

            plt.figure(figsize=(32, 32))
            plt.imshow(cv_image[:, :, ::-1])
            plt.axis('off')

            plt.savefig("test.png")

            detect_text("test.png")
            # plt.show()
            cnt += 1





    #
    # plt.imshow(result)