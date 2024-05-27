import cv2
import numpy as np
import pytesseract
import torch
from torchvision import transforms
from PIL import Image
from pdf2image import convert_from_path


def pdf_to_images(pdf_path):
    images = convert_from_path(pdf_path)
    return images


def detect_text_regions(image):
    net = cv2.dnn.readNet('frozen_east_text_detection.pb')

    orig = image.copy()
    (H, W) = image.shape[:2]

    layerNames = [
        "feature_fusion/Conv_7/Sigmoid",
        "feature_fusion/concat_3"]

    newW, newH = (320, 320)
    rW = W / float(newW)
    rH = H / float(newH)
    image = cv2.resize(image, (newW, newH))

    blob = cv2.dnn.blobFromImage(image, 1.0, (newW, newH),
                                 (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)

    (rects, confidences) = decode_predictions(scores, geometry)
    boxes = non_max_suppression(np.array(rects), probs=confidences)

    results = []
    for (startX, startY, endX, endY) in boxes:
        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)
        results.append((startX, startY, endX, endY))

    return results


def decode_predictions(scores, geometry):
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []

    for y in range(0, numRows):
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        for x in range(0, numCols):
            if scoresData[x] < 0.5:
                continue

            (offsetX, offsetY) = (x * 4.0, y * 4.0)
            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)

            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])

    return (rects, confidences)


def non_max_suppression(boxes, probs=None, overlapThresh=0.3):
    if len(boxes) == 0:
        return []

    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")

    pick = []
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = y2

    if probs is not None:
        idxs = probs

    idxs = np.argsort(idxs)

    while len(idxs) > 0:
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        overlap = (w * h) / area[idxs[:last]]

        idxs = np.delete(idxs, np.concatenate(([last],
                                               np.where(overlap > overlapThresh)[0])))

    return boxes[pick].astype("int")


def extract_text(image, boxes):
    results = []
    for (startX, startY, endX, endY) in boxes:
        roi = image[startY:endY, startX:endX]
        config = ("-l eng --oem 1 --psm 7")
        text = pytesseract.image_to_string(roi, config=config)
        results.append(((startX, startY, endX, endY), text))
    return results


def extract_text_with_context(image, boxes):
    results = []
    for (startX, startY, endX, endY) in boxes:
        margin = 10
        startY_with_context = max(0, startY - margin)
        endY_with_context = min(image.shape[0], endY + margin)
        startX_with_context = max(0, startX - margin)
        endX_with_context = min(image.shape[1], endX + margin)

        roi_with_context = image[startY_with_context:endY_with_context,
                                 startX_with_context:endX_with_context]

        text_with_context = pytesseract.image_to_string(roi_with_context)
        results.append(((startX, startY, endX, endY), text_with_context))

    return results


# class CRNNModel(torch.nn.Module):
#     def __init__(self):
#         super(CRNNModel, self).__init__()
#         # Define the CRNN model architecture
#         # This is a placeholder, you'll need to load an actual pre-trained model
#         pass

#     def forward(self, x):
#         # Define forward pass
#         pass


# crnn = CRNNModel()
# # Load the actual model weights
# crnn.load_state_dict(torch.load('crnn_model.pth'))
# crnn.eval()


# def extract_text(image, boxes):
#     results = []
#     transform = transforms.Compose([
#         transforms.Grayscale(),
#         transforms.Resize((32, 128)),
#         transforms.ToTensor(),
#         transforms.Normalize((0.5,), (0.5,))
#     ])

#     for (startX, startY, endX, endY) in boxes:
#         roi = image[startY:endY, startX:endX]
#         roi = Image.fromarray(roi)
#         roi = transform(roi)
#         roi = roi.unsqueeze(0)

#         with torch.no_grad():
#             output = crnn(roi)
#             # You'll need to implement the decode_output function
#             text = decode_output(output)

#         results.append(((startX, startY, endX, endY), text))
#     return results


# def decode_output(output, char_set):
#     _, preds = output.max(2)
#     preds = preds.transpose(1, 0).contiguous().view(-1)
#     preds_size = torch.IntTensor([preds.size(0)])
#     raw_pred = torch.IntTensor(preds)
#     sim_pred = raw_pred

#     # Convert the indices to characters
#     decoded_text = ''
#     for i in range(len(sim_pred)):
#         if sim_pred[i] != 0 and (not (i > 0 and sim_pred[i - 1] == sim_pred[i])):
#             decoded_text += char_set[sim_pred[i]]

#     return decoded_text
