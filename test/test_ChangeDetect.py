import unittest
import logging

import cv2
from ChangeDetect import ChangeDetect

activeCalled = [False]

def setActiveCallback():
  activeCalled[0] = True

def changeDetect(image1, image2, tester):
  changeDetect = ChangeDetect(setActiveCallback)
  boxedImg = changeDetect.process(image1, image2)
  tester.assertTrue(activeCalled[0])
  tester.assertIsNotNone(boxedImg)
  activeCalled[0] = False
  return boxedImg

class TestChangeDetect(unittest.TestCase):

  def test_diff(self):
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s - %(name)s', level=logging.INFO)
    logger = logging.getLogger('test_dif')

    image1 = cv2.imread('test/img1.jpg')
    image2 = cv2.imread('test/img2.jpg')
    boxedImg = changeDetect(image1, image2, self)
    cv2.imwrite('test_ChangeDetect_img1-img2.jpg', boxedImg)

    image1 = cv2.imread('test/front1.jpg')
    image2 = cv2.imread('test/front2.jpg')
    boxedImg = changeDetect(image1, image2, self)
    cv2.imwrite('test_ChangeDetect_front1-front2.jpg', boxedImg)

    image1 = cv2.imread('test/front3.jpg')
    image2 = cv2.imread('test/front4.jpg')
    boxedImg = changeDetect(image1, image2, self)
    cv2.imwrite('test_ChangeDetect_front3-front4.jpg', boxedImg)

    image1 = cv2.imread('test/front5.jpg')
    image2 = cv2.imread('test/front6.jpg')
    boxedImg = changeDetect(image1, image2, self)
    cv2.imwrite('test_ChangeDetect_front5-front6.jpg', boxedImg)

    image1 = cv2.imread('test/front6.jpg')
    image2 = cv2.imread('test/front6.jpg')
    boxedImg = changeDetect(image1, image2, self)
    cv2.imwrite('test_ChangeDetect_front6-front6.jpg', boxedImg)

if __name__ == '__main__':
  unittest.main()
