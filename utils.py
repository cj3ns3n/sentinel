from datetime import datetime
import cv2

def addText(img, txt, position, color=(0, 0, 255)):
  cv2.putText(img, txt, position, cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

def getTimestampId():
  return datetime.now().strftime('%Y-%m-%d:%H:%M:%S.%f')[:-3]
