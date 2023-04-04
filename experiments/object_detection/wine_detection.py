import cv2
import numpy as np
print(cv2.__version__)

img = cv2.imread('./images/oven.jpg')

# YOLOv3 모델 구성
model = cv2.dnn.readNetFromDarknet('yolov3.cfg', 'yolov3.weights')

# 모델의 클래스 이름 불러오기
classes = []
with open('coco.names', 'r') as f:
    classes = [line.strip() for line in f.readlines()]

# 모델의 출력 레이어 이름 가져오기
layer_names = model.getLayerNames()
output_layers = [layer_names[i - 1] for i in model.getUnconnectedOutLayers()]

# 객체 검출 함수 정의
def detecting_objects(img):
    # 이미지 전처리
    height, width, channels = img.shape
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

    # 모델에 입력
    model.setInput(blob)

    # 모델 추론
    outs = model.forward(output_layers)

    # 결과 저장할 리스트 초기화
    class_ids = []
    confidences = []
    boxes = []

    # 결과 처리
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:
                # 객체의 위치 계산
                # 객체의 위치 계산
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # 객체의 경계 상자 좌표 계산
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

                # 비최대 억제(non-maximum suppression) 수행
            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

            # 결과 출력
            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    confidence = confidences[i]
                    color = (255, 0, 0)
                    cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(img, label + ' ' + str(round(confidence, 2)), (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                color, 2)

            # 결과 반환
            return img
# 객체 검출 수행
detected_img = detecting_objects(img)

# 결과 이미지 출력
cv2.imshow('Detected Image', detected_img)
cv2.waitKey(0)
cv2.destroyAllWindows()