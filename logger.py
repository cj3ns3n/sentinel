import logging
import psutil

class Logger:
  def __init__(self, name, zone=None):
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s: %(message)s', level=logging.INFO)
    self.zone = zone
    self.logger = logging.getLogger(name)
  # end def

  def info(self, msg):
    if self.zone:
      msg = self.zone + ': ' + msg
    self.logger.info(msg)
    self.logMemory()

  def warn(self, msg):
    if self.zone:
      msg = self.zone + ': ' + msg
    self.logger.warning(msg)
    self.logMemory()

  def error(self, msg):
    if self.zone:
      msg = self.zone + ': ' + msg
    self.logger.error(msg)
    self.logMemory()

  def logMemory(self):
    vm = psutil.virtual_memory()
    self.logger.info(repr(vm))
# end class