import logging
import threading
import time
import cv2
from ChangeDetectStructuralSimilarity import ChangeDetectStructuralSimilarity


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

    structuralSimilarityChangeDetect = ChangeDetectStructuralSimilarity(prevImg, nextImg, minContourArea=self.minContourArea, minDiffScore=self.minDiffScore, logger=self.logger)
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
          self.logger.info('detected contours %d' % len(detector.diffContours))
          if len(detector.diffContours) > 0:
            boxedImg = self.boxImage(nextImg, detector.diffContours, self.CONTOUR_COLORS[1])
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

  def boxImage(self, image, contours, color):
    boxedImg = image.copy()

    minArea = self.minContourArea
    maxArea = 0
    for c in contours:
      area = cv2.contourArea(c)
      if area >= self.minContourArea:
        if area > maxArea:
          maxArea = area
        if area < minArea:
          minArea = area

        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(boxedImg, (x, y), (x + w, y + h), color, 2)
    # end for
    self.logger.info('area (min,max) (%d,%d)' % (minArea, maxArea))

    return boxedImg
  # end def
# end class
