import utils
import cv2
import logging
import os.path
import threading

class StorageObserver:
    def __init__(self, zone=None, remoteUploader=None, logger=None):
        self.zone = zone
        self.remoteUploader = remoteUploader
        if logger:
            self.logger = logger
        else:
          self.logger = logging.getLogger('StorageObserver')
    # end def

    def monitorQueue(self, imgQueue):
        while True:
          imgToStore = imgQueue.get()
          self.storeImage(imgToStore)
        # end while
    # end def

    def storeImage(self, diffObj):
        imgId = diffObj['acquireTimestamp']

        self.logInfo('storing image %s' % (imgId))
        preppedImage = self.prepImage(diffObj)

        fileName = imgId.replace(":", "-") + '.jpg'
        sourceFileName = 'src-' + fileName
        if self.zone:
            fileName = os.path.join(self.zone, fileName)
            sourceFileName = os.path.join(self.zone, sourceFileName)

        self.saveImageFs(fileName, preppedImage)

        if self.remoteUploader:
            try:
                self.logInfo("uploading image: %s" % (fileName))
                self.remoteUploader.upload(fileName)
                self.logInfo("uploaded image: %s" % (fileName))
            except Exception as err:
                self.logErr("error uploading image: " + repr(err))
        # edn if
    # end def

    def prepImage(self, diffObj):
        imgId = diffObj['acquireTimestamp']
        image = diffObj['diffImg']

        saveFrame = image.copy()
        self.logInfo('dimensions' + repr(saveFrame.shape)) #[:2]))

        if saveFrame.shape[0] > 1000:
            score = diffObj['diffScore']
            processTimestamp = diffObj['processTimestamp']
            processDuration = diffObj['processDuration']

            utils.addText(saveFrame, 'acquired:  ' + imgId, (10, 40))
            utils.addText(saveFrame, 'processed: ' + processTimestamp, (10, 70))
            utils.addText(saveFrame, 'saved:     ' + utils.getTimestampId(), (10, 100))
            utils.addText(saveFrame, 'duration: %0.2f' % (processDuration), (10, 130))
            utils.addText(saveFrame, 'score: %0.2f' % (score), (10, 160))
            utils.addText(saveFrame, 'buffer-size: %d' % (diffObj['buffer-size']), (10, 190))
        else:
            processTimestamp = diffObj['processTimestamp']

            utils.addText(saveFrame, imgId, (10, 40))
            utils.addText(saveFrame, processTimestamp, (10, 70))
            utils.addText(saveFrame, utils.getTimestampId(), (10, 100))
            utils.addText(saveFrame, 'buffer-size: %d' % (diffObj['buffer-size']), (10, 130))
        # end if

        return saveFrame
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