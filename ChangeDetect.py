from logger import Logger
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback
import cv2
import utils
from ChangeDetectStructuralSimilarity import ChangeDetectStructuralSimilarity
from ChangeDetectYolo import ChangeDetectYolo


class ChangeDetect:
  CONTOUR_COLORS = [(36,255,12), (51,153,255), (255,153,255), (255,178,102)]

  def __init__(self, activeStateCallback, minContourArea=400, minDiffScore=100, logger=None):
    self.activeStateCallback = activeStateCallback

    if logger:
      self.logger = logger
    else:
      self.logger = Logger('', 'ChangeDetect')

    structuralSimilarityChangeDetect = ChangeDetectStructuralSimilarity(minContourArea=minContourArea, minDiffScore=minDiffScore)
    yoloChangeDetect = ChangeDetectYolo()
    self.changeDetectors = [structuralSimilarityChangeDetect, yoloChangeDetect]
  # end def

  def process(self, prevImg, nextImg):
    boxedImg = None

    with ThreadPoolExecutor() as executor:
      futures = [executor.submit(detector.process, prevImg, nextImg) for detector in self.changeDetectors]

      self.logger.info('starting detectors')
      for future in as_completed(futures):
        try:
          detector = future.result()
          diffAreas = detector.diffAreas
          if len(diffAreas) > 0:
            if type(boxedImg) == type(None):
              boxedImg = nextImg.copy()
            boxedImg = self.boxImage(boxedImg, diffAreas, detector.color)
            self.activeStateCallback()
        except Exception as e:
          self.logger.error(traceback.format_exc())
          self.logger.error(repr(e))
    self.logger.info('detectors completed')

    return boxedImg
  # end def

  def boxImage(self, image, areas, color):
    for id, area in areas.items():
      cv2.rectangle(image, (int(area[0]), int(area[1])), (int(area[2]), int(area[3])), color, 2)
      utils.addText(image, id, (int(area[0]), int(area[1])), color=color)

    return image
  # end def
# end class
