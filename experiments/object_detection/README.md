### 학습 실행
yolo detect train data=coco128.yaml model=yolov8n.pt epochs=100 imgsz=640 pretrained=True

### 마지막 학습 시점에서 재시작
yolo detect train resume model=runs/detect/train5/weights/last.pt![](dataset/wines/test/KakaoTalk_20230404_104430960_03.jpg)