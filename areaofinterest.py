class AreaOfInterest:
  def __init__(self, name, area):
    self.name = name
    self.area = area

  def center(self):
    return ((self.area[0] + self.area[2]) / 2.0, (self.area[1] + self.area[3]) / 2.0)