import logging
import psutil

class Logger:
  def __init__(self, zone, name):
    self.zone = zone
    self.logger = logging.getLogger(name)
  # end def

  def info(self, msg):
    self.logger.info('%s: %s' % (self.zone, msg))
    self.logMemory()

  def warn(self, msg):
    self.logger.warning('%s: %s' % (self.zone, msg))
    self.logMemory()

  def error(self, msg):
    self.logger.error('%s: %s' % (self.zone, msg))
    self.logMemory()

  def logMemory(self):
    vm = psutil.virtual_memory()
    self.logger.info(repr(vm))
# end class