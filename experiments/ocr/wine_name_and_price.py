import easyocr
import cv2

import matplotlib.pyplot as plt


reader = easyocr.Reader(['ko'], recog_network='custom')

img_path = 'images/tag1.JPG'
img = cv2.imread(img_path)


if __name__ == "__main__":
  result = reader.readtext(img_path)

  THRESHOLD = 0.01


  for bbox, text, conf in result:
    if conf > THRESHOLD:
      print(text)
      print(bbox)
      # cv2.rectangle(img, pt1=[bbox[0][0].astype('int'), bbox[0][1].astype('int')], pt2=[bbox[2][0].astype('int'), bbox[2][1].astype('int')], color=(0,255,0))
      cv2.rectangle(img, pt1=[int(bbox[0][0]), int(bbox[0][1])], pt2=[int(bbox[2][0]), int(bbox[2][1])], color=(0,255,0))

  plt.figure(figsize=(32,32))
  plt.imshow(img[:, :, ::-1])
  plt.axis('off')
  plt.show()
