import logging
import traceback
import utils
import queue
import threading
from ChangeDetect import ChangeDetect
from time import time


class Surveillance:
  def __init__(self, imageProducer, storageObserver, detectors, bufferSize=100, logger=None):
    self.imageProducer = imageProducer
    self.storageObserver = storageObserver
    self.imageBuffer = queue.Queue(bufferSize)
    self.storageBuffer = queue.Queue(bufferSize)
    self.prevImg = None

    if logger:
      self.logger = logger
    else:
      self.logger = logging.getLogger('Surveillance')

    self.changeDetector = ChangeDetect(self.imageProducer.setActiveState, detectors)

    self.state = 'init'
  # end def

  def execute(self, durationSec=0):
    imgProducer = threading.Thread(target=self.imageProducer.produce, args=(self.imageBuffer,))
    imgProducer.daemon = True
    imgProducer.start()

    storageObserver = threading.Thread(target=self.storageObserver.monitorQueue, args=(self.storageBuffer,))
    storageObserver.daemon = True
    storageObserver.start()

    start = time()
    while not self.done(start, durationSec):
      img = self.imageBuffer.get()
      self.imageBuffer.task_done()

      if img == None:
        self.logger.error('NONE IMAGE!!!!!')

      if self.prevImg:
        imgPair = [self.prevImg, img]
        changeProduct = self.diffImages(imgPair)
        if len(changeProduct['detections']) > 0:
          changeProduct['annotatedImage'] = utils.annotateImage(changeProduct)
          self.storeImage(changeProduct)
      # end if

      self.prevImg = img
      if 'detections' in self.prevImg:
        self.logger.info('detections: ' + str(len(self.prevImg['detections'])))
        for detection in self.prevImg['detections']:
          self.logger.info('name: ' + detection['name'])
    # end while
  # end def

  def done(self, start, duration):
    done = False
    if duration > 0:
      done = time() - start > duration

    return done
  # end def

  def diffImages(self, accumList):
    self.state = 'diff'
    startTime = time()

    try:
      prevEvent = accumList[0]
      nextEvent = accumList[1]

      nextEvent['processTimestamp'] = utils.getTimestampId()
      self.changeDetector.process(prevEvent, nextEvent)

      nextEvent['processDuration'] = time() - startTime

      return nextEvent
    except Exception as ex:
      tb = traceback.format_exc()
      self.logErrorMessage(tb)
      self.logErrorMessage('failure during change detection')
    # end try

    return {'changeImage': None, 'processDuration': time() - startTime}
  # end def

  def storeImage(self, imgProduct):
    if not self.storageBuffer.full():
      self.storageBuffer.put(imgProduct)
      self.logMessage('image added to store queue (%d)' % self.storageBuffer.qsize())
    else:
      self.logMessage('storage queue full (%d)' % self.storageBuffer.qsize())
  # end def

  def completed(self):
    self.state = 'completed'
    self.logMessage("completed")
  # end def

  def logMessage(self, message):
    threadName = threading.current_thread().name
    self.logger.info('%s - [%s]: %s' % (threadName, self.state, message))
  # end def

  def logErrorMessage(self, message):
    threadName = threading.current_thread().name
    self.logger.error('%s - [%s]: %s' % (threadName, self.state, message))
# end class
