import os.path
import threading
import cv2
from logger import Logger


class StorageObserver:
    def __init__(self, zone=None, remoteUploader=None, logger=None):
        self.zone = zone
        self.remoteUploader = remoteUploader
        if logger:
            self.logger = logger
        else:
          self.logger = Logger('StorageObserver')
    # end def

    def monitorQueue(self, imgQueue):
        while True:
          imgToStore = imgQueue.get()
          self.storeImage(imgToStore)
        # end while
    # end def

    def storeImage(self, imageContext):
        imgId = imageContext.acquireTimestamp

        self.logInfo('storing image %s' % (imgId))

        fileName = imgId.replace(":", "-") + '.jpg'
        if self.zone:
            fileName = os.path.join(self.zone, fileName)

        self.saveImageFs(fileName, imageContext.annotatedImage)

        if self.remoteUploader:
            try:
                self.logInfo("uploading image: %s" % (fileName))
                self.remoteUploader.upload(fileName)
                self.logInfo("uploaded image: %s" % (fileName))
            except Exception as err:
                self.logErr("error uploading image: " + repr(err))
        # end if
    # end def

    def saveImageFs(self, fileName, image):
        self.logInfo('saved image: %s' % (fileName))
        cv2.imwrite(fileName, image)
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