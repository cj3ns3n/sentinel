class AreaOfInterest:
  def __init__(self, name, area):
    self.name = name
    self.area = area
    self.annotation_lines = []  # annotate with lines list of lines ((x1, y1), (x2, y2))
    self.annotate_cross_hairs = []  # annotate with cross-hairs list of points ((x1, y1))
    self.annotation_text = []  # list of text messages to be added to the aoi

  def center(self):
    return ((self.area[0] + self.area[2]) / 2.0, (self.area[1] + self.area[3]) / 2.0)