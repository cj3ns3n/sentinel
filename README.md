# sentinel
Sentinel is a python app to monitor video streams, detect differences in scenes, saves the differences to a file and optionally upload the difference highlighted images to a cloud storage provider.

This is slightly different than other monitoring systems in that it will record still images instead of a video.  I found it more useful to have a collection of still images with differences highlieghted than to have a video recorded when difference are detected.  Images are much easier for me to cycle through than watching a video feed.

## Execution
The easiest way to monitor a feed is to have Sentinel initiate from aconfig file.

`python sentinel.py --config-file CONFIG_FILE`

Seninel expects a json file with the following fields:
```
'frequency': 20,  # number of seconds to wait between image difference detection (when there is not differences)
'minDiffScore': 80, # The minimum score before two images are considered different
'minContourArea': 400,  # The minimum size to use for a contour area
'localStorageOnly': true,  # Only store to local storage
'url': ''  # The url of the video feed to use 
'zone': '' # an optional config value to indicate which Google cloud storage bucket to upload images too 
```
For commandline help

`python sentinel.py --help`

## How it works
Sentinal has an "ImageProducer" that operates on its own thread that captures images at a configurable frequency.  When changes in the scene are detected, Sentinel will capture images as fast as it can until no changes are detected.

The images from the producer are placed in a queue to be processed for difference by the "ImageDifferentiator" and stored by the "StorageObserver".

### Limitations
- Reads one picture at a time (not really a video stream, but more of a time lapse)
- Contour difference is highly impacted by noise in the image and will have many false positives.
- Only support google cloud bucket storage