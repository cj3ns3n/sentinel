from ultralytics import YOLO
import numpy as np
from time import time
import cv2
from logger import Logger
from areaofinterest import AreaOfInterest


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
    self.avgCenters = {}
    self.avgWindowSize = 10
  # end def

  def process(self, prevEvent, nextEvent):
    startTime = time()
    self.logger.info('yolo "%s" change detection' % self.name)
    nextImg = nextEvent.originalImage
    #nextImg = cv2.fastNlMeansDenoisingColored(nextImg, None, 10, 10, 7, 21)
    #self.logger.info('denoise time %f' % (time() - startTime))

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
        diffAreas[name] = AreaOfInterest(name, data[:4])
        # if the confidence is greater than the minimum confidence,
        # draw the bounding box on the frame
        #xmin, ymin, xmax, ymax = int(data[0]), int(data[1]), int(data[2]), int(data[3])
    # end for

    prevAois = {}
    if prevEvent.detectors:
      self.logger.info('detections: ' + str(len(detections)))
      for detection in prevEvent.detectors:
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

  def findAOIs(self, prevAOIs, nextAOIs):
    aois = {}

    for name, nextAOI in nextAOIs.items():
      nextArea = nextAOI.area
      if name not in self.ignores:
        self.logger.info('curr name (%s) prev names (%s)' % (name, repr(prevAOIs.keys())))
        nextCenter = nextAOI.center()

        if name in self.avgCenters:
          dist = np.linalg.norm(np.array(self.avgPoint(self.avgCenters[name])) - np.array(nextAOI.center()))
          self.logger.info('dist %f (threshold: %f)' % (dist, self.areaDiffThreshold))
          nextAOI.annotate_text.append('dist: %0.1f' % dist)
          if dist > self.areaDiffThreshold:
            aois[name] = nextAOI
        else:
          self.logger.info('adding curr name (%s) prev names (%s)' % (name, repr(prevAOIs.keys())))
          aois[name] = nextAOI

        self.addCenter(nextCenter, name)
        nextAOI.annotate_cross_hairs.append(nextCenter)
        nextAOI.annotate_circles.append(self.avgPoint(self.avgCenters[name]))
      # end if
    # end for

    return aois
  # end def

  def avgPoint(self, points):
    xcoords = [point[0] for point in points]
    ycoords = [point[1] for point in points]

    xavg = sum(xcoords) / len(points)
    yavg = sum(ycoords) / len(points)

    return (xavg, yavg)
  # end def

  def addCenter(self, center, name):
    if center == None:
      if name in self.avgCenters:
        newAvgs = self.avgCenters[name][1:]
        if len(newAvgs) == 0:
          self.avgCenters.pop(name)
        else:
          self.avgCenters[name] = newAvgs
    else:
      if name in self.avgCenters:
        self.avgCenters[name].append(center)
      else:
        self.avgCenters[name] = [center]

      if len(self.avgCenters[name]) > self.avgWindowSize:
        self.avgCenters[name] = self.avgCenters[name][1:]
    # end if
# end class

if __name__ == '__main__':
  image1 = cv2.imread('test/img1.jpg')
  image2 = cv2.imread('test/img2.jpg')
  changeDetect = ChangeDetectYolo(image1, image2, 0.3)
  print(len(changeDetect.diffAreas))
