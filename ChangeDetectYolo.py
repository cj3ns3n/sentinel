from ultralytics import YOLO
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
    self.logger.info('yolo "%s" change detection' % self.name)
    nextImg = nextEvent['img']

    modelResp = self.model(nextImg)
    detections = modelResp[0]
    diffAreas = {}

    for data in detections.boxes.data.tolist():
      # extract the confidence (i.e., probability) associated with the detection
      print(data)
      confidence = float(data[4])

      # filter out weak detections by ensuring the
      # confidence is greater than the minimum confidence
      if confidence >= self.confidenceThreshold:
        id = int(data[5])
        name = '%3d_%s' % (id, detections.names[id])
        self.logger.info('detected: %s: %f' % (name, confidence))
        diffAreas[name] = (data[:4])
        # if the confidence is greater than the minimum confidence,
        # draw the bounding box on the frame
        #xmin, ymin, xmax, ymax = int(data[0]), int(data[1]), int(data[2]), int(data[3])
    # end for

    return {'diffAreas': diffAreas, 'name': self.name}
  # end def

  def findAOIs(self, prevAreas, nextAreas):
    aois = {}

    for name, nextArea in nextAreas.items():
      if name not in self.ignores:
        if name in prevAreas:
          prevArea = prevAreas[name]
          if abs(prevArea[0] - nextArea[0]) > self.areaDiffThreshold:
            aois[name] = nextArea
        else:
          aois[name] = nextArea
      # end if
    # end for
# end class

if __name__ == '__main__':
  image1 = cv2.imread('test/img1.jpg')
  image2 = cv2.imread('test/img2.jpg')
  changeDetect = ChangeDetectYolo(image1, image2, 0.3)
  print(len(changeDetect.diffAreas))
