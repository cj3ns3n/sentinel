import curses
import queue
import psutil
import threading
import time
import traceback


class TerminalDisplay (threading.Thread):
  def __init__(self, detectors=[]):
    threading.Thread.__init__(self)
    self.scr = curses.initscr()
    self.size = self.scr.getmaxyx()
    self.message_start_line = 10
    self.message_last_line = self.size[0] - 4
    self.message_lines = self.message_last_line - self.message_start_line

    self.done = False
    self.infoQueue = queue.Queue(10)
    self.warnQueue = queue.Queue(10)
    self.errQueue = queue.Queue(10)
    self.detectorQueues = []

    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)
    if curses.has_colors():
      curses.start_color()

    self.messages = []
  # end def

  def add_message(self, message):
    if len(message) < self.size[1]:
      message = message + ' ' * (self.size[1] - len(message))
    else:
      message = message[:self.size[1]-1]

    self.messages.append(message)
    if len(self.messages) > self.message_lines:
      self.messages = self.messages[-self.message_lines:]
  # end def

  def run(self):
    while not self.done:
      try:
        self.processQueues()
        #stats = self.stats_container.get_stats()

        sys_mem = psutil.virtual_memory()
        avail_mem = sys_mem.available / (1000 * 1000)
        pct_mem_used = sys_mem.percent
        proc = psutil.Process()
        with proc.oneshot():
          uptime_hrs = (time.time() - proc.create_time()) / (60 * 60)
          cpu_percent = proc.cpu_percent()
          num_threads = proc.num_threads()
          mem_pct = proc.memory_percent()
          io = proc.io_counters()
          read_mb = io.read_bytes / (1000 * 1000)
          write_mb = io.write_bytes / (1000 * 1000)
          mem = proc.memory_info()
          mem_phys = mem.rss / (1000 * 1000)
          mem_vms = mem.vms / (1000 * 1000)
          open_files = len(proc.open_files())
          connections = len(proc.net_connections())

        sys_line1 = 'avail mem: %0.1f; used mem: %0.1f%%; Process: uptime %0.2f hrs; cpu used: %0.2f%%; mem used: %0.1f%%' % \
        (avail_mem, pct_mem_used, uptime_hrs, cpu_percent, mem_pct)
        sys_line2 = 'phys mem: %0.1f; virt mem: %0.1f; read mb: %0.1f; write mb: %0.1f; threads: %d; files: %d; connections: %d' % \
        (mem_phys, mem_vms, read_mb, write_mb, num_threads, open_files, connections)
        self.scr.addstr(0, 0, sys_line1)
        self.scr.addstr(1, 0, sys_line2)
        #self.scr.addstr(1, 0, "Screen size: %s" % repr(self.size))
        self.scr.addstr(2, 0, "info queue size: %d" % self.infoQueue.qsize())
        self.scr.addstr(3, 0, "warn queue size: %d" % self.warnQueue.qsize())
        self.scr.addstr(4, 0, "err queue size: %d" % self.errQueue.qsize())
        self.scr.addstr(5, 0, "msg queue size: %d" % len(self.messages))

        for msg_idx in range(len(self.messages)):
          self.scr.addstr(self.message_start_line + msg_idx, 0, self.messages[msg_idx])
      except Exception as e:
        traceback.print_exc()


      self.scr.refresh()
      time.sleep(0.01)
    # end while
  # end def

  def processQueues(self):
    for level, queue in [('INFO', self.infoQueue), ('WARN', self.warnQueue), ('ERROR', self.errQueue)]:
      msg = self.getItemOrNone(queue)
      if msg:
        self.add_message('%s: %s' % (level, msg))
  # end def

  def getItemOrNone(self, queueObj):
    try:
      msg = queueObj.get(block=False)
      queueObj.task_done()
      return msg
    except queue.Empty:
      return None
  # end def
  
  def shutdown(self):
    self.done = True
    curses.nocbreak()
    curses.echo()
    curses.curs_set(True)
    # self.scr.keypad(False)
    curses.endwin()
  # end def
# end class

if __name__ == "__main__":
  terminal = TerminalDisplay()
  terminal.start()

  for i in range(100):
    terminal.add_message(str(i))
    time.sleep(0.2)
  # end while

  terminal.shutdown()
  terminal.join()
# end if