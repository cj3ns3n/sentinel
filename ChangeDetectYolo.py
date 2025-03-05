from ultralytics import YOLO
import numpy as np
from time import time
import cv2
from logger import Logger


class ChangeDetectYolo:
  def __init__(self, modelName='yolo11s.pt', ignores=[], confidenceThreshold=0.3, areaDiffThreshold=5, logger=None):
    if logger:
      self.logger = logger
    else:
      self.logger = Logger('YoloChangeDetect')

    self.name = modelName
    self.logger.info('yolo model: "%s"' % modelName)
    self.model = YOLO(modelName)
    self.confidenceThreshold = confidenceThreshold
    self.areaDiffThreshold = areaDiffThreshold
    self.ignores = ignores
  # end def

  def process(self, prevEvent, nextEvent):
    startTime = time()
    self.logger.info('yolo "%s" change detection' % self.name)
    nextImg = nextEvent.originalImage
    #nextImg = cv2.fastNlMeansDenoisingColored(nextImg, None, 10, 10, 7, 21)
    self.logger.info('denoise time %f' % (time() - startTime))

    modelResp = self.model(nextImg)
    detections = modelResp[0]
    diffAreas = {}

    for data in detections.boxes.data.tolist():
      # extract the confidence (i.e., probability) associated with the detection
      confidence = float(data[4])
      self.logger.info('\tconfidence: ' + repr(confidence))

      # filter out weak detections by ensuring the
      # confidence is greater than the minimum confidence
      if confidence >= self.confidenceThreshold:
        id = int(data[5])
        name = '%03d_%s' % (id, detections.names[id])
        self.logger.info('detected: %s: %f' % (name, confidence))
        diffAreas[name] = (data[:4])
        # if the confidence is greater than the minimum confidence,
        # draw the bounding box on the frame
        #xmin, ymin, xmax, ymax = int(data[0]), int(data[1]), int(data[2]), int(data[3])
    # end for

    prevAois = {}
    if prevEvent.detections:
      self.logger.info('detections: ' + str(len(detections)))
      for detection in prevEvent.detections:
        self.logger.info('detection name: ' + detection['name'])
        if detection['name'] == self.name:
          prevAois = detection['diffAreas']

    if len(prevAois) > 0:
      self.logger.info('ADDING ** prev aois **')
      return {'diffAreas': self.findAOIs(prevAois, diffAreas), 'name': self.name}
    else:
      self.logger.info('ADDING ** no prev aois **')
      return {'diffAreas': diffAreas, 'name': self.name}

    self.logger.info('detect time %f' % (time() - startTime))
  # end def

  def findAOIs(self, prevAreas, nextAreas):
    aois = {}

    for name, nextArea in nextAreas.items():
      if name not in self.ignores:
        self.logger.info('curr name (%s) prev names (%s)' % (name, repr(prevAreas.keys())))
        if name in prevAreas:
          prevArea = prevAreas[name]
          dist = np.linalg.norm(np.array((prevArea[0], prevArea[1])) - np.array((nextArea[0], nextArea[1])))
          self.logger.info('dist 01 %f (%f)' % (dist, self.areaDiffThreshold))
          if dist > self.areaDiffThreshold:
            aois[name] = nextArea
          else:
            dist = np.linalg.norm(np.array((prevArea[2], prevArea[3])) - np.array((nextArea[2], nextArea[3])))
            self.logger.info('dist 02 %f (%f)' % (dist, self.areaDiffThreshold))
            if dist > self.areaDiffThreshold:
              aois[name] = nextArea
        else:
          self.logger.info('ADDING curr name (%s) prev names (%s)' % (name, repr(prevAreas.keys())))
          aois[name] = nextArea
      # end if
    # end for

    return aois
  # end def
# end class

if __name__ == '__main__':
  image1 = cv2.imread('test/img1.jpg')
  image2 = cv2.imread('test/img2.jpg')
  changeDetect = ChangeDetectYolo(image1, image2, 0.3)
  print(len(changeDetect.diffAreas))
