from areaofinterest import AreaOfInterest


class AoiTracker:
  def __init__(self, name, window_size=10):
    self.name = name
    self.window_size = window_size
    self.minxs = []
    self.minys = []
    self.maxxs = []
    self.maxys = []
  # end def

  def isActive(self):
    if len(self.minxs) >= self.window_size:
      return any(x != None for x in self.minxs)

    return True
  # end def

  def addAoi(self, aoi):
    if aoi == None:
      self.minxs.append(None)
      self.minys.append(None)
      self.maxxs.append(None)
      self.maxys.append(None)
    else:
      self.minxs.append(aoi[0])
      self.minys.append(aoi[1])
      self.maxxs.append(aoi[2])
      self.maxys.append(aoi[3])

    if len(self.minxs) > self.window_size:
      self.minxs = self.minxs[1:]
      self.minys = self.minys[1:]
      self.maxxs = self.maxxs[1:]
      self.maxys = self.maxys[1:]
  # end def


  def generateAoi(self):
    minxs = list(filter(lambda x : x != None, self.minxs))
    minys = list(filter(lambda y : y != None, self.minys))
    maxxs = list(filter(lambda x : x != None, self.maxxs))
    maxys = list(filter(lambda y : y != None, self.maxys))

    minx = sum(minxs) / len(minxs)
    miny = sum(minys) / len(minys)
    maxx = sum(maxxs) / len(maxxs)
    maxy = sum(maxys) / len(maxys)

    return AreaOfInterest(self.name, (minx, miny, maxx, maxy))
# end class