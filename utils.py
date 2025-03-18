from datetime import datetime
import cv2

CONTOUR_COLORS = [(36,255,12), (51,153,255), (255,153,255), (255,178,102)]

def addText(img, txt, position, color=(0, 0, 255)):
  cv2.putText(img, txt, position, cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)


def getTimestampId():
  return datetime.now().strftime('%Y-%m-%d:%H:%M:%S.%f')[:-3]

def getCrossHairLines(center):
  return (((int(center[0] - 6), int(center[1])), (int(center[0] + 6), int(center[1]))),
           ((int(center[0]), int(center[1] - 6)), (int(center[0]), int(center[1] + 6))))

def annotateImage(imgContext):
  image = imgContext.originalImage.copy()
  detectorCount = 0
  for detector in imgContext.detectors:
    detectorName = detector['name']
    aois = detector['diffAreas']
    color = CONTOUR_COLORS[sum(str.encode(detectorName)) % len(CONTOUR_COLORS)]
    addText(image, detectorName, (550, (40 + (30 * detectorCount))), color=color)
    detectorCount += 1

    for aoiId, aoi in aois.items():
      area = aoi.area
      cv2.rectangle(image, (int(area[0]), int(area[1])), (int(area[2]), int(area[3])), color, 2)
      addText(image, aoiId, (int(area[0]+2), int(area[1]+20)), color=color)

      txtCount = 1
      for txt in aoi.annotate_text:
        pos = (int(area[0]+2), int(area[1]+(22 * (txtCount + 1))))
        addText(image, txt, pos, color=color)

      for crossHairCenter in aoi.annotate_cross_hairs:
        crossHairLines = getCrossHairLines(crossHairCenter)
        cv2.line(image, crossHairLines[0][0], crossHairLines[0][1], color, thickness=2)
        cv2.line(image, crossHairLines[1][0], crossHairLines[1][1], color, thickness=2)
      # end for

      for circleCenter in aoi.annotate_circles:
        cv2.circle(image, (int(circleCenter[0]), int(circleCenter[1])), 4, color, -1)
    # end for
  # end for

  imgId = imgContext.acquireTimestamp
  if image.shape[0] > 1000:
    if imgContext.diffScore:
      score = '%0.2f' % imgContext.diffScore
    else:
      score = '--'
    processTimestamp = imgContext.processTimestamp
    processDuration = imgContext.processDuration

    addText(image, 'acquired:  ' + imgId, (10, 40))
    addText(image, 'processed: ' + processTimestamp, (10, 70))
    addText(image, 'saved:     ' + getTimestampId(), (10, 100))
    addText(image, 'duration: %0.2f' % (processDuration), (10, 130))
    addText(image, 'score: %s' % (score), (10, 160))
    addText(image, 'buffer-size: %d' % (imgContext.bufferSize), (10, 190))
  else:
    processTimestamp = imgContext.processTimestamp

    addText(image, imgId, (10, 40))
    addText(image, processTimestamp, (10, 70))
    addText(image, getTimestampId(), (10, 100))
    addText(image, 'buffer-size: %d' % (imgContext.bufferSize), (10, 130))
  # end if

  return image
# end def
