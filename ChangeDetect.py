import logging
import threading
import time


class ChangeDetect:
  def __init__(self, changeDetectors, activeStateCallback, logger=None):
    self.changeDetectors = changeDetectors
    self.activeStateCallback = activeStateCallback

    if logger:
      self.logger = logger
    else:
      self.logger = logging.getLogger('ChangeDetect')

  def process(self):
    boxedImg = None
    changePairs = []

    for detector in self.changeDetectors:
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
        self.logger.info('detector alive: %s' % repr(thread.is_alive()))
        if thread.is_alive():
          alive = True
        else:
          detector = threadPair[1]
          self.logger.info('detected difference %s' % repr(detector.isDifferent))
          if detector.isDifferent:
            boxedImg = detector.boxedDiffImg
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
# end class
