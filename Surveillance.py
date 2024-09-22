import logging
import traceback
import utils
import queue
import threading
import time
from ImageDifferentiator import ImageDifferentiator
from time import time

class Surveillance:
  def __init__(self, imageProducer, storageObserver, minContourArea=400, minDiffScore=100, bufferSize=100, logger=None):
    self.imageProducer = imageProducer
    self.storageObserver = storageObserver
    self.minContourArea = minContourArea
    self.minDiffScore = minDiffScore
    self.imageBuffer = queue.Queue(bufferSize)
    self.storageBuffer = queue.Queue(bufferSize)
    self.prevImg = None

    if logger:
      self.logger = logger
    else:
      self.logger = logging.getLogger('Surveillance')

    self.state = 'init'
  # end def

  def execute(self):
    imgProducer = threading.Thread(target=self.imageProducer.produce, args=(self.imageBuffer,))
    imgProducer.daemon = True
    imgProducer.start()

    storageObserver = threading.Thread(target=self.storageObserver.monitorQueue, args=(self.storageBuffer,))
    storageObserver.daemon = True
    storageObserver.start()

    while True:
      img = self.imageBuffer.get()
      self.imageBuffer.task_done()

      if img == None:
        self.logger.error('NONE IMAGE!!!!!')

      if self.prevImg:
        imgPair = [self.prevImg, img]
        diffProduct = self.diffImages(imgPair)
        if self.filterImages(diffProduct):
          self.imageProducer.setActiveState()
          self.storeImage(diffProduct)
      # end if

      self.prevImg = img
    # end while
  # end def

  def diffImages(self, accumList):
    self.state = 'diff'

    try:
      prevEvent = accumList[0]
      nextEvent = accumList[1]

      prevEvent['processTimestamp'] = utils.getTimestampId()
      startTime = time()
      diff = ImageDifferentiator(prevEvent['img'], nextEvent['img'], minContourArea=self.minContourArea, minDiffScore=self.minDiffScore)

      prevEvent['processDuration'] = time() - startTime
      prevEvent['diffScore'] = diff.score
      prevEvent['diffImg'] = diff.boxedDiffImg

      return prevEvent
    except Exception as ex:
      tb = traceback.format_exc()
      self.logErrorMessage(tb)
      self.logErrorMessage('failure during change detection')
    # end try

    return {'diffImg': None, 'diffScore': self.minDiffScore}
  # end def

  def filterImages(self, diffedProduct):
    self.state = 'filter'

    try:
      diff = diffedProduct['diffScore'] < self.minDiffScore
      self.logMessage('filter: %s' % diff)
      return diff
    except Exception as ex:
      tb = traceback.format_exc()
      self.logErrorMessage(tb)
      self.logErrorMessage('failure during filter')
    # end try

    return False
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
