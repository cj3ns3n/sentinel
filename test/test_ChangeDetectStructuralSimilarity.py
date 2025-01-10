import unittest
import logging

import cv2
from ChangeDetectStructuralSimilarity import ChangeDetectStructuralSimilarity

class TestStructuralSimilarity(unittest.TestCase):

  def test_diff(self):
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s - %(name)s', level=logging.INFO)
    logger = logging.getLogger('test_dif')

    image1 = cv2.imread('test/img1.jpg')
    image2 = cv2.imread('test/img2.jpg')
    changeDetect = ChangeDetectStructuralSimilarity(image1, image2, 400, 98, logger=logger)
    self.assertEqual(1, len(changeDetect.diffAreas))

if __name__ == '__main__':
  unittest.main()