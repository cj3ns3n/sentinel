import logging
import threading
import time
import cv2
import utils
from ChangeDetectStructuralSimilarity import ChangeDetectStructuralSimilarity
from ChangeDetectYolo import ChangeDetectYolo


class ChangeDetect:
  CONTOUR_COLORS = [(36,255,12), (51,153,255), (255,153,255), (255,178,102)]

  def __init__(self, activeStateCallback, minContourArea=400, minDiffScore=100, logger=None):
    self.activeStateCallback = activeStateCallback
    self.minContourArea = minContourArea
    self.minDiffScore = minDiffScore

    if logger:
      self.logger = logger
    else:
      self.logger = logging.getLogger('ChangeDetect')

  def process(self, prevImg, nextImg):
    boxedImg = None
    changePairs = []

    structuralSimilarityChangeDetect = ChangeDetectStructuralSimilarity(prevImg, nextImg, minContourArea=self.minContourArea, minDiffScore=self.minDiffScore)
    #structuralSimilarityChangeDetect = ChangeDetectYolo(prevImg, nextImg)
    changeDetectors = [structuralSimilarityChangeDetect]

    for detector in changeDetectors:
      thread = threading.Thread(target=detector.process)
      thread.daemon = True
      thread.start()
      changePairs.append((thread, detector))
    # end for

    done = False
    while not done:
      alive = False
      for threadPair in changePairs:
        thread = threadPair[0]
        if thread.is_alive():
          alive = True
        else:
          detector = threadPair[1]
          self.logger.info('detected contours %d' % len(detector.diffAreas))
          if len(detector.diffAreas) > 0:
            boxedImg = self.boxImage(nextImg, detector.diffAreas, self.CONTOUR_COLORS[0])
            self.activeStateCallback()
            done = True
            break
        # end if
        time.sleep(0.01)

        done = done or not alive
      # end for
    # end while

    for threadPair in changePairs:
      threadPair[0].join()

    return boxedImg
  # end def

  def boxImage(self, image, areas, color):
    boxedImg = image.copy()

    for id, area in areas.items():
      cv2.rectangle(boxedImg, (int(area[0]), int(area[1])), (int(area[2]), int(area[3])), color, 2)
      utils.addText(boxedImg, id, (int(area[0]), int(area[1])), color=color)

    return boxedImg
  # end def
# end class
