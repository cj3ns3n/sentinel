class ImageContext:
  def __init__(self, originalImage):
    self.originalImage = originalImage
    self.acquireTimestamp = None
    self.annotatedImage = None
    self.detections = []
    self.diffScore = None
    self.processTimestamp = None
    self.processDuration = None
    self.bufferSize = None
