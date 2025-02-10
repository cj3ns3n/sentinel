from ImageProducer import ImageProducer
from StorageObserver import StorageObserver
from Surveillance import Surveillance
from logger import Logger
from importlib import import_module
from terminal_display import TerminalDisplay
import time
import threading
import json
import argparse

def getConfiguration(args):
  config = {'frequency': 20,
            'minDiffScore': 80,
            'minContourArea': 400,
            'localStorageOnly': False,
            'url': None}

  if args.local_storage_only:
    config['localStorageOnly'] = True

  if args.config_file:
    with open(args.config_file, 'r') as configFile:
      config = config | json.load(configFile)
      print(config)
  else:
    config['url'] = args.url
    if args.zone:
      config['zone'] = args.zone
    if args.frequency:
      config['frequency'] = args.frequency
  # end if

  return config
# end def

def loadDetectors(detectorConfigs, display):
  detectors = []
  for detector in config['detectors']:
    detectorLogger = Logger(detector['name'], display=display)
    detectorModule = import_module(detector['name'])
    initStr = 'detectorModule.%s(' % detector['name']
    for key, value in detector.items():
      if key != 'name':
        initStr += key + '=' + str(value) + ','
    # end for
    initStr += 'logger=detectorLogger)'

    print(initStr)
    detectors.append(eval(initStr))

  return detectors
# end def

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Collect and store IMINT')
  parser.add_argument('-z', '--zone', help='The zone name for cloud storage')
  parser.add_argument('--url', help='The WebCam URL; if not specified, the attached web cam will be used')
  parser.add_argument('--cleanup', action='store_true', help='remove uploaded image file')
  parser.add_argument('--local-storage-only', action='store_true', help='only store files to local file system')
  parser.add_argument('--logfile', help='The file to store logs.  Defaults to stdout')
  parser.add_argument('--display', default='curses', help='log display mode, curses or stdout')
  parser.add_argument('-f', '--frequency', type=int, default=120, help='The number of seconds between capturing images')
  parser.add_argument('--config-file', help="file containing configuration values")

  args = parser.parse_args()
  config = getConfiguration(args)

  display = None
  if args.display == 'curses':
    display = TerminalDisplay()
    display.run()

  logger = Logger('main', display, config['zone'])
  logger.info(repr(config))

  detectors = loadDetectors(config['detectors'], display)

  credentials = None
  if 'login' in config.keys():
    credentials = config

  imgProducer = ImageProducer(config['url'], credentials=credentials, frequency=config['frequency'], logger=Logger('ImageProducer', display, config['zone']))
  uploader = None
  if not config['localStorageOnly']:
    from storageGCS import SurveilUploader
    uploader = SurveilUploader('surveil', config['zone'], Logger('SurveilUploader', display), config['zone'])
  storageObserver = StorageObserver(zone=config['zone'], remoteUploader=uploader, logger=Logger('StorageObserver', display, config['zone']))

  surveillance = Surveillance(imgProducer, storageObserver, detectors, logger=Logger('Surveillance', display, config['zone']))
  surveillanceThread = threading.Thread(target=surveillance.execute)
  surveillanceThread.daemon = True
  surveillanceThread.start()

  if args.display == 'curses':
    while surveillanceThread.is_alive():
      display.run()
      time.sleep(0.01)

  surveillanceThread.join()
# end if
