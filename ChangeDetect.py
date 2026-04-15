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
    for detector in self.changeDetectors:
      diffResp = detector.process(prevEvent, nextEvent)
      diffAreas = diffResp['diffAreas']

      if len(diffAreas) > 0:
        nextEvent.detectors.append({'diffAreas': diffAreas, 'name': diffResp['name']})
        self.activeStateCallback()
    # end for
  # end def

  def process_threaded(self, prevEvent, nextEvent):
    with ThreadPoolExecutor() as executor:
      futures = [executor.submit(detector.process, prevEvent, nextEvent) for detector in self.changeDetectors]

      self.logger.info('starting detectors')
      for future in as_completed(futures):
        diffResp = future.result()
        diffAreas = diffResp['diffAreas']

        if len(diffAreas) > 0:
          nextEvent.detectors.append({'diffAreas': diffAreas, 'name': diffResp['name']})
          self.activeStateCallback()

      self.logger.info('detectors completed')
    # end with
  # end def
# end class
