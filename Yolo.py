import cv2
import numpy as np

# read class names from text file

classes = None
with open('obj.names', 'r') as f:
    classes = [line.strip() for line in f.readlines()]

# generate different colors for different classes
COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

# read pre-trained model and config file
net = cv2.dnn.readNet('Weights file path', 'yolov4-obj.cfg')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

# function to get the output layer names
# in the architecture
def get_output_layers(net):
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return output_layers


# function to draw bounding box on the detected object with class name
def draw_bounding_box(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = str(classes[class_id])
    color = COLORS[class_id]
    cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)
    cv2.putText(img, "%s" % label, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    print(label, confidence)


def classify(frame):
    Width = frame.shape[1]
    Height = frame.shape[0]
    scale = 0.00392
    # create input blob
    blob = cv2.dnn.blobFromImage(frame, scale, (416, 416), (0, 0, 0), True, crop=False)
    # set input blob for the network
    net.setInput(blob)
    # run inference through the network
    # and gather predictions from output layers
    outs = net.forward(get_output_layers(net))
    # initialization
    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.65
    nms_threshold = 0.5
    # for each detection from each output layer
    # get the confidence, class id, bounding box params
    # and ignore weak detections (confidence < 0.5)
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
    # apply non-max suppression
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
    # go through the detections remaining
    # after nms and draw bounding box
    for i in indices:
        i = i[0]
        box = boxes[i]
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]
        draw_bounding_box(frame, class_ids[i], confidences[i], round(x), round(y), round(x + w), round(y + h))

    # display output image
    cv2.imshow("object detection", frame)
    # wait until any key is pressed
    # cv2.waitKey()

# function to take Region of interest
def ROI(frame):
    length, width = frame.shape[:2]
    mask = np.zeros((length, width), dtype=np.uint8)
    # Rectangle
    pt1, pt2 = (width // 4, length // 4), (width * 3 // 4, length * 3 // 4)
    cv2.rectangle(mask, pt1, pt2, (255, 255, 255), 3)
    cv2.rectangle(mask, (0, length * 3 // 8), (width, length * 5 // 8), (0, 0, 0), -1)
    cv2.rectangle(mask, (width * 3 // 8, 0), (width * 5 // 8, length), (0, 0, 0), -1)
    # + Sign
    cv2.line(mask, (width // 2, length // 2 - 10), (width // 2, length // 2 + 10), (255, 255, 255), 2)
    cv2.line(mask, (width // 2 - 10, length // 2), (width // 2 + 10, length // 2), (255, 255, 255), 2)
    mask_color = [0, 255, 0]
    colored_mask = cv2.merge([np.multiply(mask, mask_color[2] / 255), np.multiply(mask, mask_color[1] / 255),
                              np.multiply(mask, mask_color[0] / 255)])
    colored_mask = colored_mask.astype(np.uint8)
    combo = cv2.addWeighted(frame, 1, colored_mask, 1, 1)
    cv2.imshow("IMG", combo)
    return frame[pt1[1]:pt2[1], pt1[0]:pt2[0]]


if __name__ == '__main__':
    # Image of the shape you want to classify
    # image = cv2.imread("D:\Aquaphoton\YOLO\\fcf3a917-4a86-4546-822c-52b4affa1ba7.jpg")
    # classify(image)
    # cv2.waitKey(0)

    # Video of the shape you want to classify
    cap = cv2.VideoCapture("Video path")
    i = 0
    while True:
        i += 1
        ret, frame = cap.read()
        if i % 15:
            # cv2.imshow("CAM", frame)
            roi = ROI(frame)     # Region of interest
            classify(roi)        # classify the shape
            cv2.waitKey(1)

    # save output image to disk
    # cv2.imwrite("object-detection.jpg", image)

    # release resources
    cv2.destroyAllWindows()
