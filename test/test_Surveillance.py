import unittest
from logger import Logger
import time
import os.path
import cv2
import utils
from Surveillance import Surveillance
from StorageObserver import StorageObserver
from ChangeDetectYolo import ChangeDetectYolo


class ImageProducer:
  def __init__(self, images, frequency=0.01, logger=None):
    self.images = images
    self.frequency = frequency
    self.logger = logger
  # end def

  def produce(self, queue):
    for imgPath in self.images:
      img = cv2.imread(imgPath, cv2.IMREAD_COLOR)
      imgData = {'buffer-size': queue.qsize(), 'img': img, 'acquireTimestamp': utils.getTimestampId()}
      self.logger.info('produce: %s' % imgPath)
      queue.put(imgData)
      time.sleep(self.frequency)
    # end for
  # end def

  def setActiveState(self):
    pass
  # end def
# end class


class TestSurveillance(unittest.TestCase):
  def test_diff(self):
    imgs = [os.path.join('test', 'night_00.jpg'),
            os.path.join('test', 'night_01.jpg'),
            os.path.join('test', 'night_02.jpg'),
            os.path.join('test', 'night_03.jpg'),
            os.path.join('test', 'night_04.jpg'),
            os.path.join('test', 'night_05.jpg'),
            os.path.join('test', 'night_06.jpg'),
            os.path.join('test', 'night_07.jpg'),
            os.path.join('test', 'night_08.jpg'),
            os.path.join('test', 'night_09.jpg')]

    logger = Logger('test_Surveillance')

    imgProducer = ImageProducer(imgs, logger=logger)
    storageObserver = StorageObserver('test_results', logger=logger)
    yoloDetector = ChangeDetectYolo(modelName='yolo11x.pt')

    surveillance = Surveillance(imgProducer, storageObserver, [yoloDetector], logger=logger)
    surveillance.execute(0)
  # end def
# end class
if __name__ == '__main__':
  unittest.main()
