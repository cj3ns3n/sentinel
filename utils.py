from datetime import datetime
import cv2

CONTOUR_COLORS = [(36,255,12), (51,153,255), (255,153,255), (255,178,102)]

def addText(img, txt, position, color=(0, 0, 255)):
  cv2.putText(img, txt, position, cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)


def getTimestampId():
  return datetime.now().strftime('%Y-%m-%d:%H:%M:%S.%f')[:-3]


def annotateImage(imgContext):
  image = imgContext['img'].copy()
  for detection in imgContext['detections']:
    detectorName = detection['name']
    areas = detection['diffAreas']
    color = CONTOUR_COLORS[sum(str.encode(detectorName)) % len(CONTOUR_COLORS)]
    for id, area in areas.items():
      cv2.rectangle(image, (int(area[0]), int(area[1])), (int(area[2]), int(area[3])), color, 2)
      addText(image, id, (int(area[0]), int(area[1])), color=color)

  imgId = imgContext['acquireTimestamp']
  if image.shape[0] > 1000:
    if 'diffScore' in imgContext:
      score = '%0.2f' % imgContext['diffScore']
    else:
      score = '--'
    processTimestamp = imgContext['processTimestamp']
    processDuration = imgContext['processDuration']

    addText(image, 'acquired:  ' + imgId, (10, 40))
    addText(image, 'processed: ' + processTimestamp, (10, 70))
    addText(image, 'saved:     ' + getTimestampId(), (10, 100))
    addText(image, 'duration: %0.2f' % (processDuration), (10, 130))
    addText(image, 'score: %s' % (score), (10, 160))
    addText(image, 'buffer-size: %d' % (imgContext['buffer-size']), (10, 190))
  else:
    processTimestamp = imgContext['processTimestamp']

    addText(image, imgId, (10, 40))
    addText(image, processTimestamp, (10, 70))
    addText(image, getTimestampId(), (10, 100))
    addText(image, 'buffer-size: %d' % (imgContext['buffer-size']), (10, 130))
  # end if

  return image
# end def
