from logger import Logger
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback


class ChangeDetect:
  def __init__(self, activeStateCallback, changeDetectors):
    self.activeStateCallback = activeStateCallback
    self.logger = Logger('ChangeDetect')
    self.changeDetectors = changeDetectors
  # end def

  def process(self, prevEvent, nextEvent):
    nextEvent['detections'] = []

    with ThreadPoolExecutor() as executor:
      futures = [executor.submit(detector.process, prevEvent, nextEvent) for detector in self.changeDetectors]

      self.logger.info('starting detectors')
      for future in as_completed(futures):
        diffResp = future.result()
        diffAreas = diffResp['diffAreas']

        if len(diffAreas) > 0:
          nextEvent['detections'].append({'diffAreas': diffAreas, 'name': diffResp['name']})

      self.logger.info('detectors completed')
  # end def
# end class
