from logger import Logger
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback


class ChangeDetect:
  def __init__(self, activeStateCallback, changeDetectors):
    self.activeStateCallback = activeStateCallback
    self.logger = Logger('ChangeDetect')
    self.changeDetectors = changeDetectors
  # end def

  def process(self, prevImg, nextImg):
    nextImg['detections'] = []

    with ThreadPoolExecutor() as executor:
      futures = [executor.submit(detector.process, prevImg['img'], nextImg['img']) for detector in self.changeDetectors]

      self.logger.info('starting detectors')
      for future in as_completed(futures):
        diffResp = future.result()
        diffAreas = diffResp['diffAreas']

        if len(diffAreas) > 0:
          nextImg['detections'].append({'diffAreas': diffAreas, 'name': diffResp['name']})

      self.logger.info('detectors completed')
  # end def
# end class
