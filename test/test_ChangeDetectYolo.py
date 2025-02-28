import unittest
import logging
import os

import cv2
from ChangeDetectYolo import ChangeDetectYolo

class TestStructuralSimilarity(unittest.TestCase):

  def test_diff(self):
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s - %(name)s', level=logging.INFO)
    logger = logging.getLogger('test_dif')

    image1 = cv2.imread(str(os.path.join('test', 'front-n55.jpg')))
    image2 = cv2.imread(str(os.path.join('test', 'front-n56.jpg')))
    changeDetect = ChangeDetectYolo()
    changeResp = changeDetect.process({'img':image1}, {'img':image2})
    print(changeResp['diffAreas'])
    self.assertEqual(1, len(changeResp['diffAreas']))

if __name__ == '__main__':
  unittest.main()
