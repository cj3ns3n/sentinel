from ImageProducer import ImageProducer
from StorageObserver import StorageObserver
from Surveillance import Surveillance
from logger import Logger
import json
import logging
import argparse

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s - %(name)s', level=logging.INFO)

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
  else:
    config['url'] = args.url
    if args.zone:
      config['zone'] = args.zone
    if args.frequency:
      config['frequency'] = args.frequency
  # end if

  return config
# end def


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Collect and store IMINT')
  parser.add_argument('-z', '--zone', help='The zone name for cloud storage')
  parser.add_argument('--url', help='The WebCam URL; if not specified, the attached web cam will be used')
  parser.add_argument('--cleanup', action='store_true', help='remove uploaded image file')
  parser.add_argument('--local-storage-only', action='store_true', help='only store files to local file system')
  parser.add_argument('--logfile', help='The file to store logs.  Defaults to stdout')
  parser.add_argument('-f', '--frequency', type=int, default=120, help='The number of seconds between capturing images')
  parser.add_argument('--config-file', help="file containing configuration values")

  config = getConfiguration(parser.parse_args())

  logger = Logger(config['zone'], 'main')
  logger.info(config)

  credentials = None
  if 'login' in config.keys():
    credentials = config

  imgProducer = ImageProducer(config['url'], credentials = credentials, frequency = config['frequency'], logger = Logger(config['zone'], 'ImageProducer'))
  uploader = None
  if not config['localStorageOnly']:
    from storageGCS import SurveilUploader
    uploader = SurveilUploader('surveil', config['zone'], Logger(config['zone'], 'SurveilUploader'))
  storageObserver = StorageObserver(zone = config['zone'], remoteUploader = uploader, logger = Logger(config['zone'], 'StorageObserver'))

  surveillance = Surveillance(imgProducer, storageObserver, config['minContourArea'], config['minDiffScore'], logger = Logger(config['zone'], 'Surveillance'))
  surveillance.execute()
# end if
