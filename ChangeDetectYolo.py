from ultralytics import YOLO
from time import time
import cv2
import math
from logger import Logger
from areaofinterest import AreaOfInterest
from aoitracker import AoiTracker
from hashlib import md5

class ChangeDetectYolo:
  def __init__(self, modelName='yolo11m.pt', ignores=[], confidenceThreshold=0.3, distThreshold=10, logger=None):
    if logger:
      self.logger = logger
    else:
      self.logger = Logger('YoloChangeDetect')

    self.name = modelName
    self.logger.info('yolo model: "%s"' % modelName)
    self.model = YOLO(modelName)
    self.confidenceThreshold = confidenceThreshold
    self.distThreshold = distThreshold
    self.ignores = ignores
    self.aoiTrackers = {}
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

    self.logger.info('detect time %f' % (time() - startTime))
    return {'diffAreas': self.findAOIs(diffAreas), 'name': self.name}
  # end def

  def findAOIs(self, nextAOIs):
    aois = {}

    keys = list(self.aoiTrackers)
    notFoundKeys = keys.copy()

    for name, nextAOI in nextAOIs.items():
      nextCenter = nextAOI.center()

      aoiCount = 0
      found = False
      self.logger.info('found %d aois' % len(keys))
      while not found and aoiCount < len(keys):
        self.logger.info('checking aoi %d' % aoiCount)

        try:
          aoiTracker = self.aoiTrackers[keys[aoiCount]]
          knownAoi = aoiTracker.generateAoi()
          if knownAoi.contains(nextCenter):
            found = True
            notFoundKeys.remove(keys[aoiCount])
            aoiTracker.addAoi(nextAOI.area)

            aoiCenter = knownAoi.center()
            dist = math.hypot(nextCenter[0] - aoiCenter[0], nextCenter[1] - aoiCenter[1])
            self.logger.info('dist: %0.1f' % dist)
            if dist > self.distThreshold:
              newAoi = aoiTracker.generateAoi()
              newAoi.annotate_cross_hairs.append(nextCenter)
              newAoi.annotate_circles.append(newAoi.center())
              newAoi.annotate_text.append('dist: %0.1f' % dist)
              aois[aoiTracker.name] = newAoi
            # end if
          # end if
        except Exception as ex:
          self.logger.error(str(ex))

        aoiCount += 1
      # end while

      if not found:
        nextArea = nextAOI.area
        name = name + '_' + md5((str(nextArea[0]) + str(nextArea[1]) + str(nextArea[2]) + str(nextArea[3])).encode()).hexdigest()[:4]
        nextAOI.name = name
        nextAOI.annotate_cross_hairs.append(nextAOI.center())
        aois[name] = nextAOI

        try:
          newTracker = AoiTracker(name, window_size=self.avgWindowSize)
          newTracker.addAoi(nextAOI.area)
          self.aoiTrackers[name] = newTracker
        except Exception as ex:
          self.logger.error(ex)
      # end if
    # end for

    # remove any inactive AOIs
    for notFound in notFoundKeys:
      self.aoiTrackers[notFound].addAoi(None)
      if not self.aoiTrackers[notFound].isActive():
        self.aoiTrackers.pop(notFound)
    # end for

    return aois
  # end def
# end class

if __name__ == '__main__':
  image1 = cv2.imread('test/img1.jpg')
  image2 = cv2.imread('test/img2.jpg')
  changeDetect = ChangeDetectYolo(image1, image2, 0.3)
  print(len(changeDetect.diffAreas))
