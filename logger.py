import logging
import psutil

class Logger:
  def __init__(self, name, display=None, zone=None):
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s: %(message)s', level=logging.INFO)
    self.display = display
    self.zone = zone
    self.logger = logging.getLogger(name)
  # end def

  def info(self, msg):
    if self.zone:
      msg = self.zone + ': ' + msg
    self.logger.info(msg)
    self.displayMsg('[INFO] ' + msg)
    #self.logMemory()

  def warn(self, msg):
    if self.zone:
      msg = self.zone + ': ' + msg
    self.logger.warning(msg)
    self.displayMsg('[WARN] ' + msg)
    #self.logMemory()

  def error(self, msg):
    if self.zone:
      msg = self.zone + ': ' + msg
    self.logger.error(msg)
    self.displayMsg('[ERR] ' + msg)
    #self.logMemory()

  def displayMsg(self, msg):
    if self.display:
      self.display.add_message(msg)

  def logMemory(self):
    vm = psutil.virtual_memory()
    self.logger.info(repr(vm))
# end class