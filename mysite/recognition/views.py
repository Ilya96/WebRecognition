from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from .forms import RecognitionForm
import cv2
import argparse
import numpy as np
from collections import namedtuple
from PIL import Image

# Create your views here.


Args = namedtuple('Args', 'classes weights config')
args = Args(
    classes='yolov3.txt',
    weights='yolov3.weights',
    config='yolov3.cfg'
)

fs = FileSystemStorage()


def recognition(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('document')
        if not uploaded_file:
            return render(request, 'recognition/recognition_get.html')
        else:
            if not fs.exists(uploaded_file.name):
                fs.save(uploaded_file.name, uploaded_file)
            # uploaded_file_url = fs.url(filename)
            # print(uploaded_file_url)
            # print(uploaded_file.size)
            # print(uploaded_file.name)
            recognition_image('media/'+uploaded_file.name)
            return render(request, 'recognition/recognition.html', {'uploaded_file': "media/" + uploaded_file.name.split('.')[0] + "detection.jpg"})
    else:
        return render(request, 'recognition/recognition_get.html')


def recognition_image(uploaded_file_name):

    def get_output_layers(net):
        layer_names = net.getLayerNames()

        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

        return output_layers

    def draw_prediction(img, class_id, x, y, x_plus_w, y_plus_h):
        label = str(classes[class_id])

        color = COLORS[class_id]

        cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)

        cv2.putText(img, label, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    image = cv2.imread(uploaded_file_name)
    Width = image.shape[1]
    Height = image.shape[0]
    scale = 0.00392

    classes = None

    with open(args.classes, 'r') as f:
        classes = [line.strip() for line in f.readlines()]

    COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

    net = cv2.dnn.readNet(args.weights, args.config)

    blob = cv2.dnn.blobFromImage(image, scale, (416, 416), (0, 0, 0), True, crop=False)

    net.setInput(blob)

    outs = net.forward(get_output_layers(net))

    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.4

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * Width)
                center_y = int(detection[1] * Height)
                w = int(detection[2] * Width)
                h = int(detection[3] * Height)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])

    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    for i in indices:
        i = i[0]
        box = boxes[i]
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]
        draw_prediction(image, class_ids[i], round(x), round(y), round(x + w), round(y + h))

    cv2.imwrite(uploaded_file_name.split('.')[0] + "detection.jpg", image)
    cv2.destroyAllWindows()
