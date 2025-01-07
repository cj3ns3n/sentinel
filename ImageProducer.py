import urllib.request
import base64
import time
import cv2
import np
import utils
import logging
import threading
import psutil

class ImageProducer:
  def __init__(self, imageUrl, credentials=None, frequency=2.5, count=None, logger=None):
    self.imageUrl = imageUrl
    self.credentials = credentials
    self.frequency = frequency
    self.maxCount = count
    self.setActiveState()

    if logger:
      self.logger = logger
    else:
      self.logger = logging.getLogger('ImageProducer')

    if imageUrl:
      self.getImage = self.captureWeb

      self.req = urllib.request.Request(self.imageUrl)
      if self.credentials:
        encodedCredentials = ('%s:%s' % (self.credentials['login'], self.credentials['password']))
        encodedCredentials = base64.b64encode(encodedCredentials.encode('ascii'))
        self.req.add_header('Authorization', 'Basic %s' % encodedCredentials.decode("ascii"))
      #end if
    else:
      self.getImage = self.captureLocal
    # end if

    # testing
    #self.getImage = self.captureBlack
  # end def

  def captureBlack(self):
    return np.zeros((256, 256, 3), np.uint8)
  # end def

  def captureLocal(self):
    capture = cv2.VideoCapture(0)
    (ret, frame) = capture.read()

    if ret:
      #self.logInfo('dimensions' + repr(frame.shape[:2]))
      return frame
    else:
      return None
  #end def

  def captureWeb(self):
    image = None

    try:
      self.logger.info("retrieving url: %s" % (self.imageUrl))
      resp = urllib.request.urlopen(self.req, timeout=30)
      image = cv2.imdecode(np.fromstring(resp.read(), dtype=np.uint8), cv2.IMREAD_COLOR)
      #utils.addText(image, 'acquired: ' + utils.getTimestampId(), (10, 20))

      if image is not None:
        self.logInfo('dimensions' + repr(image.shape[:2]))
      else:
        self.logErr('failed to decode image')
    except Exception as ex:
      self.logger.error(ex)

    return image
  # end def

  def produce(self, queue):
    startTime = time.time()

    while True:
      if self.shouldGetImage():
        try:
          self.logInfo("acquiring image")
          img = self.getImage()
          self.logInfo('acquired image (duration: %f) %s' % (time.time() - startTime, utils.getTimestampId()))
          self.onNextImage({'img': img, 'acquireTimestamp': utils.getTimestampId()}, queue)
        except urllib.error.URLError as err:
          self.logErr("url error getting web cam image: " + repr(err))
          self.logInfo("url: %s" % (self.imageUrl))
          #observer.on_error(err)
        except cv2.error as error:
          self.logErr("cv error getting web cam image: " + repr(error))
          self.logInfo("url: %s" % (self.imageUrl))
          #observer.on_error(error)
        #end try
      # end if

      #self.logInfo("------------ITS ABOUT TIME-----------")
      if time.time() > self.nextSleepTime:
        sleepTime = self.sleepUntilTime - time.time()
        self.sleepUntilTime += self.frequency

        if sleepTime > 0:
          self.logInfo('sleeping %f sec' % (sleepTime))
          time.sleep(sleepTime)
      else:
        self.logInfo('no sleeping')
      # end if
    #end while
  # end def

  def shouldGetImage(self):
    vm = psutil.virtual_memory()
    return vm.percent < 92
  # end def

  def setActiveState(self):
    self.nextSleepTime = time.time() +  self.frequency
    self.sleepUntilTime = self.nextSleepTime + self.frequency
  # end def

  def onNextImage(self, imgData, imageBuffer):
    if not imageBuffer.full():
      imgData['buffer-size'] = imageBuffer.qsize()
      imageBuffer.put(imgData)
      self.logInfo('image added to queue (buffer size: %d)' % imageBuffer.qsize())
    else:
      self.logInfo('queue full; image not added (buffer size: %d)' % imageBuffer.qsize())
  # end def

  def logInfo(self, message):
    threadName = threading.current_thread().name
    self.logger.info(threadName + ' - ' + message)
  # end def

  def logErr(self, message):
    threadName = threading.current_thread().name
    self.logger.error(threadName + ' - ' + message)
  # end def
# end class

if __name__ == '__main__':
  import sys
  import queue
  from logger import Logger

  logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s - %(name)s', level=logging.INFO)
  logger = Logger('test', 'main')

  imageBuffer = queue.Queue(5)

  producer = ImageProducer(sys.argv[1], logger=logger)
  imgProducerThread = threading.Thread(target=producer.produce, args=(imageBuffer,))
  imgProducerThread.daemon = True
  imgProducerThread.start()

  #cv2.imwrite(sys.argv[2], producer.getImage())
  count = 0
  while True:
    logger.info('00; %s: count: %03d; qsize: %d' % (utils.getTimestampId(), count, imageBuffer.qsize()))
    img = imageBuffer.get()
    imageBuffer.task_done()
    #logger.error('%s: current' % (img['acquireTimestamp']))
    logger.info('acquired time: %s; qsize: %d' % (img['acquireTimestamp'], img['buffer-size']))
    logger.info('01: %s: count: %03d; qsize: %d' % (utils.getTimestampId(), count, imageBuffer.qsize()))
    count += 1
    time.sleep(6)
    producer.setActiveState()

