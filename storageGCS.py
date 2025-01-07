import argparse
from google.cloud import storage
import os.path

class Storage:
  def __init__(self):
    self.client = storage.Client()
  #end def

  def upload(self, bucketName, uploadName, localFilePath):
    tgtBucket = self.client.get_bucket(bucketName)
    blob = storage.Blob(uploadName, tgtBucket)

    with open(localFilePath, 'rb') as uploadFile:
      blob.upload_from_file(uploadFile)
  #end def

  def download(self, bucketName, blobName, tgtFile):
    bucket = slef.get_bucket(bucketName)
    self.downloadFromABucket(bucket, blobName, tgtFile)
  #end def

  def downloadFromBucket(self, bucket, blobName, tgtFile):
    lbBlob = bucket.get_blob(blobName)
    if lbBlob:
      lbBlob.download_to_filename(tgtFile)
  #end def

  def getBuckets(self):
    return self.client.list_buckets()
  #end def

  def getFiles(self, bucketName):
    return self.client.get_bucket(bucketName).list_blobs()
  #end def
#end class

class SurveilUploader:
  def __init__(self, bucket, zone, logger):
    self.bucket = bucket
    self.zone = zone
    self.logger = logger
  #end def

  def upload(self, filePath):
    gcs = Storage()
    uploadPath = filePath.split(os.path.sep)[-1]
    uploadName = self.zone + '/' + uploadPath
    self.logger.info('Uploading %s to %s' % (filePath, uploadPath))
    gcs.upload(self.bucket, uploadName, filePath)
    self.logger.info('Uploaded %s' % uploadName)
  #end def

#end class

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Google Cloud Storage')
  parser.add_argument('-b', '--bucket',     required=True,       help='Bucket name')
  parser.add_argument('-u', '--upload-file',                     help='File to upload')
  parser.add_argument('-n', '--name',                            help='Name to give uploaded file')
  parser.add_argument('-l', '--list-files', action='store_true', help='List files in the specified bucket')
  parser.add_argument('--list-buckets',     action='store_true', help='List buckets')
  parser.add_argument('-d', '--download-file',                   help='Remote blob name of file to download')
  parser.add_argument('-t', '--target-file',                     help='Name of file to download to')
  args = parser.parse_args()

  store = Storage()
  if args.upload_file:
    store.upload(args.bucket, args.name, args.upload_file)

  if args.download_file:
    tgtFile = args.target_file
    if tgtFile == None:
      tgtFile = args.bucket + '-download.dat'
    store.download(args.bucket, args.args.download_file, tgtFile)
    print('downloaded from: %s to: %s' % (args.download_file, tgtFile))

  elif args.list_files:
    for f in store.getFiles(args.bucket):
      print('%s : %s' % (f.bucket.name, f.id))

  elif args.list_buckets:
    for b in store.getBuckets():
      print(b.name)
  #end if
#end if
