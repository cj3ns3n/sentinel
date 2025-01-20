import logging
import traceback
import utils
import queue
import threading
from ChangeDetect import ChangeDetect
from ChangeDetectStructuralSimilarity import ChangeDetectStructuralSimilarity
from ChangeDetectYolo import ChangeDetectYolo
from time import time


class Surveillance:
  def __init__(self, imageProducer, storageObserver, minContourArea=400, minDiffScore=100, bufferSize=100, logger=None):
    self.imageProducer = imageProducer
    self.storageObserver = storageObserver
    self.imageBuffer = queue.Queue(bufferSize)
    self.storageBuffer = queue.Queue(bufferSize)
    self.prevImg = None

    if logger:
      self.logger = logger
    else:
      self.logger = logging.getLogger('Surveillance')

    structuralSimilarityChangeDetect = ChangeDetectStructuralSimilarity(minContourArea=minContourArea, minDiffScore=minDiffScore)
    yoloChangeDetect = ChangeDetectYolo()

    self.changeDetector = ChangeDetect(self.imageProducer.setActiveState, [structuralSimilarityChangeDetect, yoloChangeDetect])

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
        changeProduct = self.diffImages(imgPair)
        if not isinstance(changeProduct['changeImage'], type(None)):
          self.storeImage(changeProduct)
      # end if

      self.prevImg = img
    # end while
  # end def

  def diffImages(self, accumList):
    self.state = 'diff'
    startTime = time()

    try:
      prevEvent = accumList[0]
      nextEvent = accumList[1]

      prevEvent['processTimestamp'] = utils.getTimestampId()
      changeImage = self.changeDetector.process(prevEvent['img'], nextEvent['img'])

      prevEvent['processDuration'] = time() - startTime
      prevEvent['changeImage'] = changeImage

      return prevEvent
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
