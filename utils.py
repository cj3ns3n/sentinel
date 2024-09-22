from datetime import datetime
import cv2

def addText(img, txt, position):
  cv2.putText(img, txt, position, cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

def getTimestampId():
  return datetime.now().strftime('%Y-%m-%d:%H:%M:%S.%f')[:-3]
