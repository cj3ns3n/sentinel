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

        self.logger.info('storing image %s' % (imgId))

        fileName = imgId.replace(":", "-") + '.jpg'
        if self.zone:
            fileName = os.path.join(self.zone, fileName)

        self.saveImageFs(fileName, imageContext.annotatedImage)

        if self.remoteUploader:
            try:
                self.logger.info("uploading image: %s" % (fileName))
                self.remoteUploader.upload(fileName)
                self.logger.info("uploaded image: %s" % (fileName))
            except Exception as err:
                self.logger.error("error uploading image: " + repr(err))
        # end if
    # end def

    def saveImageFs(self, fileName, image):
        self.logger.info('saved image: %s' % (fileName))
        cv2.imwrite(fileName, image)
    # end def
# end class