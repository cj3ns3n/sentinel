from skimage.metrics import structural_similarity
import cv2
import logging

class ImageDifferentiator:
  def __init__(self, prevImg, nextImg, minContourArea=400, minDiffScore=100, logger=None):
    self.prevImg = prevImg
    self.nextImg = nextImg
    self.boxedDiffImg = None
    self.minContourArea = minContourArea
    self.minDiffScore = minDiffScore
    self.score = minDiffScore
    if logger:
      self.logger = logger
    else:
      self.logger = logging.getLogger('ImageDifferentiator')

    if type(prevImg) != None and type(nextImg) != None:
      self.process()
  # end def

  def process(self):
    self.logger.info('change detection')
    diffContours = self.findDiffContours(self.prevImg, self.nextImg)

    if len(diffContours) > 0:
      self.logger.info('%d contours found' % (len(diffContours)))
      self.boxedDiffImg = self.boxImage(self.nextImg, diffContours)
  # end def

  def findDiffContours(self, before, after):
    contours = []

    # Convert images to grayscale
    #cv2.imwrite('before.jpg', before)
    #cv2.imwrite('after.jpg', after)

    before_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    before_gray = cv2.GaussianBlur(before_gray, (21, 21), 0)
    after_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)
    after_gray = cv2.GaussianBlur(after_gray, (21, 21), 0)

    #cv2.imwrite('before_gray.jpg', before_gray)
    #cv2.imwrite('after_gray.jpg', after_gray)

    # Compute SSIM between the two images
#    (score, diff) = structural_similarity(before_gray, after_gray, data_range=300, full=True)
    (score, diff) = structural_similarity(before_gray, after_gray, data_range=75,  full=True)
    self.score = score * 100
    self.logger.info('similarity: %0.2f; min similarity: %d' % (self.score, self.minDiffScore))

    if self.score < self.minDiffScore:
      # The diff image contains the actual image differences between the two images
      # and is represented as a floating point data type in the range [0,1]
      # so we must convert the array to 8-bit unsigned integers in the range
      # [0,255] before we can use it with OpenCV
      diff = (diff * 255).astype("uint8")

      # Threshold the difference image, followed by finding contours to
      # obtain the regions of the two input images that differ
      thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
      contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      contours = contours[0] if len(contours) == 2 else contours[1]
    # end if

    return contours
  # end def

  def boxImage(self, image, contours):
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
        cv2.rectangle(boxedImg, (x, y), (x + w, y + h), (36,255,12), 2)
    # end for
    self.logger.info('area (min,max) (%d,%d)' % (minArea, maxArea))

    return boxedImg
  # end def
# end class
